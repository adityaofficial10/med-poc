import re

def extract_structured_tests(text: str) -> list:
    pattern = r"(?P<name>[A-Za-z \(\)\-]+)[^\d]*(?P<value>\d+\.?\d*)\s*(?P<unit>[a-zA-Z\/\%\^\d]+)"
    results = []
    for match in re.finditer(pattern, text):
        results.append({
            "test_name": match.group("name").strip(),
            "value": float(match.group("value")),
            "unit": match.group("unit")
        })
    return results
