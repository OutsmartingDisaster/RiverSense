from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy import create_engine
from .session import SessionLocal

Base = declarative_base()

class GNSSData(Base):
    __tablename__ = 'gnss_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_data = Column(Text, nullable=False)
    rinex_file_path = Column(String)
    processing_status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<GNSSData(id={self.id}, status='{self.processing_status}')>"

# Example of how to create the database and table
if __name__ == '__main__':
    engine = create_engine('sqlite:///gnss_data.db')
    Base.metadata.create_all(engine)