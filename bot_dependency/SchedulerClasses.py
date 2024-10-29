from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from models import Base

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    message_type = Column(String, nullable=False)  # Text, photo, video, etc.
    content = Column(String)  # For text messages
    caption = Column(String)  # For media messages with captions
    date = Column(DateTime, nullable=False)
    
    # Relationships to other message types
    media = relationship("Media", back_populates="message", uselist=False)
    poll = relationship("Poll", back_populates="message", uselist=False)
    contact = relationship("Contact", back_populates="message", uselist=False)
    location = relationship("Location", back_populates="message", uselist=False)

class Media(Base):
    __tablename__ = 'media'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    file_id = Column(String, nullable=False)
    file_unique_id = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # photo, video, audio, document
    mime_type = Column(String)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Integer)
    
    # Relationship back to Message
    message = relationship("Message", back_populates="media")

class Poll(Base):
    __tablename__ = 'polls'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    poll_id = Column(String, nullable=False)
    question = Column(String, nullable=False)
    is_anonymous = Column(Boolean, nullable=False)
    allows_multiple_answers = Column(Boolean, default=False)
    is_quiz = Column(Boolean, default=False)
    correct_option_id = Column(Integer)
    
    # Relationship back to Message
    message = relationship("Message", back_populates="poll")

class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    phone_number = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    vcard = Column(String)  # Optional vCard info
    
    # Relationship back to Message
    message = relationship("Message", back_populates="contact")

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Relationship back to Message
    message = relationship("Message", back_populates="location")