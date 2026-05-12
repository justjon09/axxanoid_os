from pydantic import BaseModel

# Define exactly what the UI is allowed to send to the backend
class ChatRequest(BaseModel):
    conversation_id: int = 1
    sender: str
    message: str

# easily expand this later, for example:
# class ToggleRequest(BaseModel):
#     cron_active: bool