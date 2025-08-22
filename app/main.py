
import time
import queue
import threading
import sys
import yaml

from app.intent_router import parse_intent
from app.tools import Toolbelt
from app.memory import Memory
from core.llm import LocalLLM
from inputs.audio_in import SpeechRecognizer
from inputs.tts_out import TTS

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def voice_loop(llm, tools, stt, tts, memory, cfg):
    tts.say("Voice mode ready. Say something.")
    for transcript in stt.listen_stream():
        text = transcript.strip()
        if not text:
            continue
        print(f"\n[You]: {text}")
        handle_user_turn(text, llm, tools, tts, memory, cfg)

def handle_user_turn(user_text, llm, tools, tts, memory, cfg):
    # 1) Route intent
    intent = parse_intent(user_text)
    print(f"[Intent]: {intent}")

    # 2) Tool calls (screen read etc.), with confirmation if needed
    tool_result = None
    if intent["type"] == "screen_read":
        tool_result = tools.read_screen_text()
    elif intent["type"] == "type_text":
        to_type = intent.get("text", "")
        if cfg["controls"].get("confirm_actions", True):
            print(f"[Confirm] Type this? -> {to_type!r}  (y/n)")
            ans = input("> ").strip().lower()
            if ans != "y":
                print("[Action] Cancelled.")
                tool_result = "User cancelled typing."
            else:
                tools.type_text(to_type)
                tool_result = f"Typed: {to_type}"
        else:
            tools.type_text(to_type)
            tool_result = f"Typed: {to_type}"
    elif intent["type"] == "click":
        x, y = intent.get("x"), intent.get("y")
        if x is None or y is None:
            print("[Info] No coords provided; clicking current mouse position.")
            tools.click()
            tool_result = "Clicked at current position."
        else:
            tools.click(x, y)
            tool_result = f"Clicked at ({x}, {y})"
    elif intent["type"] == "move_mouse":
        x, y = intent.get("x"), intent.get("y")
        tools.move_mouse(x, y)
        tool_result = f"Moved mouse to ({x}, {y})"
    else:
        tool_result = None

    # 3) Build LLM context
    system = (
        "You are a helpful **local** assistant. "
        "If the user asks to perform an action, consider available tools: "
        "screen_read (OCR), type_text, click(x,y), move_mouse(x,y). "
        "Ask before risky actions."
    )
    memory.add_user(user_text)
    if tool_result:
        memory.add_tool(tool_result)

    # 4) Get LLM reply
    reply = llm.chat(system=system, history=memory.history(), tool_result=tool_result)
    print(f"[Assistant]: {reply}")
    tts.say(reply)
    memory.add_assistant(reply)

def main():
    cfg = load_config()

    # Initialize subsystems
    llm = LocalLLM(cfg["llm"])
    tools = Toolbelt(cfg)
    tts = TTS(cfg["tts"])
    memory = Memory(max_turns=12)

    # Choose voice or console mode
    if cfg["app"].get("use_voice_loop", False):
        stt = SpeechRecognizer(cfg["audio"])
        try:
            voice_loop(llm, tools, stt, tts, memory, cfg)
        except KeyboardInterrupt:
            print("\nExiting voice loop.")
    else:
        print("Console mode. Type your message. Try commands like:")
        print("- what's on my screen?")
        print("- type: Hello Professor")
        print("- click 500 400")
        print("- move 1000 500")
        print("Press Ctrl+C to exit.\n")

        try:
            while True:
                user_text = input("You> ").strip()
                if not user_text:
                    continue
                handle_user_turn(user_text, llm, tools, tts, memory, cfg)
        except KeyboardInterrupt:
            print("\nGoodbye.")

if __name__ == "__main__":
    main()
