from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    
    # Role dengan constraint
    role = Column(String(50), default='user', nullable=False)
    
    # Self-referencing untuk parent_id (hierarchy)
    parent_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Relationship untuk akses parent dan children
    parent = relationship(
        'User', 
        remote_side=[id],
        backref='children'
    )
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Add CHECK constraint untuk role
    __table_args__ = (
        CheckConstraint(role.in_(['admin','user']), name="check_role_valid"),
    )

    # def __repr__(self):
    #     return f"<User(id={self.id}, name='{self.name}', email='{self.email}', role={self.role}')>"
    
    def to_dict(self):
        """ Helper method convert ke dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active

        }