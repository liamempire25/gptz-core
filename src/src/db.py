import os, datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Chronicle(Base):
    __tablename__ = "chronicle"
    id = Column(Integer, primary_key=True)
    event_type = Column(String(150))
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ChronicleDB:
    def __init__(self):
        url = os.getenv("DATABASE_URL")
        if not url:
            raise Exception("DATABASE_URL not set")
        self.engine = create_engine(url, future=True)
        self.Session = sessionmaker(bind=self.engine)

    def connect(self):
        Base.metadata.create_all(self.engine)

    async def log_event(self, event_type, data):
        s = self.Session()
        rec = Chronicle(event_type=event_type, data=data)
        s.add(rec)
        s.commit()
        s.close()
        return rec.id
