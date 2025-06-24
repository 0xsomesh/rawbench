import os


class Credential:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    def get_api_key(self):
        return self.api_key