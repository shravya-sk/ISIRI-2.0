

from ai_engine.intent_detector import detect_intent
from ai_engine.entity_extractor import extract_entities
from ai_engine.planner import plan
from ai_engine.plugin_executor import execute_plugin

while True:

    user = input("User: ")

    intent = detect_intent(user)
    print("Detected Intent:", intent)

    entities = extract_entities(user)

    action = plan(intent, entities)

    print("Planner Output:", action)

    response = execute_plugin(action)

    print("\nIntent :", intent)
    print("Entities :", entities)
    print("Planner :", action)
    print("Plugin Response :", response)
    print("-" * 50)