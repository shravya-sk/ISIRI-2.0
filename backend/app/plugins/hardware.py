"""
ISIRI 2.0 -- Hardware Plugin (Door Lock)

Controls the servo-driven miniature door lock via HTTP calls to the
Raspberry Pi service (hardware/rpi_gpio_service.py).

Supported Commands:
- "Lock the door" / "Baakil lock malpule"
- "Unlock the door" / "Baakil unlock malpule"

Networking
----------
The Pi is often reachable only over IPv6 -- including *link-local* addresses
that carry a zone ID, e.g. ``fe80::ba27:ebff:fe12:3456%wlan0``. Two rules make
that work, and both are easy to get wrong:

1. ``getaddrinfo`` (and therefore http.client) wants the zone RAW: ``%wlan0``.
   A URL carries it percent-encoded as ``%25wlan0``. We decode on the way in.
2. The zone names the interface of *this* machine, not the Pi's. It differs on
   every PC -- ``%wlan0`` on Linux, a numeric index like ``%12`` on Windows
   (``netsh interface ipv6 show interfaces``). So it belongs in a per-machine
   .env file and must never be committed.

We use http.client rather than `requests` on purpose: `requests`/urllib3 cannot
carry a zone ID, and the stdlib has no extra dependency to install.
"""

import http.client
import json
import logging
import os
import socket
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)

DEFAULT_PORT = 5000
DEFAULT_TIMEOUT = 2.0

LOCK_STATE = "locked"   # last state the Pi confirmed (or the simulated one)

TULU_RESPONSES = {
    "locked": "Baakil lock aathund.",
    "unlocked": "Baakil unlock aathund.",
}


# --------------------------------------------------------------------------
# Configuration (read lazily, so editing .env + restarting is enough)
# --------------------------------------------------------------------------

def _simulation_mode() -> bool:
    """Real hardware is the default; simulation is opt-in.

    The old default was 'true', which is why the HTTP call never fired.
    """
    return os.environ.get("HARDWARE_SIMULATION", "false").strip().lower() == "true"


def _timeout() -> float:
    try:
        return float(os.environ.get("RPI_TIMEOUT", DEFAULT_TIMEOUT))
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT


def parse_rpi_host(raw: str, default_port: int = DEFAULT_PORT) -> Tuple[str, int]:
    """Parse RPI_HOST into a (host, port) pair.

    Accepts every form somebody might reasonably paste::

        192.168.1.50                         -> ('192.168.1.50', 5000)
        192.168.1.50:5000                    -> ('192.168.1.50', 5000)
        raspberrypi.local                    -> ('raspberrypi.local', 5000)
        fe80::1%wlan0                        -> ('fe80::1%wlan0', 5000)
        [fe80::1%wlan0]:5000                 -> ('fe80::1%wlan0', 5000)
        http://[fe80::1%25wlan0]:5000/       -> ('fe80::1%wlan0', 5000)

    The returned host keeps its RAW ``%zone`` suffix (that is what getaddrinfo
    wants), is unbracketed, and preserves case -- interface names on Linux are
    case-sensitive, which is why urlsplit().hostname must not be used here: it
    lowercases the whole authority.

    Raises ValueError with an actionable message on malformed input.
    """
    s = (raw or "").strip()
    if not s:
        return ("127.0.0.1", default_port)

    if "://" in s:
        scheme, _, s = s.partition("://")
        if scheme.lower() != "http":
            raise ValueError(
                "RPI_HOST: only http:// is supported, got %r" % scheme
            )

    # Drop any path/query/fragment.
    for sep in ("/", "?", "#"):
        s = s.split(sep, 1)[0]

    # A URL spells the zone '%25wlan0'; the socket layer needs '%wlan0'.
    s = s.replace("%25", "%")

    if not s:
        raise ValueError("RPI_HOST: no host found in %r" % raw)

    if s.startswith("["):                      # [ipv6] or [ipv6]:port
        host, sep, rest = s[1:].partition("]")
        if not sep:
            raise ValueError("RPI_HOST: unbalanced '[' in %r" % raw)
        if rest.startswith(":") and rest[1:]:
            return (host, _port(rest[1:], raw))
        return (host, default_port)

    if s.count(":") >= 2:                      # bare IPv6 literal, no port
        return (s, default_port)

    host, sep, port = s.rpartition(":")
    if sep:
        return (host, _port(port, raw) if port else default_port)
    return (s, default_port)


