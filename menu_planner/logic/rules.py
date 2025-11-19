def weekly_penalty(summary: dict, rules: dict) -> int:
    p = 0
    if summary.get("麺", 0) > rules.get("noodle_per_week_max", 7): p += 3
    if summary.get("汁物", 0) < rules.get("soup_per_week_min", 0): p += 2
    if summary.get("魚", 0) < rules.get("fish_per_week_min", 0):   p += 2
    if summary.get("揚げ物", 0) > rules.get("fried_per_week_max", 99): p += 3
    return p
