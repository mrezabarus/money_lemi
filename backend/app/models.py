from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)

    #parent-child relationship
    parent_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Relasi ke parent
    parent = relationship('User', remote_side=[id], backref='children')