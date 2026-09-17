# 🔌 ISIRI 2.0 — Hardware & GPIO Integration Guide

This directory contains the standalone **Raspberry Pi Servo Lock Service** that enables ISIRI 2.0 to lock/unlock a real-world door latch via spoken Tulu commands.

> **Note:** this replaces the earlier relay-based lights/fan design. The mechanism that was actually built is a 3D-printed **rack-and-pinion latch** driven by a single SG90 micro servo — not a relay board.

---

## 1. Hardware Architecture

```text
[Spoken Tulu Voice]
        │
        ▼
[ISIRI 2.0 Backend]
        │ (HTTP REST: POST http://<RPi_IP>:5000/device/lock/{locked|unlocked})
        ▼
[Raspberry Pi Servo Service (`rpi_gpio_service.py`)]
        │ (PWM signal, 0°–180° sweep)
        ▼
[SG90 Micro Servo]
        │ (pinion gear on servo horn)
        ▼
[3D-Printed Rack-and-Pinion Latch]
   └── Pinion rotates 0°↔180° → drives toothed rack bar in/out → 🔒 bolt extends/retracts
```

The servo's horn carries a small pinion gear that meshes with a toothed rack (the straight bar in the print). Rotating the servo through its full sweep drives the rack linearly — that linear motion is what extends or retracts the lock bolt. Because the throw is done by the rack rather than a direct arm, the servo needs its **full 0°–180° range**, not just a small flip.

---

## 2. GPIO Pinout & Wiring

| Component | BCM GPIO Pin | Physical Board Pin | Notes |
| :--- | :--- | :--- | :--- |
| **Lock Servo (signal)** | `GPIO 18` | Pin 12 | Hardware PWM-capable pin, ideal for servo control |
| **Servo VCC** | `5V` | Pin 2 or 4 | SG90 draws power from the 5V rail |
| **Servo GND** | `GND` | Pin 6, 9, 14, etc. | Common ground with the Pi |

Servo wire colors are typically: **orange/yellow** = signal → GPIO 18, **red** = VCC → 5V, **brown/black** = GND → GND.

---

## 3. Calibration

`LOCK_ANGLE` and `UNLOCK_ANGLE` in `rpi_gpio_service.py` are set to `180` and `0` respectively, but the actual "locked" direction depends on which way the pinion meshes with the rack on your specific print. After mounting:

1. Run the service and hit `/device/lock/locked`, then `/device/lock/unlocked`.
2. Watch which direction the rack moves.
3. If it's backwards, swap the two angle values in the script — no other code changes needed.

---

## 4. How to Run on Raspberry Pi

### Step 1: Copy `hardware/rpi_gpio_service.py` to Raspberry Pi
```bash
scp hardware/rpi_gpio_service.py pi@<raspberry_pi_ip>:~/
```

### Step 2: Start the Daemon on Raspberry Pi
```bash
python3 rpi_gpio_service.py --port 5000
```
*Output: `ISIRI 2.0 Lock Service listening on port 5000...`*

### Step 3: Connect ISIRI 2.0 Backend

Put the settings in **`backend/.env`** (copy `backend/.env.example`). The backend loads that file
at startup, so this works the same on Windows and Linux — no `export`/`set` in the right shell.

```ini
RPI_HOST=[fe80::ba27:ebff:fe12:3456%wlan0]:5000
HARDWARE_SIMULATION=false
```

`backend/.env` is git-ignored on purpose — see the zone-ID warning below.

---

## 4a. Connecting over IPv6 (read this if IPv4 doesn't work)

On many networks — college Wi-Fi especially, where client isolation blocks IPv4 peer-to-peer —
the Pi is reachable **only over IPv6**. If `ssh pi@<ipv4>` fails but `ssh pi@fe80::…%wlan0` works,
this is you.

The daemon binds `::` as a **dual-stack** socket, so one process answers IPv6 *and* IPv4 on port
5000. (The stdlib `HTTPServer` defaults to IPv4-only, which is why the backend previously could
never reach the Pi on an IPv6-only network — even though `ssh`, which listens on `::`, worked fine.)

### Find the address

On the Pi the daemon prints every usable address at startup, already formatted for `.env`:

```text
Set one of these as RPI_HOST in the ISIRI backend's .env file:
  RPI_HOST=[2409:40f2:300b:2651::42]:5000        (global IPv6 via wlan0)
  RPI_HOST=[fe80::ba27:ebff:fe12:3456%ZONE]:5000  (link-local IPv6 via wlan0)
  RPI_HOST=192.168.1.50:5000                      (IPv4 via wlan0)
```

Prefer a **global** IPv6 address (`2xxx:`/`fd`) if one is listed — it needs no zone ID and is the
same string on every machine.

### ⚠️ The zone ID is YOUR machine's interface, not the Pi's

A link-local address (`fe80::…`) is only meaningful together with the interface it is reached
*through*, written after a `%`. That interface belongs to **the computer running the backend**, so
the correct value is **different on every PC** — this is the single most common mistake.

| Where | How to find it | Looks like |
| :--- | :--- | :--- |
| Windows | `netsh interface ipv6 show interfaces` → the **Idx** column of your Wi-Fi adapter | `%12` |
| Linux / macOS | `ip -6 addr` / `ifconfig` → the device name | `%wlan0`, `%en0` |

