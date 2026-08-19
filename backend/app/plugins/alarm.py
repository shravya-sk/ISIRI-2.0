from datetime import datetime
import dateparser
import winsound
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.start()


def ring_alarm(alarm_time):
    print("\n🔔🔔 ALARM RINGING 🔔🔔")
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