import audit_script

results = audit_script.analyze_file("GBX_brain_78A.json")
print("Valid JSON:", results["is_valid_json"])
print("Fatal errors:", results["fatal_error"])
print("Details:", results["details"])
print("Minor errors:", results["minor_errors_pct"])
