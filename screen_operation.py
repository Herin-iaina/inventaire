from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging
from datetime import date

from .database import get_db
from .models import EcranItemsDB, EcranItems

logger = logging.getLogger(__name__)

class ScreenOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_ecran_item(self, screen_item_data: dict) -> "EcranItemsDB":
        try:
            # Check required fields only for creation (when id_ecran is not present)
            if "id_ecran" not in screen_item_data:
                required_fields = ["numero_serie", "marque", "modele", "connectivite"]
                missing_fields = [field for field in required_fields 
                                if not screen_item_data.get(field)]
                if missing_fields:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Required fields missing: {', '.join(missing_fields)}"
                    )

            # If id_ecran is present, it's an update operation
            if "id_ecran" in screen_item_data:
                item_id = screen_item_data["id_ecran"]
                existing_item = self.db.query(EcranItemsDB).filter(
                    EcranItemsDB.id_ecran == item_id
                ).first()
                if not existing_item:
                    raise HTTPException(status_code=404, detail="Screen item not found")
                
                # Update existing item
                for key, value in screen_item_data.items():
                    if hasattr(existing_item, key) and value is not None:
                        setattr(existing_item, key, value)
                item = existing_item
                logger.info(f"Updated screen item with ID: {item_id}")
            else:
                # Check if serial number already exists
                numero_serie = screen_item_data.get("numero_serie")
                existing_item = self.db.query(EcranItemsDB).filter(
                    EcranItemsDB.numero_serie == numero_serie
                ).first()
                
                if existing_item:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Screen with serial number {numero_serie} already exists"
                    )
                
                # Create new item
                item = EcranItemsDB(**screen_item_data)
                self.db.add(item)
                logger.info(f"Created new screen item with serial number: {numero_serie}")

            self.db.commit()
            self.db.refresh(item)
            return item

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_ecran_item(self, item_id: int) -> "EcranItemsDB":
        try:
            item = self.db.query(EcranItemsDB).filter(EcranItemsDB.id_ecran == item_id).first()
            if not item:
                logger.warning(f"Screen item not found with ID: {item_id}")
                raise HTTPException(status_code=404, detail="Screen item not found")
            return item

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def list_ecran_items(self, skip: int = 0, limit: int = 100) -> List["EcranItemsDB"]:
        try:
            items = self.db.query(EcranItemsDB).offset(skip).limit(limit).all()
            return items

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def delete_ecran_item(self, item_id: int) -> bool:
        try:
            item = self.db.query(EcranItemsDB).filter(EcranItemsDB.id_ecran == item_id).first()
            if not item:
                logger.warning(f"Screen item not found with ID: {item_id}")
                raise HTTPException(status_code=404, detail="Screen item not found")
            
            self.db.delete(item)
            self.db.commit()
            logger.info(f"Deleted screen item with ID: {item_id}")
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def search_ecran_items(self, 
                        numero_serie: Optional[str] = None,
                        modele: Optional[str] = None,
                        statut: Optional[str] = None) -> List["EcranItemsDB"]:
        try:
            query = self.db.query(EcranItemsDB)
            
            if numero_serie:
                query = query.filter(EcranItemsDB.numero_serie.ilike(f"%{numero_serie}%"))
                logger.info(f"Searching for screen with serial number containing: {numero_serie}")
            if modele:
                query = query.filter(EcranItemsDB.modele.ilike(f"%{modele}%"))
                logger.info(f"Filtering by model containing: {modele}")
            if statut:
                query = query.filter(EcranItemsDB.statut == statut)
                logger.info(f"Filtering by status: {statut}")

            return query.all()

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")