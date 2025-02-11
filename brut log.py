from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

# Énumération pour les types d'actions
class ActionType(PyEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

# Modèle pour les utilisateurs autorisés
class AuthorizedUser(Base):
    __tablename__ = 'authorized_users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    google_id = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Modèle pour l'historique des modifications
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('authorized_users.id'))
    action_type = Column(Enum(ActionType))
    entity_type = Column(String(50))  # Ex: 'Product', 'Category'
    entity_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('AuthorizedUser')

# Service pour la gestion de l'authentification
class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session
        
    def is_authorized(self, email):
        """Vérifie si l'utilisateur est autorisé"""
        user = self.db_session.query(AuthorizedUser).filter_by(
            email=email, 
            is_active=True
        ).first()
        return user is not None
    
    def register_google_user(self, google_user_info):
        """Enregistre ou met à jour un utilisateur Google"""
        user = self.db_session.query(AuthorizedUser).filter_by(
            email=google_user_info['email']
        ).first()
        
        if user and user.is_active:
            user.google_id = google_user_info['sub']
            self.db_session.commit()
            return user
        return None

# Service pour la gestion de l'historique
class AuditService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def log_action(self, user_id, action_type, entity_type, entity_id, old_values=None, new_values=None):
        """Enregistre une action dans l'historique"""
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values
        )
        self.db_session.add(audit_log)
        self.db_session.commit()
    
    def get_entity_history(self, entity_type, entity_id):
        """Récupère l'historique d'une entité"""
        return self.db_session.query(AuditLog).filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(AuditLog.timestamp.desc()).all()

# Exemple de décorateur pour tracer automatiquement les modifications
def audit_changes(entity_type):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            # Capture l'état avant modification
            old_state = None
            entity_id = kwargs.get('id')
            if entity_id:
                old_state = self.get_current_state(entity_id)
            
            # Exécute la fonction
            result = f(self, *args, **kwargs)
            
            # Capture le nouvel état et enregistre la modification
            new_state = self.get_current_state(entity_id or result.id)
            AuditService().log_action(
                user_id=get_current_user_id(),
                action_type=ActionType.UPDATE if entity_id else ActionType.CREATE,
                entity_type=entity_type,
                entity_id=entity_id or result.id,
                old_values=old_state,
                new_values=new_state
            )
            return result
        return wrapper
    return decorator