def _port(text: str, raw: str) -> int:
    try:
        return int(text)
    except ValueError:
        raise ValueError("RPI_HOST: %r is not a valid port (in %r)" % (text, raw))


def _check_zone(host: str) -> None:
    """A link-local address without a zone resolves, then fails at connect()
    with an unhelpful errno. Catch it here and say what to actually do."""
    if host.lower().startswith("fe80:") and "%" not in host:
        raise ValueError(
            "RPI_HOST '%s' is an IPv6 link-local address with no zone ID. "
            "Append the interface of THIS machine: '%%wlan0' on Linux/macOS, "
            "or '%%<Idx>' on Windows (get Idx from: "
            "netsh interface ipv6 show interfaces)." % host
        )


def build_host_header(host: str, port: int) -> str:
    """RFC 6874: the zone ID must NOT appear in the Host header.

    Newer CPython strips it automatically, but 3.9 (which the Pi may run) does
    not, so we always send the header ourselves -- http.client skips its own
    when we supply one.
    """
    bare = host.split("%", 1)[0]
    if ":" in bare:
        bare = "[%s]" % bare
    return "%s:%d" % (bare, port)


# --------------------------------------------------------------------------
# Transport
# --------------------------------------------------------------------------

def _request(method: str, path: str, timeout: float = None) -> Tuple[int, Dict[str, Any]]:
    """One stdlib HTTP round-trip to the Pi. Returns (status, parsed_json).

    Raises OSError / http.client.HTTPException / ValueError -- callers decide
    how to report. Nothing is swallowed here.

    Note the port is passed separately: HTTPConnection('fe80::1%wlan0') would
    raise InvalidURL, because it reads the text after the last ':' as a port.
    Given an explicit port it hands the zone'd host straight to getaddrinfo,
    which understands it natively.
    """
    raw = os.environ.get("RPI_HOST", "")
    host, port = parse_rpi_host(raw)
    _check_zone(host)

    if timeout is None:
        timeout = _timeout()

    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request(method, path, headers={
            "Host": build_host_header(host, port),
            "Accept": "application/json",
            "Connection": "close",
        })
        response = conn.getresponse()
        body = response.read()
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except ValueError:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        return response.status, payload
    finally:
        conn.close()


def _request_with_retry(method: str, path: str) -> Tuple[int, Dict[str, Any]]:
    """Retries once on a transient transport error.

    Deliberately does NOT retry a timeout: a host that is simply not there
    times out again identically, and the retry only doubles how long the user
    waits before hearing that the door did not move. A refused/reset
    connection, by contrast, is often worth a second attempt.
    """
    try:
        return _request(method, path)
    except (socket.timeout, TimeoutError):
        raise
    except OSError as first:
        logger.debug("RPi request %s %s failed (%s); retrying once.", method, path, first)
        return _request(method, path)


def get_status() -> Dict[str, Any]:
    """GET /status on the Pi. Used by the backend's diagnostic route."""
    if _simulation_mode():
        return {
            "success": True,
            "simulated": True,
            "state": LOCK_STATE,
            "rpi_connected": False,
        }
    try:
        status, payload = _request_with_retry("GET", "/status")
    except Exception as error:
        return {
            "success": False,
            "rpi_connected": False,
            "error": "%s: %s" % (type(error).__name__, error),
            "rpi_host": os.environ.get("RPI_HOST", ""),
        }

    return {
        "success": status == 200,
        "rpi_connected": status == 200,
        "http_status": status,
        "state": payload.get("state", LOCK_STATE),
        "servo_mode": payload.get("servo_mode"),
        "rpi_host": os.environ.get("RPI_HOST", ""),
    }


