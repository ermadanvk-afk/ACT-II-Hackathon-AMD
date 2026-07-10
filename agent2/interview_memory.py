from typing import List, Dict

class InterviewMemory:
    def __init__(self, system_prompt: str):
        # Initialize with the system prompt as the first message
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        # We can limit the history size to prevent context overflow
        self.max_messages = 20

    def add_user_message(self, text: str):
        self.history.append({"role": "user", "content": text})
        self._trim_history()

    def add_ai_message(self, text: str):
        self.history.append({"role": "assistant", "content": text})
        self._trim_history()

    def get_messages(self) -> List[Dict[str, str]]:
        return self.history

    def _trim_history(self):
        # Keep the system prompt (index 0) and the last (max_messages - 1) messages
        if len(self.history) > self.max_messages:
            self.history = [self.history[0]] + self.history[-(self.max_messages - 1):]

    def clear(self):
        # Reset back to just the system prompt
        self.history = [self.history[0]]
