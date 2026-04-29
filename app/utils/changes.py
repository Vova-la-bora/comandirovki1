def calculate_changes(before: dict, after: dict):

    changes = {}

    keys = set(before.keys()) | set(after.keys())

    for key in keys:

        old = before.get(key)

        new = after.get(key)

        if old != new:

            changes[key] = {
                "old": old,
                "new": new
            }

    return changes