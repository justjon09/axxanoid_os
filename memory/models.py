from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from memory.database import Base

class SystemConfig(Base):
    __tablename__ = "system_config"

    # Use single row (id=1) to hold global toggles
    id = Column(Integer, primary_key=True, index=True)
    cron_active = Column(Boolean, default=True)
    q_status = Column(String, default="idle") #idel thinking executing
    last_heartbeat = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class CurrentChat(Base):
    __tablename__ = "current_chat"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id")) #Links to Conversation
    sender = Column(String, index=True) # 'user' or 'q'
    message = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())

class ChatLogs(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id")) #links to Conversation
    chat_start = Column(DateTime, server_default=func.now())
    chat_end = Column(DateTime, nullable=True)
    context_summary = Column(Text)
    intent = Column(String) # Detected intent
    actions_taken = Column(Text) # Description of actions Q took
    sentiment = Column(String) # e.g., 'positive', 'neutral', 'negative'
    emotion = Column(String) # e.g., 'happy', 'sad', 'angry'
    argument = Column(Boolean, default=False)
    argument_resolved = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profile"

    #Make a table for Q to easlity store and access info about me 
    id = Column(Integer, primary_key=True, index=True)
    real_name = Column(String, index=True)
    user_names = Column(String, index=True)
    context = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class CronState(Base):
    __tablename__ = "cron_state"

    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String, unique=True, index=True)
    description = Column(String)
    last_run = Column(DateTime, nullable=True)
    last_result = Column(String, nullable=True)
    is_running = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    next_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