def diagnostics() -> Dict[str, Any]:
    """Everything needed to tell a config typo from a firewall problem.

    This is the first thing to run when the lock 'doesn't work' on a new PC.
    """
    raw = os.environ.get("RPI_HOST", "")
    report: Dict[str, Any] = {
        "rpi_host_raw": raw,
        "simulation_mode": _simulation_mode(),
        "timeout": _timeout(),
    }

    try:
        host, port = parse_rpi_host(raw)
        report["parsed_host"] = host
        report["parsed_port"] = port
        report["host_header"] = build_host_header(host, port)
        _check_zone(host)
    except ValueError as error:
        report["error"] = str(error)
        report["hint"] = "Fix RPI_HOST in backend/.env"
        return report

    try:
        candidates = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        report["resolved"] = [
            {"family": c[0].name, "sockaddr": list(c[4])} for c in candidates
        ]
    except OSError as error:
        report["error"] = "getaddrinfo failed: %s" % error
        report["hint"] = (
            "The address or its zone ID is wrong. On Windows the zone is the "
            "numeric Idx from 'netsh interface ipv6 show interfaces'."
        )
        return report

    try:
        status, payload = _request("GET", "/status")
        report["reachable"] = True
        report["http_status"] = status
        report["pi_response"] = payload
    except Exception as error:
        report["reachable"] = False
        report["error"] = "%s: %s" % (type(error).__name__, error)
        report["hint"] = _triage(error)

    return report


def _triage(error: Exception) -> str:
    if isinstance(error, ValueError):
        return "RPI_HOST in backend/.env is malformed: %s" % error
    if isinstance(error, socket.gaierror):
        return "Bad address or zone ID syntax in RPI_HOST."
    if isinstance(error, (socket.timeout, TimeoutError)):
        return ("Reached the network but got no answer: firewall on the Pi, "
                "or the wrong interface index in the zone ID.")
    if isinstance(error, ConnectionRefusedError):
        return ("The Pi answered but nothing is listening on that port -- "
                "start rpi_gpio_service.py on the Pi.")
    return "Check that rpi_gpio_service.py is running and the Pi is reachable."


# --------------------------------------------------------------------------
# Plugin entry point
# --------------------------------------------------------------------------

def _normalize(entities: Dict[str, Any]) -> str:
    raw_action = str(entities.get("state", entities.get("action", "locked"))).lower().strip()
    if raw_action in {"unlock", "unlocked", "open", "opened"}:
        return "unlocked"
    return "locked"


def control_hardware(entities: Dict[str, Any]) -> Dict[str, Any]:
    global LOCK_STATE

    action = _normalize(entities)
    logger.info("Hardware action: lock -> %s", action)

    if _simulation_mode():
        LOCK_STATE = action
        return {
            "success": True,
            "reply": "The door is now %s. (%s) [simulated - no Raspberry Pi]" % (
                action, TULU_RESPONSES.get(action, "Baakil %s." % action)),
            "device": "lock",
            "state": action,
            "rpi_connected": False,
            "simulated": True,
        }

    try:
        status, payload = _request_with_retry("POST", "/device/lock/%s" % action)
    except Exception as error:
        # The Pi is the source of truth, so do NOT move LOCK_STATE on failure.
        detail = "%s: %s" % (type(error).__name__, error)
        logger.error("Could not reach the Raspberry Pi lock service: %s", detail)
        return {
            "success": False,
            "reply": "I couldn't reach the door lock. The Raspberry Pi did not respond.",
            "device": "lock",
            "state": LOCK_STATE,
            "rpi_connected": False,
            "error": detail,
            "hint": _triage(error),
        }

    if status != 200:
        logger.error("Raspberry Pi refused the lock command (HTTP %s): %s", status, payload)
        return {
            "success": False,
            "reply": "The door lock rejected that command.",
            "device": "lock",
            "state": LOCK_STATE,
            "rpi_connected": True,
            "error": "HTTP %s: %s" % (status, payload),
        }

    # Trust the Pi's own reported state over what we asked for.
    LOCK_STATE = payload.get("state", action)

    return {
        "success": True,
        "reply": "The door is now %s. (%s)" % (
            LOCK_STATE, TULU_RESPONSES.get(LOCK_STATE, "Baakil %s." % LOCK_STATE)),
        "device": "lock",
        "state": LOCK_STATE,
        "rpi_connected": True,
    }


def execute(data: Dict[str, Any]) -> Dict[str, Any]:
    """Plugin contract. Must never raise: ai_engine/plugin_executor.py turns any
    escaping exception into a spoken raw Python error string."""
    try:
        return control_hardware(data)
    except Exception as error:               # pragma: no cover - safety net
        logger.exception("hardware plugin failed")
        return {
            "success": False,
            "reply": "The door lock is not configured correctly.",
            "device": "lock",
            "error": "%s: %s" % (type(error).__name__, error),
        }
