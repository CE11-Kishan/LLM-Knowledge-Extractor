from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, models
from .database import get_db
from .services.llm import extract_text_insights
from .services.analysis import extract_keywords, confidence

router = APIRouter()

@router.post("/analyze", response_model=schemas.AnalysisResponse)
def analyze(req: schemas.AnalysisCreate, db: Session = Depends(get_db)):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    try:
        summary, topics, title, sentiment_label = extract_text_insights(text)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    extracted_keywords = extract_keywords(text)
    confidence_score = confidence(summary, topics, extracted_keywords)
    obj = models.Analysis(
        original_text=text,
        summary=summary,
        title=title,
        topics=",".join(topics),
        sentiment=sentiment_label,
        keywords=",".join(extracted_keywords),
        confidence=confidence_score,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return schemas.AnalysisResponse(
        id=obj.id,
        created_at=obj.created_at,
        original_text=obj.original_text,
        summary=obj.summary,
        title=obj.title,
        topics=obj.topics_list(),
        sentiment=obj.sentiment,
        keywords=obj.keywords_list(),
        confidence=obj.confidence,
    )


@router.get("/search", response_model=schemas.SearchResponse)
def search(topic: str, db: Session = Depends(get_db)):
    """Search stored analyses by topic/keyword fragment (case-insensitive)."""
    search_term = topic.lower()
    query = db.query(models.Analysis).filter(
        (models.Analysis.topics.like(f"%{search_term}%")) | (models.Analysis.keywords.like(f"%{search_term}%"))
    ).order_by(models.Analysis.created_at.desc())
    analysis_rows = query.all()
    return schemas.SearchResponse(
        results=[
            schemas.AnalysisResponse(
                id=analysis_record.id,
                created_at=analysis_record.created_at,
                original_text=analysis_record.original_text,
                summary=analysis_record.summary,
                title=analysis_record.title,
                topics=analysis_record.topics_list(),
                sentiment=analysis_record.sentiment,
                keywords=analysis_record.keywords_list(),
                confidence=analysis_record.confidence,
            )
            for analysis_record in analysis_rows
        ]
    )
