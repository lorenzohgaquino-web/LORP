from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import SessionLocal
from app.models.models import Entity, Source, RelevanceScore
from app.api.schemas import EntityOut, CrawlRequest
from app.services.crawler import run_crawl_job
from app.services.classifier import Classifier
import io
import csv
from fastapi.responses import StreamingResponse
import uuid
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/entities", response_model=List[EntityOut])
def get_entities(
    entity_type: Optional[str] = None,
    unit: Optional[str] = None,
    relevance: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Entity)
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    if unit:
        query = query.filter(Entity.unit_name.ilike(f"%{unit}%"))

    entities = query.all()

    if relevance:
        entities = [e for e in entities if e.relevance and e.relevance.relevance_level.lower() == relevance.lower()]

    results = []
    for e in entities:
        eo = EntityOut.model_validate(e)
        if e.source:
            eo.source_url = e.source.url
        results.append(eo)
    return results

@router.get("/entities/{id}", response_model=EntityOut)
def get_entity(id: str, db: Session = Depends(get_db)):
    try:
        entity_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    entity = db.query(Entity).filter(Entity.id == entity_uuid).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    eo = EntityOut.model_validate(entity)
    if entity.source:
        eo.source_url = entity.source.url
    return eo

@router.get("/search", response_model=List[EntityOut])
def search_entities(q: str, db: Session = Depends(get_db)):
    entities = db.query(Entity).filter(
        (Entity.name.ilike(f"%{q}%")) | (Entity.unit_name.ilike(f"%{q}%"))
    ).all()

    results = []
    for e in entities:
        eo = EntityOut.model_validate(e)
        if e.source:
            eo.source_url = e.source.url
        results.append(eo)
    return results

@router.post("/crawl")
def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_crawl_job, request.seed_urls, request.max_depth)
    return {"message": "Crawl job started in background"}

@router.post("/classify/{entity_id}")
def classify_entity(entity_id: str, db: Session = Depends(get_db)):
    try:
        entity_uuid = uuid.UUID(entity_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    entity = db.query(Entity).filter(Entity.id == entity_uuid).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    source = entity.source
    content = ""
    if source:
        content = source.title

    relevance_score = Classifier.classify_entity(entity, content)

    existing = db.query(RelevanceScore).filter(RelevanceScore.entity_id == entity.id).first()
    if existing:
        db.delete(existing)

    db.add(relevance_score)
    db.commit()
    return {"message": "Classification complete", "relevance_level": relevance_score.relevance_level}

@router.get("/export")
def export_results(format: str = "csv", relevance: Optional[str] = None, db: Session = Depends(get_db)):
    entities = db.query(Entity).all()
    if relevance:
        entities = [e for e in entities if e.relevance and e.relevance.relevance_level.lower() == relevance.lower()]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Type", "Unit", "Contact", "Relevance", "Score", "Source URL"])

    for e in entities:
        score = e.relevance.score_total if e.relevance else 0
        rel_level = e.relevance.relevance_level if e.relevance else "N/A"
        writer.writerow([
            e.id, e.name, e.entity_type, e.unit_name, e.official_contact,
            rel_level, score, e.source.url if e.source else ""
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=entities_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
