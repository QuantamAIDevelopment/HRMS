from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from src.models.session import get_db
from src.models.events_holidays import EventsHolidays
from src.schemas.events_holidays import EventsHolidaysCreate, EventsHolidaysResponse

router = APIRouter()

@router.post("/", response_model=EventsHolidaysResponse)
def create_event_holiday(event: EventsHolidaysCreate, db: Session = Depends(get_db)):
    db_obj = EventsHolidays(**event.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[EventsHolidaysResponse])
def get_all_events_holidays(db: Session = Depends(get_db)):
    query = text("SELECT * FROM events_holidays ORDER BY event_date ASC")
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/cards")
def get_events_holidays_cards(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN type = 'Event' THEN 1 END) as events,
            COUNT(CASE WHEN type = 'Public Holiday' THEN 1 END) as public_holidays,
            COUNT(CASE WHEN type = 'Optional Holiday' THEN 1 END) as optional_holidays
        FROM events_holidays
    """)
    result = db.execute(query).fetchone()
    return dict(result._mapping)

@router.put("/{title}", response_model=EventsHolidaysResponse)
def update_event_holiday(title: str, event: EventsHolidaysCreate, db: Session = Depends(get_db)):
    db_obj = db.query(EventsHolidays).filter(EventsHolidays.title == title).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Event/Holiday not found")
    
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.delete("/{title}")
def delete_event_holiday(title: str, db: Session = Depends(get_db)):
    db_obj = db.query(EventsHolidays).filter(EventsHolidays.title == title).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Event/Holiday not found")
    
    db.delete(db_obj)
    db.commit()
    return {"message": "Event/Holiday deleted successfully"}

