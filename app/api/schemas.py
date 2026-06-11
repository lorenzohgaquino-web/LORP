from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class EvidenceOut(BaseModel):
    evidence_type: str
    snippet: str
    source_url: str
    confidence: float

    model_config = ConfigDict(from_attributes=True)

class RelevanceScoreOut(BaseModel):
    score_total: float
    relevance_level: str
    explanation: str

    model_config = ConfigDict(from_attributes=True)

class EntityOut(BaseModel):
    id: UUID
    entity_type: str
    name: str
    unit_name: Optional[str] = None
    department_name: Optional[str] = None
    program_name: Optional[str] = None
    public_role: Optional[str] = None
    official_contact: Optional[str] = None
    official_contact_type: Optional[str] = None
    relevance: Optional[RelevanceScoreOut] = None
    source_url: Optional[str] = None
    evidence: List[EvidenceOut] = []

    model_config = ConfigDict(from_attributes=True)

class CrawlRequest(BaseModel):
    seed_urls: List[str]
    max_depth: int = 2
    allowed_domains: Optional[List[str]] = None
