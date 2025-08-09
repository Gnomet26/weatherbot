from sqlalchemy import Column, BigInteger, String
from .db import Base

class User(Base):
    __tablename__ = "user_list"

    id = Column(BigInteger, primary_key=True, index=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, access_token={self.access_token}, refresh_token={self.refresh_token})>"
