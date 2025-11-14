from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Connect to PostgreSQL
engine = create_engine('postgresql://localhost/narrations')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Tables
class Narration(Base):
    __tablename__ = 'narrations'
    id = Column(Integer, primary_key=True)
    url = Column(String(500))
    text = Column(Text)
    status = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    image_captions = relationship("ImageCaption", cascade="all, delete-orphan")
    audio_chunks = relationship("AudioChunk", cascade="all, delete-orphan")

class ImageCaption(Base):
    __tablename__ = 'image_captions'
    id = Column(Integer, primary_key=True)
    narration_id = Column(Integer, ForeignKey('narrations.id'))
    image_url = Column(String(500))
    caption = Column(Text)

class AudioChunk(Base):
    __tablename__ = 'audio_chunks'
    id = Column(Integer, primary_key=True)
    narration_id = Column(Integer, ForeignKey('narrations.id'))
    chunk_number = Column(Integer)
    text = Column(Text)
    file_path = Column(String(255))

get_db = lambda: Session()

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✓ Database tables created!")

