import ollama

class LocalLLM:
    def __init__(self, cfg):
        self.model = cfg.get("model", "llama3:8b-instruct-q4_0")
        self.temperature = cfg.get("temperature", 0.6)
        self.max_tokens = cfg.get("max_tokens", 512)

    def chat(self, system: str, history, tool_result=None) -> str:
        messages = []

        # Add system message
        if system:
            messages.append({"role": "system", "content": system})

        # Add chat history
        if history:
            messages.extend(history)

        # Add tool output if any
        if tool_result:
            messages.append({"role": "system", "content": f"Tool output:\n{tool_result}"})

        try:
            # Call Ollama client
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content'].strip()
        except Exception as e:
            return f"[LLM Error] {e}"
