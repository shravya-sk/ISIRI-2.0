"""
ISIRI 2.0 — Full Pipeline Test (text -> translation -> intent -> plan -> hardware)

Simulates what happens after Whisper transcribes speech: takes raw text
(as if just transcribed) and runs it through the whole decision chain,
ending in an actual (simulated) hardware action.

Usage:
    python test_full_pipeline.py
"""

from ai_engine.translator import translate_to_english
from ai_engine.intent_detector import detect_intent
from ai_engine.entity_extractor import extract_entities
from ai_engine.planner import plan
from backend.app.plugins.hardware import control_hardware


PLUGIN_MAP = {
    "hardware": control_hardware,
    "device_control": control_hardware,
}


def run_pipeline(raw_text: str):
    print(f"\n{'='*60}")
    print(f"RAW INPUT (as if just transcribed by Whisper): {raw_text!r}")
    print(f"{'='*60}")

    # 1. Translate (Tulu -> English, or pass-through if already English)
    english_text = translate_to_english(raw_text)
    print(f"1. Translated to English : {english_text!r}")

    # 2. Detect intent
    intent_result = detect_intent(english_text)
    print(f"2. Detected intent       : {intent_result}")

    # 3. Extract entities
    entities = extract_entities(english_text)
    print(f"3. Extracted entities    : {entities}")

    # 4. Plan (route to the right plugin)
    # planner.py expects a plain string intent, not the full detect_intent() dict
    plan_result = plan(intent_result.get("intent"), entities)
    print(f"4. Plan                  : {plan_result}")

    # 5. Execute via the right plugin
    plugin_name = plan_result.get("plugin")
    plugin_fn = PLUGIN_MAP.get(plugin_name)

    if plugin_fn is None:
        print(f"5. EXECUTION SKIPPED — no plugin wired up for '{plugin_name}' in this test script.")
        return

    result = plugin_fn(plan_result.get("entities", entities))
    print(f"5. Execution result      : {result}")


if __name__ == "__main__":
    test_commands = [
        "Baakil lock malpule",       # Tulu: lock the door
        "Baakil unlock malpule",     # Tulu: unlock the door
        "Lock the door",             # English direct
        "Unlock the door",           # English direct
    ]

    for cmd in test_commands:
        run_pipeline(cmd)