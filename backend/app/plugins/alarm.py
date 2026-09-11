from datetime import datetime
import dateparser
import winsound
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()


def ring_alarm(alarm_time):
    print("\nALARM RINGING")
    print(f"Alarm time: {alarm_time}")

    for _ in range(10):
        winsound.Beep(1000, 500)


def set_alarm(time_text):
    try:
        alarm_time = dateparser.parse(
            time_text,
            settings={
                "PREFER_DATES_FROM": "future"
            }
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
