from fastapi import HTTPException
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging
from datetime import date

from .database import get_db  # Import get_db from  database module
from .models import MacItemDB, MacItem  # Import  SQLAlchemy and Pydantic models
from audit_manager import audit_changes, AuditManager, AuditLog


# Configure logging
logger = logging.getLogger(__name__)

class MacOperations:
    def __init__(self, db: Session):
        self.db = db
        self.audit_manager = AuditManager(db)

    @audit_changes(table_name="mac_inventory")
    async def create_or_update_mac_item(self, mac_item_data: dict) -> "MacItemDB":
        try:
            numero_serie = mac_item_data.get("numero_serie")
            if not numero_serie:
                raise HTTPException(status_code=400, detail="Serial number is required")

            existing_item = self.db.query(MacItemDB).filter(
                MacItemDB.numero_serie == numero_serie
            ).first()

            if existing_item:
                for key, value in mac_item_data.items():
                    if hasattr(existing_item, key) and value is not None:
                        setattr(existing_item, key, value)
                item = existing_item
                logger.info(f"Updated MAC item with serial number: {numero_serie}")
            else:
                item = MacItemDB(**mac_item_data)
                self.db.add(item)
                logger.info(f"Created new MAC item with serial number: {numero_serie}")

            self.db.commit()
            self.db.refresh(item)
            return item

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        pass

    def get_mac_item(self, item_id: int) ->  Tuple["MacItemDB", List["AuditLog"]] :
        try:
            item = self.db.query(MacItemDB).filter(MacItemDB.id_mac == item_id).first()
            if not item:
                logger.warning(f"MAC item not found with ID: {item_id}")
                raise HTTPException(status_code=404, detail="MAC item not found")
            
            # Récupération de l'historique
            history = self.audit_manager.get_history(
                table_name="mac_inventory",
                record_id=item_id
            )
            
            # Formatage de l'historique pour l'affichage
            formatted_history = []
            for log in history:
                formatted_log = {
                    "date": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "user": self._get_user_info(log.user_id),
                    "action": log.action.value,
                    "changes": self._format_changes(log.old_values, log.new_values)
                }
                formatted_history.append(formatted_log)

            return item, formatted_history

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        pass

    def list_mac_items(self, skip: int = 0, limit: int = 100) -> List["MacItemDB"]:
        try:
            items = self.db.query(MacItemDB).offset(skip).limit(limit).all()
            result = []
            
            for item in items:
                # Récupère uniquement le dernier changement pour la liste
                last_change = self.audit_manager.get_history(
                    table_name="mac_inventory",
                    record_id=item.id_mac,
                    limit=1
                )
                
                item_dict = self._model_to_dict(item)
                item_dict["last_modification"] = {
                    "date": last_change[0].timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "user": self._get_user_info(last_change[0].user_id),
                    "action": last_change[0].action.value
                } if last_change else None
                
                result.append(item_dict)
            # return items
            return result

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def delete_mac_item(self, item_id: int) -> bool:
        try:
            item = self.db.query(MacItemDB).filter(MacItemDB.id_mac == item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="MAC item not found")
            
            self.db.delete(item)
            self.db.commit()
            logger.info(f"Deleted MAC item with ID: {item_id}")
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def search_mac_items(self, 
                        numero_serie: Optional[str] = None,
                        modele: Optional[str] = None,
                        statut: Optional[str] = None) -> List["MacItemDB"]:
        try:
            query = self.db.query(MacItemDB)
            
            if numero_serie:
                query = query.filter(MacItemDB.numero_serie.ilike(f"%{numero_serie}%"))
            if modele:
                query = query.filter(MacItemDB.modele.ilike(f"%{modele}%"))
            if statut:
                query = query.filter(MacItemDB.statut == statut)

            return query.all()

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