Two spellings, and they are not interchangeable:

- **In `backend/.env`** — write it **raw**: `[fe80::ba27:ebff:fe12:3456%12]:5000`
- **In a URL** (curl, browser) — percent-encode it as `%25`: `http://[fe80::…%2512]:5000/status`

The `.env` value is handed to the OS resolver, which wants the raw `%`; a URL parser would read a
bare `%` as the start of an escape.

### Test it, in this order

Each step isolates one layer — stop at the first failure.

```bash
# 1. Is the Pi reachable at L2 at all? (no Python involved)
ping -6 fe80::ba27:ebff:fe12:3456%12          # Windows
ping6 fe80::ba27:ebff:fe12:3456%wlan0         # Linux

# 2. Is the daemon answering? (note -g and %25)
curl -g -6 "http://[fe80::ba27:ebff:fe12:3456%2512]:5000/status"

# 3. Can the backend parse and reach it? (the fastest way to see what's wrong)
curl http://127.0.0.1:8000/device/lock/diag

# 4. Drive the lock without speaking
curl -X POST http://127.0.0.1:8000/device/lock/unlocked
curl -X POST http://127.0.0.1:8000/device/lock/locked
```

`/device/lock/diag` reports the raw `RPI_HOST`, how it was parsed, what it resolved to (including
the IPv6 scope_id) and whether the Pi answered — so a typo in `.env` is immediately
distinguishable from a firewall problem.

### Troubleshooting

| Symptom | Cause |
| :--- | :--- |
| `gaierror` / "not known" | Bad zone ID syntax. On Windows it's the numeric `Idx`, not `wlan0`. |
| `...link-local address with no zone ID` | You wrote `fe80::…` with no `%zone`. Add it. |
| `TimeoutError` after ~2s | Wrong interface index, or a firewall on the Pi (`sudo ufw allow 5000`). |
| `ConnectionRefusedError` | You reached the Pi, but `rpi_gpio_service.py` isn't running. |
| Ping works, curl doesn't | Firewall on the Pi, or the daemon bound IPv4-only — check its startup log. |

### Keep it running across reboots

```ini
# /etc/systemd/system/isiri-lock.service
[Unit]
Description=ISIRI 2.0 Servo Lock Service
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/rpi_gpio_service.py --port 5000
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now isiri-lock
journalctl -u isiri-lock -f      # watch lock commands arrive
```

---

## 4b. SSH tunnel (use this when direct TCP to the Pi is blocked)

If `ping -6` reaches the Pi but `curl` to port 5000 times out, the network is
filtering TCP while allowing ICMP — Wi-Fi client isolation does exactly that. A
firewall rule on the Pi does the same. Rather than fight it, tunnel port 5000
over the SSH connection that already works:

```bash
# On the machine running the backend. Leave this window open.
ssh -N -L 5000:127.0.0.1:5000 pi@fe80::ba27:ebff:fe12:3456%12
```

Then in `backend/.env`:

```ini
RPI_HOST=127.0.0.1:5000
HARDWARE_SIMULATION=false
```

The backend now talks to its own loopback, SSH carries it to the Pi, and the
zone ID, the Pi's firewall and client isolation all stop mattering. The
`127.0.0.1:5000` in the `-L` argument is resolved **on the Pi**, so it reaches
the daemon's own listener.

Notes:
- If port 5000 is taken locally, use `-L 5001:127.0.0.1:5000` and set
  `RPI_HOST=127.0.0.1:5001`.
- The tunnel dies with the SSH session. If it keeps dropping, add
  `-o ServerAliveInterval=30 -o ExitOnForwardFailure=yes` — the latter makes SSH
  fail loudly instead of connecting without the forward.
- **Restart the backend after editing `.env`** — it is read at startup.

---

## 4c. Driving the lock without the backend

`tools/lock.py` talks to the Pi using only the standard library — no FastAPI, no
uvicorn, no Whisper, no torch. Use it to test the tunnel and the servo
independently of the web app:

```bash
python tools/lock.py status
python tools/lock.py unlock
python tools/lock.py lock
python tools/lock.py diag
```

It reads `backend/.env` like the backend does, and `--host` overrides it for a
one-off test:

```bash
python tools/lock.py unlock --host 127.0.0.1:5000
```

It exits 0 on success and 1 on failure, printing the resolved address, whether
the Pi confirmed the move, and a hint when it fails. **If this works but the
HTTP API does not, the problem is the backend process, not the lock.**

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/status` | Returns current lock state (`locked`/`unlocked`) and whether the physical servo or simulation mode is active |
| `POST` | `/device/lock/{state}` | `state` = `locked` or `unlocked` — drives the servo to the corresponding angle |

---

## 6. Supported Voice Commands in Tulu & English

| Voice Command (Tulu) | Voice Command (English) | Action Executed |
| :--- | :--- | :--- |
| `Bagilu lock malpule` | *"Lock the door"* | POST `/device/lock/locked` → servo drives rack to lock position |
| `Bagilu unlock malpule` | *"Unlock the door"* | POST `/device/lock/unlocked` → servo drives rack to unlock position |

> Tulu phrasing above is a placeholder based on the original doc's naming pattern — swap in your team's actual wording for "lock"/"unlock" if it differs.