import os
import sys
import importlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def execute_plugin(plan):
    plugin_name = plan.get("plugin")
    data = plan.get("entities", {})

    if not plugin_name:
        return {
            "success": False,
            "reply": plan.get("message", "No plugin selected.")
        }

    try:
        module = importlib.import_module(f"app.plugins.{plugin_name}")
        return module.execute(data)

    except Exception as e:
        return {
            "success": False,
            "reply": str(e)
        }