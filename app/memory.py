
class Memory:
    def __init__(self, max_turns=12):
        self._history = []
        self.max_turns = max_turns

    def add_user(self, text):
        self._history.append({"role":"user","content":text})
        self._trim()

    def add_assistant(self, text):
        self._history.append({"role":"assistant","content":text})
        self._trim()

    def add_tool(self, text):
        self._history.append({"role":"tool","content":text})
        self._trim()

    def history(self):
        return list(self._history)

    def _trim(self):
        if len(self._history) > self.max_turns*2+2:
            self._history = self._history[-(self.max_turns*2+2):]
