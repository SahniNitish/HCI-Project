"""Mock emergentintegrations package for local development"""

class UserMessage:
    def __init__(self, text: str):
        self.text = text

class LlmChat:
    def __init__(self, **kwargs):
        self.model = kwargs.get('model', 'gpt-3.5-turbo')
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 100)

    async def run_astream(self, message):
        """Mock streaming response"""
        # Return a simple mock response for expense categorization
        if "Categorize this expense" in message.text:
            yield {"type": "text", "text": "Food"}
        elif "insights and recommendations" in message.text:
            yield {"type": "text", "text": "You're spending a lot on food. Consider meal prepping to save money."}
        else:
            yield {"type": "text", "text": "Mock response"}
