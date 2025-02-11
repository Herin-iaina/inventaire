# audit_manager.py
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from functools import wraps
import json

Base = declarative_base()

class ActionType(PyEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(Enum(ActionType), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Champs additionnels pour plus de contexte
    ip_address = Column(String(50))
    user_agent = Column(String(200))

class AuditManager:
    def __init__(self, db: Session):
        self.db = db

    def _serialize_model(self, model) -> dict:
        """Convertit un modèle SQLAlchemy en dictionnaire"""
        data = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            # Gestion des types spéciaux
            if isinstance(value, datetime):
                value = value.isoformat()
            if hasattr(value, '__dict__'):
                continue  # Évite les relations complexes
            data[column.name] = value
        return data

    def log_change(
        self,
        table_name: str,
        record_id: int,
        action: ActionType,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Enregistre une modification dans l'historique"""
        audit_entry = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            user_id=user_id or self._get_current_user_id(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(audit_entry)
        self.db.commit()

    def get_history(
        self,
        table_name: str,
        record_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
        action: Optional[ActionType] = None
    ) -> list:
        """Récupère l'historique avec filtres optionnels"""
        query = self.db.query(AuditLog).filter(AuditLog.table_name == table_name)
        
        if record_id is not None:
            query = query.filter(AuditLog.record_id == record_id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
            
        return query.order_by(AuditLog.timestamp.desc()).all()

    def _get_current_user_id(self) -> int:
        """À implémenter selon votre système d'authentification"""
        from fastapi import Request
        request = Request.get_current()
        return request.state.user_id

def audit_changes(table_name: str):
    """Décorateur pour auditer automatiquement les changements"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            audit_manager = AuditManager(self.db)
            
            # Capture l'état avant modification
            old_state = None
            record_id = kwargs.get('id') or (args[0] if args else None)
            if record_id and hasattr(self, 'get_by_id'):
                old_item = await self.get_by_id(record_id)
                if old_item:
                    old_state = audit_manager._serialize_model(old_item)
            
            # Exécute la fonction
            result = await func(self, *args, **kwargs)
            
            # Détermine l'action et capture le nouvel état
            action = ActionType.CREATE
            if old_state:
                action = ActionType.UPDATE
            if func.__name__.startswith('delete'):
                action = ActionType.DELETE
            
            new_state = None
            if result and action != ActionType.DELETE:
                new_state = audit_manager._serialize_model(result)
            
            # Enregistre dans l'historique
            audit_manager.log_change(
                table_name=table_name,
                record_id=record_id or getattr(result, 'id', None),
                action=action,
                old_values=old_state,
                new_values=new_state
            )
            
            return result
        return wrapper
    return decorator