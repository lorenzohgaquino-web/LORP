from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
from app.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False, unique=True)
    domain = Column(String)
    title = Column(String)
    html_hash = Column(String)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    status_code = Column(Integer)
    content_type = Column(String)

    entities = relationship("Entity", back_populates="source")

class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    normalized_name = Column(String)
    parent_entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    unit_name = Column(String)
    department_name = Column(String)
    program_name = Column(String)
    lab_name = Column(String)
    public_role = Column(String)
    official_contact = Column(String)
    official_contact_type = Column(String)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    source = relationship("Source", back_populates="entities")
    relevance = relationship("RelevanceScore", back_populates="entity", uselist=False)
    evidence = relationship("Evidence", back_populates="entity")

class RelevanceScore(Base):
    __tablename__ = "relevance_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    score_total = Column(Float)
    score_ai = Column(Float)
    score_automation = Column(Float)
    score_simulation = Column(Float)
    score_industry4 = Column(Float)
    score_software_eng = Column(Float)
    relevance_level = Column(String)
    explanation = Column(Text)
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)

    entity = relationship("Entity", back_populates="relevance")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    evidence_type = Column(String)
    snippet = Column(Text)
    source_url = Column(Text)
    publication_year = Column(Integer)
    confidence = Column(Float)

    entity = relationship("Entity", back_populates="evidence")
