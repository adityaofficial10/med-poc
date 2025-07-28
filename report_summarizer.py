def summarize_report(patient_name: str, structured_data: list, risk_profile: dict, tone: str = "patient") -> str:
    lines = []

    if tone == "patient":
        lines.append(f"Hi {patient_name}, here's a summary of your lab test results:\n")
    elif tone == "doctor":
        lines.append(f"Summary for patient {patient_name}:\n")

    if tone == "patient":
        for area, level in risk_profile.items():
            if level == "High":
                lines.append(f"- There is a high risk related to your {area} health.")
            elif level == "Borderline":
                lines.append(f"- Your {area} results are slightly outside the normal range.")
            else:
                lines.append(f"- Your {area} health appears normal.")
    else:
        for area, level in risk_profile.items():
            lines.append(f"- {area.title()} risk: {level}")

    abnormal_tests = []
    for panel in structured_data:
        for test in panel["tests"]:
            try:
                val = float(test["value"])
                ref = test["ref_range"]
                if ref and ("-" in ref or ">" in ref or "<" in ref):
                    low, high = parse_range(ref)
                    if not (low <= val <= high):
                        abnormal_tests.append(f"{test['name']} = {test['value']} {test['unit']} (Ref: {ref})")
            except:
                continue

    if abnormal_tests:
        lines.append("\nNotable test values:")
        for line in abnormal_tests[:3]:
            lines.append(f"- {line}")
    else:
        lines.append("\nAll tested values appear to be within the normal range.")

    return "\n".join(lines)


def parse_range(range_str):
    if " - " in range_str:
        low, high = range_str.split(" - ")
        return float(low.strip()), float(high.strip())
    elif ">" in range_str:
        return float(range_str.strip(" >")), float("inf")
    elif "<" in range_str:
        return float("-inf"), float(range_str.strip(" <"))
    return 0.0, float("inf")
