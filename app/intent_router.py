
import re

def parse_intent(text: str):
    t = text.strip().lower()

    # type: <text>
    m = re.match(r"^type\s*:\s*(.+)$", t, flags=re.IGNORECASE)
    if m:
        return {"type": "type_text", "text": m.group(1)}

    # click x y
    m = re.match(r"^click\s+(\d+)\s+(\d+)$", t)
    if m:
        return {"type": "click", "x": int(m.group(1)), "y": int(m.group(2))}

    # move x y
    m = re.match(r"^move\s+(\d+)\s+(\d+)$", t)
    if m:
        return {"type": "move_mouse", "x": int(m.group(1)), "y": int(m.group(2))}

    # what's on my screen / read screen
    if "what's on my screen" in t or "whats on my screen" in t or "read screen" in t or "screen" in t and "read" in t:
        return {"type": "screen_read"}

    # fall back to chat
    return {"type": "chat"}
