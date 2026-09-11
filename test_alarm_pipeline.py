from ai_engine.translator import translate_to_english
from ai_engine.intent_detector import detect_intent
from ai_engine.entity_extractor import extract_entities
from ai_engine.planner import plan
from backend.app.plugins.alarm import execute as alarm_execute, scheduler


def run_pipeline(raw_text: str):
    print(f"\n{'='*60}")
    print(f"RAW INPUT: {raw_text!r}")
    print(f"{'='*60}")

    english_text = translate_to_english(raw_text)
    print(f"1. Translated to English : {english_text!r}")

    intent_result = detect_intent(english_text)
    print(f"2. Detected intent       : {intent_result}")

    entities = extract_entities(english_text)
    print(f"3. Extracted entities    : {entities}")

    plan_result = plan(intent_result.get("intent"), entities)
    print(f"4. Plan                  : {plan_result}")

    if plan_result.get("plugin") != "alarm":
        print("5. EXECUTION SKIPPED - did not route to the alarm plugin.")
        return

    result = alarm_execute(plan_result.get("entities", entities))
    print(f"5. Execution result      : {result}")


if __name__ == "__main__":
    test_commands = [
        "Set an alarm for 6am tomorrow",
        "Set an alarm for 6am tomorrow because I have a train to catch.",
        "Wake me up in 15 seconds",
        "Remind me at 9pm to take medicine",
    ]

    for cmd in test_commands:
        run_pipeline(cmd)

    print(f"\n{'='*60}")
    print("Currently scheduled jobs in this process:")
    print(f"{'='*60}")
    for job in scheduler.get_jobs():
        print(f"  - {job.id}: next run at {job.next_run_time}")
