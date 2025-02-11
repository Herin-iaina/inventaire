from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from functools import wraps
from contextlib import contextmanager

# Fonction utilitaire pour obtenir l'utilisateur courant depuis le contexte de requête
def get_current_user_id():
    # À implémenter selon votre système d'authentification
    # Par exemple, utiliser une variable globale de requête ou un middleware
    from fastapi import Request
    request = Request.get_current()
    return request.state.user_id

class ScreenOperations:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def get_current_state(self, item_id: int) -> dict:
        """Récupère l'état actuel d'un écran pour l'audit"""
        item = self.db.query(EcranItemsDB).filter(
            EcranItemsDB.id_ecran == item_id
        ).first()
        if item:
            return {
                "numero_serie": item.numero_serie,
                "marque": item.marque,
                "modele": item.modele,
                "connectivite": item.connectivite,
                "statut": item.statut,
                # Ajoutez d'autres champs selon votre modèle
            }
        return None

    @audit_changes(entity_type="ecran")
    def create_or_update_ecran_item(self, screen_item_data: dict) -> "EcranItemsDB":
        try:
            # Logique existante pour la création/mise à jour
            if "id_ecran" not in screen_item_data:
                required_fields = ["numero_serie", "marque", "modele", "connectivite"]
                missing_fields = [field for field in required_fields 
                                if not screen_item_data.get(field)]
                if missing_fields:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Required fields missing: {', '.join(missing_fields)}"
                    )

            if "id_ecran" in screen_item_data:
                item_id = screen_item_data["id_ecran"]
                existing_item = self.db.query(EcranItemsDB).filter(
                    EcranItemsDB.id_ecran == item_id
                ).first()
                if not existing_item:
                    raise HTTPException(status_code=404, detail="Screen item not found")
                
                for key, value in screen_item_data.items():
                    if hasattr(existing_item, key) and value is not None:
                        setattr(existing_item, key, value)
                item = existing_item
            else:
                numero_serie = screen_item_data.get("numero_serie")
                existing_item = self.db.query(EcranItemsDB).filter(
                    EcranItemsDB.numero_serie == numero_serie
                ).first()
                
                if existing_item:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Screen with serial number {numero_serie} already exists"
                    )
                
                item = EcranItemsDB(**screen_item_data)
                self.db.add(item)

            self.db.commit()
            self.db.refresh(item)
            return item

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    @audit_changes(entity_type="ecran")
    def delete_ecran_item(self, item_id: int) -> bool:
        try:
            item = self.db.query(EcranItemsDB).filter(EcranItemsDB.id_ecran == item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail="Screen item not found")
            
            # Capture l'état avant suppression pour l'audit
            old_state = self.get_current_state(item_id)
            
            self.db.delete(item)
            self.db.commit()
            
            # Log de la suppression
            self.audit_service.log_action(
                user_id=get_current_user_id(),
                action_type=ActionType.DELETE,
                entity_type="ecran",
                entity_id=item_id,
                old_values=old_state,
                new_values=None
            )
            
            return True

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    # Méthode pour consulter l'historique d'un écran
    def get_ecran_history(self, item_id: int) -> List[AuditLog]:
        """Récupère l'historique complet des modifications d'un écran"""
        return self.audit_service.get_entity_history("ecran", item_id)
    



    from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime

class ScreenOperations:
    def __init__(self, db: Session):
        self.db = db
        self.audit_manager = AuditManager(db)

    def get_ecran_item(self, item_id: int) -> Tuple["EcranItemsDB", List["AuditLog"]]:
        """
        Récupère un écran et son historique complet
        """
        try:
            # Récupération de l'écran
            item = self.db.query(EcranItemsDB).filter(
                EcranItemsDB.id_ecran == item_id
            ).first()
            
            if not item:
                logger.warning(f"Screen item not found with ID: {item_id}")
                raise HTTPException(status_code=404, detail="Screen item not found")
            
            # Récupération de l'historique
            history = self.audit_manager.get_history(
                table_name="ecrans",
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

    def list_ecran_items(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        Liste tous les écrans avec leur dernier changement
        """
        try:
            items = self.db.query(EcranItemsDB).offset(skip).limit(limit).all()
            result = []
            
            for item in items:
                # Récupère uniquement le dernier changement pour la liste
                last_change = self.audit_manager.get_history(
                    table_name="ecrans",
                    record_id=item.id_ecran,
                    limit=1
                )
                
                item_dict = self._model_to_dict(item)
                item_dict["last_modification"] = {
                    "date": last_change[0].timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "user": self._get_user_info(last_change[0].user_id),
                    "action": last_change[0].action.value
                } if last_change else None
                
                result.append(item_dict)
            
            return result

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def _model_to_dict(self, model: "EcranItemsDB") -> Dict:
        """Convertit un modèle en dictionnaire"""
        return {
            "id_ecran": model.id_ecran,
            "numero_serie": model.numero_serie,
            "marque": model.marque,
            "modele": model.modele,
            "connectivite": model.connectivite,
            "statut": model.statut
            # Ajoutez d'autres champs selon votre modèle
        }

    def _get_user_info(self, user_id: int) -> Dict:
        """Récupère les informations de l'utilisateur"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        return {"id": user_id, "name": "Unknown", "email": ""}

    def _format_changes(self, old_values: Dict, new_values: Dict) -> List[Dict]:
        """Formate les changements pour l'affichage"""
        changes = []
        if not old_values:  # Création
            return [{"field": k, "old": None, "new": v} 
                   for k, v in new_values.items()]
        
        if not new_values:  # Suppression
            return [{"field": k, "old": v, "new": None} 
                   for k, v in old_values.items()]
        
        # Modification
        for key in set(old_values.keys()) | set(new_values.keys()):
            if old_values.get(key) != new_values.get(key):
                changes.append({
                    "field": key,
                    "old": old_values.get(key),
                    "new": new_values.get(key)
                })
        
        return changes

# Dans votre fichier routes.py
@router.get("/ecrans/{item_id}")
async def get_ecran(item_id: int, db: Session = Depends(get_db)):
    screen_ops = ScreenOperations(db)
    item, history = screen_ops.get_ecran_item(item_id)
    return {
        "item": item,
        "history": history
    }

@router.get("/ecrans")
async def list_ecrans(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    screen_ops = ScreenOperations(db)
    return screen_ops.list_ecran_items(skip, limit)