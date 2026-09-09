from backend.app.plugins.hardware import control_hardware

print("=== Unlock ===")
result = control_hardware({"state": "unlocked"})
print(result)

print("\n=== Lock ===")
result = control_hardware({"state": "locked"})
print(result)
