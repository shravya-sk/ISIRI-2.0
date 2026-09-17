"""
ISIRI 2.0 -- door lock round-trip test.

Starts a real rpi_gpio_service.py daemon on this machine (it falls back to
SIMULATION mode when gpiozero is absent, so no Pi is needed), then drives it
through the hardware plugin exactly the way the voice pipeline does.

Run:  python test_hardware_lock.py

Covers the cases that actually broke in the field:
  * IPv6 link-local with a zone ID  (the Pi's real transport)
  * IPv4 to the same dual-stack listener
  * the Pi being unreachable -> must report failure, not a cheerful lie
  * a link-local address with the zone ID forgotten
"""

import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

DAEMON = os.path.join("hardware", "rpi_gpio_service.py")


def free_port() -> int:
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
        s.bind(("::", 0))
        return s.getsockname()[1]


def link_local() -> str:
    """This machine's own link-local address as 'addr%zone', or '' if none.

    Used to exercise the exact zone-ID code path the Raspberry Pi needs,
    without needing a Raspberry Pi.
    """
    try:
        out = subprocess.run(
            ["ip", "-o", "-6", "addr", "show", "scope", "link"],
            capture_output=True, text=True, timeout=3,
        ).stdout
    except Exception:
        return ""
    for line in out.splitlines():
        fields = line.split()
        for i, token in enumerate(fields):
            if token == "inet6" and i + 1 < len(fields):
                return "%s%%%s" % (fields[i + 1].split("/")[0], fields[1])
    return ""


def wait_until_up(port: int, timeout: float = 10.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("::1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def main() -> int:
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, DAEMON, "--port", str(port)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        if not wait_until_up(port):
            print("FAIL: daemon did not start on port %s" % port)
            return 1
        print("daemon up on port %s\n" % port)

        os.environ["HARDWARE_SIMULATION"] = "false"
        os.environ["RPI_TIMEOUT"] = "2.0"
        from app.plugins import hardware

        failures = []

        def check(label, condition):
            print("  %s  %s" % ("ok  " if condition else "FAIL", label))
            if not condition:
                failures.append(label)

        def call(rpi_host, state):
            os.environ["RPI_HOST"] = rpi_host
            return hardware.control_hardware({"state": state})

        ll = link_local()
        if ll:
            print("IPv6 link-local with zone ID (%s)" % ll)
            host = "[%s]:%d" % (ll, port)
            r = call(host, "unlocked")
            check("unlock reaches the daemon", r["success"] and r["rpi_connected"])
            check("state is 'unlocked'", r["state"] == "unlocked")
            r = call(host, "locked")
            check("lock reaches the daemon", r["success"] and r["state"] == "locked")
        else:
            print("IPv6 link-local: SKIPPED (no link-local address on this host)")

        print("\nIPv4 to the same dual-stack listener")
        r = call("127.0.0.1:%d" % port, "unlocked")
        check("IPv4 still works", r["success"] and r["rpi_connected"])

        print("\nIPv6 loopback")
        r = call("[::1]:%d" % port, "locked")
        check("IPv6 loopback works", r["success"] and r["rpi_connected"])

        print("\nPi unreachable (must fail honestly, not claim success)")
        r = call("192.0.2.1:%d" % port, "locked")     # TEST-NET-1, always black-holed
        check("success is False", r["success"] is False)
        check("rpi_connected is False", r["rpi_connected"] is False)
        check("reply does not claim the door moved", "now locked" not in r["reply"])

        print("\nLink-local with the zone ID forgotten")
        r = call("fe80::1", "locked")
        check("fails with an actionable message", "zone ID" in r.get("error", ""))

        print("\nSimulation mode is opt-in")
        os.environ["HARDWARE_SIMULATION"] = "true"
        r = call("127.0.0.1:%d" % port, "unlocked")
        check("flagged as simulated", r.get("simulated") is True and not r["rpi_connected"])
        os.environ["HARDWARE_SIMULATION"] = "false"

        print("\n%s" % ("ALL CHECKS PASSED" if not failures
                        else "%d FAILURE(S): %s" % (len(failures), ", ".join(failures))))
        return 1 if failures else 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
