from datetime import datetime
import re
import time
import dateparser

# winsound is Windows-only. backend/app/main.py imports this module at startup,
# so an unguarded import takes the whole backend down on Linux/macOS.
try:
    import winsound
except ImportError:
    winsound = None
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()

UNAMBIGUOUS_MARKERS = re.compile(
    r"am|pm|a\.m|p\.m|o'?clock|:|noon|midnight|morning|evening|night|"
    r"second|minute|hour",
    re.IGNORECASE,
)

CORE_TIME_PATTERN = re.compile(
    r"\d{1,2}(:\d{2})?\s*"
    r"(am|pm|a\.m|p\.m|o'?clock|second[s]?|minute[s]?|hour[s]?)?"
    r"(\s*(today|tomorrow|tonight|morning|evening|noon|midnight))?",
    re.IGNORECASE,
)

BARE_DURATION_PATTERN = re.compile(
    r"^\s*\d{1,2}\s*(second[s]?|minute[s]?|hour[s]?)\s*\.?\s*$",
    re.IGNORECASE,
)


def ring_alarm(alarm_time):
    print("\n🔔🔔 ALARM RINGING 🔔🔔")
    print(f"Alarm time: {alarm_time}")

    for _ in range(10):
        if winsound is not None:
            winsound.Beep(1000, 500)
        else:
            # Terminal bell: the closest cross-platform equivalent.
            print("\a", end="", flush=True)
            time.sleep(0.5)


def is_ambiguous_bare_number(time_text: str) -> bool:
    stripped = time_text.strip().lower()
    has_digit = bool(re.search(r"\d", stripped))
    has_marker = bool(UNAMBIGUOUS_MARKERS.search(stripped))
    remainder = re.sub(r"\b(today|tomorrow|yelle|ini)\b", "", stripped).strip()
    is_just_a_number = bool(re.fullmatch(r"\d{1,2}", remainder))
    return has_digit and not has_marker and is_just_a_number


def extract_core_time_expression(time_text: str) -> str:
    match = CORE_TIME_PATTERN.search(time_text)
    if match and match.group(0).strip():
        return match.group(0).strip()
    return time_text


def normalize_bare_duration(time_text: str) -> str:
    stripped = time_text.strip()
    if BARE_DURATION_PATTERN.match(stripped):
        return f"in {stripped.rstrip('.')}"
    return time_text


def set_alarm(time_text):
    try:
        if is_ambiguous_bare_number(time_text):
            return {
                "success": False,
                "reply": f"Did you mean {time_text.strip()} AM or {time_text.strip()} PM?"
            }

        core_time_text = extract_core_time_expression(time_text)
        core_time_text = normalize_bare_duration(core_time_text)

        alarm_time = dateparser.parse(
            core_time_text,
            settings={
                "PREFER_DATES_FROM": "future"
            }
        )

        if not alarm_time and core_time_text != time_text:
            alarm_time = dateparser.parse(
                normalize_bare_duration(time_text),
                settings={"PREFER_DATES_FROM": "future"}
            )

        if not alarm_time:
            return {
                "success": False,
                "reply": "I couldn't understand the alarm time."
            }

        if alarm_time <= datetime.now():
            return {
                "success": False,
                "reply": "That time has already passed."
            }

        scheduler.add_job(
            ring_alarm,
            "date",
            run_date=alarm_time,
            args=[alarm_time],
            misfire_grace_time=30,
            coalesce=True
        )

        formatted_time = alarm_time.strftime("%I:%M %p")
        formatted_date = alarm_time.strftime("%d %B %Y")

        return {
            "success": True,
            "reply": f"Alarm set for {formatted_time} on {formatted_date}.",
            "alarm_time": alarm_time.isoformat()
        }

    except Exception as e:
        print("Alarm error:", e)

        return {
            "success": False,
            "reply": "Sorry, I couldn't set the alarm."
        }


def execute(entities):
    time_text = entities.get("alarm_time_text")

    if not time_text:
        time_text = entities.get("time", "")

    if not time_text:
        return {
            "success": False,
            "reply": "What time should I set the alarm for?"
        }

    return set_alarm(time_text)


def get_scheduled_alarms():
    jobs = scheduler.get_jobs()
    return [
        {
            "id": job.id,
            "scheduled_for": job.next_run_time.strftime("%I:%M %p on %d %B %Y")
            if job.next_run_time else None,
        }
        for job in jobs
    ]