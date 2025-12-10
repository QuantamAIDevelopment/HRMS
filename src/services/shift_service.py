from sqlalchemy.orm import Session
from ..models.shift import Shift
from ..schemas.shift import ShiftCreate, ShiftUpdate

class ShiftService:
    @staticmethod
    def create_shift(db: Session, shift: ShiftCreate):
        db_shift = Shift(**shift.dict())
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        return db_shift

    @staticmethod
    def get_all_shifts(db: Session):
        return db.query(Shift).all()

    @staticmethod
    def get_shift_by_id(db: Session, shift_id: int):
        return db.query(Shift).filter(Shift.shift_id == shift_id).first()

    @staticmethod
    def update_shift(db: Session, shift_id: int, shift_update: ShiftUpdate):
        shift = db.query(Shift).filter(Shift.shift_id == shift_id).first()
        if shift:
            for field, value in shift_update.dict(exclude_unset=True).items():
                setattr(shift, field, value)
            db.commit()
            db.refresh(shift)
        return shift

    @staticmethod
    def delete_shift(db: Session, shift_id: int):
        shift = db.query(Shift).filter(Shift.shift_id == shift_id).first()
        if shift:
            db.delete(shift)
            db.commit()
            return True
        return False

    @staticmethod
    def get_shift_by_name(db: Session, shift_name: str):
        return db.query(Shift).filter(Shift.shift_name == shift_name).first()

    @staticmethod
    def update_shift_by_name(db: Session, shift_name: str, shift_update: ShiftUpdate):
        shift = db.query(Shift).filter(Shift.shift_name == shift_name).first()
        if shift:
            for field, value in shift_update.dict(exclude_unset=True).items():
                setattr(shift, field, value)
            db.commit()
            db.refresh(shift)
        return shift

    @staticmethod
    def delete_shift_by_name(db: Session, shift_name: str):
        shift = db.query(Shift).filter(Shift.shift_name == shift_name).first()
        if shift:
            db.delete(shift)
            db.commit()
            return True
        return False