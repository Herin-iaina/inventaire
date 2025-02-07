# models.py
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from decimal import Decimal

class CategorieBase(BaseModel):
    nom_categorie: str
    description: Optional[str] = None

class CategorieCreate(CategorieBase):
    pass

class Categorie(CategorieBase):
    id_categorie: int
    
    class Config:
        from_attributes = True

class EquipementBase(BaseModel):
    id_categorie: int
    numero_serie: str
    marque: str
    modele: str
    date_achat: date
    date_mise_en_service: date
    statut: str
    localisation: str
    prix: Decimal
    fournisseur: str
    garantie_expire: date
    commentaires: Optional[str] = None

class EquipementCreate(EquipementBase):
    pass

class Equipement(EquipementBase):
    id_equipement: int

    class Config:
        from_attributes = True

class DetailEquipementBase(BaseModel):
    id_equipement: int
    type_connexion: Optional[str] = None
    puissance_watts: Optional[Decimal] = None
    longueur_cable: Optional[Decimal] = None
    couleur: Optional[str] = None
    compatibilite: Optional[str] = None
    caracteristiques_specifiques: Optional[str] = None

class DetailEquipementCreate(DetailEquipementBase):
    pass

class DetailEquipement(DetailEquipementBase):
    id_detail: int

    class Config:
        from_attributes = True

# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./equipment.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# crud.py
from sqlalchemy.orm import Session
from . import models, schemas

# Opérations CRUD pour Categorie
def create_categorie(db: Session, categorie: schemas.CategorieCreate):
    db_categorie = models.Categorie(**categorie.dict())
    db.add(db_categorie)
    db.commit()
    db.refresh(db_categorie)
    return db_categorie

def get_categorie(db: Session, categorie_id: int):
    return db.query(models.Categorie).filter(models.Categorie.id_categorie == categorie_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Categorie).offset(skip).limit(limit).all()

def update_categorie(db: Session, categorie_id: int, categorie: schemas.CategorieCreate):
    db_categorie = db.query(models.Categorie).filter(models.Categorie.id_categorie == categorie_id).first()
    for key, value in categorie.dict().items():
        setattr(db_categorie, key, value)
    db.commit()
    return db_categorie

def delete_categorie(db: Session, categorie_id: int):
    db_categorie = db.query(models.Categorie).filter(models.Categorie.id_categorie == categorie_id).first()
    db.delete(db_categorie)
    db.commit()
    return db_categorie

# Opérations CRUD pour Equipement
def create_equipement(db: Session, equipement: schemas.EquipementCreate):
    db_equipement = models.Equipement(**equipement.dict())
    db.add(db_equipement)
    db.commit()
    db.refresh(db_equipement)
    return db_equipement

def get_equipement(db: Session, equipement_id: int):
    return db.query(models.Equipement).filter(models.Equipement.id_equipement == equipement_id).first()

def get_equipements(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Equipement).offset(skip).limit(limit).all()

def update_equipement(db: Session, equipement_id: int, equipement: schemas.EquipementCreate):
    db_equipement = db.query(models.Equipement).filter(models.Equipement.id_equipement == equipement_id).first()
    for key, value in equipement.dict().items():
        setattr(db_equipement, key, value)
    db.commit()
    return db_equipement

def delete_equipement(db: Session, equipement_id: int):
    db_equipement = db.query(models.Equipement).filter(models.Equipement.id_equipement == equipement_id).first()
    db.delete(db_equipement)
    db.commit()
    return db_equipement

# Opérations CRUD pour DetailEquipement
def create_detail_equipement(db: Session, detail: schemas.DetailEquipementCreate):
    db_detail = models.DetailEquipement(**detail.dict())
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail

def get_detail_equipement(db: Session, detail_id: int):
    return db.query(models.DetailEquipement).filter(models.DetailEquipement.id_detail == detail_id).first()

def update_detail_equipement(db: Session, detail_id: int, detail: schemas.DetailEquipementCreate):
    db_detail = db.query(models.DetailEquipement).filter(models.DetailEquipement.id_detail == detail_id).first()
    for key, value in detail.dict().items():
        setattr(db_detail, key, value)
    db.commit()
    return db_detail

def delete_detail_equipement(db: Session, detail_id: int):
    db_detail = db.query(models.DetailEquipement).filter(models.DetailEquipement.id_detail == detail_id).first()
    db.delete(db_detail)
    db.commit()
    return db_detail

# main.py
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints pour Categorie
@app.post("/categories/", response_model=schemas.Categorie)
def create_categorie_endpoint(categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    return crud.create_categorie(db=db, categorie=categorie)

@app.get("/categories/", response_model=List[schemas.Categorie])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@app.get("/categories/{categorie_id}", response_model=schemas.Categorie)
def read_categorie(categorie_id: int, db: Session = Depends(get_db)):
    db_categorie = crud.get_categorie(db, categorie_id=categorie_id)
    if db_categorie is None:
        raise HTTPException(status_code=404, detail="Categorie not found")
    return db_categorie

@app.put("/categories/{categorie_id}", response_model=schemas.Categorie)
def update_categorie_endpoint(categorie_id: int, categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    return crud.update_categorie(db=db, categorie_id=categorie_id, categorie=categorie)

@app.delete("/categories/{categorie_id}", response_model=schemas.Categorie)
def delete_categorie_endpoint(categorie_id: int, db: Session = Depends(get_db)):
    return crud.delete_categorie(db=db, categorie_id=categorie_id)

# Endpoints pour Equipement
@app.post("/equipements/", response_model=schemas.Equipement)
def create_equipement_endpoint(equipement: schemas.EquipementCreate, db: Session = Depends(get_db)):
    return crud.create_equipement(db=db, equipement=equipement)

@app.get("/equipements/", response_model=List[schemas.Equipement])
def read_equipements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    equipements = crud.get_equipements(db, skip=skip, limit=limit)
    return equipements

@app.get("/equipements/{equipement_id}", response_model=schemas.Equipement)
def read_equipement(equipement_id: int, db: Session = Depends(get_db)):
    db_equipement = crud.get_equipement(db, equipement_id=equipement_id)
    if db_equipement is None:
        raise HTTPException(status_code=404, detail="Equipement not found")
    return db_equipement

@app.put("/equipements/{equipement_id}", response_model=schemas.Equipement)
def update_equipement_endpoint(equipement_id: int, equipement: schemas.EquipementCreate, db: Session = Depends(get_db)):
    return crud.update_equipement(db=db, equipement_id=equipement_id, equipement=equipement)

@app.delete("/equipements/{equipement_id}", response_model=schemas.Equipement)
def delete_equipement_endpoint(equipement_id: int, db: Session = Depends(get_db)):
    return crud.delete_equipement(db=db, equipement_id=equipement_id)

# Endpoints pour DetailEquipement
@app.post("/details/", response_model=schemas.DetailEquipement)
def create_detail_endpoint(detail: schemas.DetailEquipementCreate, db: Session = Depends(get_db)):
    return crud.create_detail_equipement(db=db, detail=detail)

@app.get("/details/{detail_id}", response_model=schemas.DetailEquipement)
def read_detail(detail_id: int, db: Session = Depends(get_db)):
    db_detail = crud.get_detail_equipement(db, detail_id=detail_id)
    if db_detail is None:
        raise HTTPException(status_code=404, detail="Detail not found")
    return db_detail

@app.put("/details/{detail_id}", response_model=schemas.DetailEquipement)
def update_detail_endpoint(detail_id: int, detail: schemas.DetailEquipementCreate, db: Session = Depends(get_db)):
    return crud.update_detail_equipement(db=db, detail_id=detail_id, detail=detail)

@app.delete("/details/{detail_id}", response_model=schemas.DetailEquipement)
def delete_detail_endpoint(detail_id: int, db: Session = Depends(get_db)):
    return crud.delete_detail_equipement(db=db, detail_id=detail_id)







from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
from . import models, schemas

# Configuration du logger
logger = logging.getLogger(__name__)

class CategorieOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_categorie(self, categorie_data: dict) -> "models.Categorie":
        try:
            nom_categorie = categorie_data.get("nom_categorie")
            if not nom_categorie:
                raise HTTPException(status_code=400, detail="Le nom de la catégorie est requis")

            existing_categorie = self.db.query(models.Categorie).filter(
                models.Categorie.nom_categorie == nom_categorie
            ).first()

            if existing_categorie:
                for key, value in categorie_data.items():
                    if hasattr(existing_categorie, key) and value is not None:
                        setattr(existing_categorie, key, value)
                categorie = existing_categorie
                logger.info(f"Catégorie mise à jour avec le nom : {nom_categorie}")
            else:
                categorie = models.Categorie(**categorie_data)
                self.db.add(categorie)
                logger.info(f"Nouvelle catégorie créée avec le nom : {nom_categorie}")

            self.db.commit()
            self.db.refresh(categorie)
            return categorie

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def get_categorie(self, categorie_id: int) -> "models.Categorie":
        try:
            categorie = self.db.query(models.Categorie).filter(
                models.Categorie.id_categorie == categorie_id
            ).first()
            if not categorie:
                logger.warning(f"Catégorie non trouvée avec l'ID : {categorie_id}")
                raise HTTPException(status_code=404, detail="Catégorie non trouvée")
            return categorie

        except SQLAlchemyError as e:
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def get_all_categories(self, skip: int = 0, limit: int = 100) -> list["models.Categorie"]:
        try:
            categories = self.db.query(models.Categorie).offset(skip).limit(limit).all()
            return categories

        except SQLAlchemyError as e:
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def delete_categorie(self, categorie_id: int) -> "models.Categorie":
        try:
            categorie = self.get_categorie(categorie_id)
            self.db.delete(categorie)
            self.db.commit()
            logger.info(f"Catégorie supprimée avec l'ID : {categorie_id}")
            return categorie

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

class EquipementOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_equipement(self, equipement_data: dict, detail_data: dict) -> "models.Equipement":
        try:
            numero_serie = equipement_data.get("numero_serie")
            if not numero_serie:
                raise HTTPException(status_code=400, detail="Le numéro de série est requis")

            existing_equipement = self.db.query(models.Equipement).filter(
                models.Equipement.numero_serie == numero_serie
            ).first()

            if existing_equipement:
                for key, value in equipement_data.items():
                    if hasattr(existing_equipement, key) and value is not None:
                        setattr(existing_equipement, key, value)
                equipement = existing_equipement
                logger.info(f"Équipement mis à jour avec le numéro de série : {numero_serie}")
            else:
                equipement = models.Equipement(**equipement_data)
                self.db.add(equipement)
                self.db.commit()
                self.db.refresh(equipement)
                logger.info(f"Nouvel équipement créé avec le numéro de série : {numero_serie}")

                # Ajout des détails de l'équipement
                detail_data["id_equipement"] = equipement.id_equipement
                detail = models.DetailEquipement(**detail_data)
                self.db.add(detail)
                logger.info(f"Nouvel détail de l'équipement créé pour l'ID de l'équipement : {equipement.id_equipement}")

            self.db.commit()
            self.db.refresh(equipement)
            return equipement

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def get_equipement(self, equipement_id: int) -> "models.Equipement":
        try:
            equipement = self.db.query(models.Equipement).filter(
                models.Equipement.id_equipement == equipement_id
            ).first()
            if not equipement:
                logger.warning(f"Équipement non trouvé avec l'ID : {equipement_id}")
                raise HTTPException(status_code=404, detail="Équipement non trouvé")
            return equipement

        except SQLAlchemyError as e:
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def get_all_equipements(self, skip: int = 0, limit: int = 100) -> list["models.Equipement"]:
        try:
            equipements = self.db.query(models.Equipement).offset(skip).limit(limit).all()
            return equipements

        except SQLAlchemyError as e:
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def delete_equipement(self, equipement_id: int) -> "models.Equipement":
        try:
            equipement = self.get_equipement(equipement_id)
            self.db.delete(equipement)
            self.db.commit()
            logger.info(f"Équipement supprimé avec l'ID : {equipement_id}")
            return equipement

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

class DetailEquipementOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_detail(self, detail_data: dict) -> "models.DetailEquipement":
        try:
            id_equipement = detail_data.get("id_equipement")
            if not id_equipement:
                raise HTTPException(status_code=400, detail="L'ID de l'équipement est requis")

            existing_detail = self.db.query(models.DetailEquipement).filter(
                models.DetailEquipement.id_equipement == id_equipement
            ).first()

            if existing_detail:
                for key, value in detail_data.items():
                    if hasattr(existing_detail, key) and value is not None:
                        setattr(existing_detail, key, value)
                detail = existing_detail
                logger.info(f"Détail de l'équipement mis à jour avec l'ID de l'équipement : {id_equipement}")
            else:
                detail = models.DetailEquipement(**detail_data)
                self.db.add(detail)
                logger.info(f"Nouveau détail de l'équipement créé avec l'ID de l'équipement : {id_equipement}")

            self.db.commit()
            self.db.refresh(detail)
            return detail

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Erreur de base de données : {str(e)}")
            raise HTTPException(status_code=500, detail="Échec de l'opération sur la base de données")

    def get_detail(self, detail_id: int) -> "models.DetailEquipement":
        try:
            detail = self.db.query(models.DetailEquipement).filter(
                models.DetailEquipement.id_detail == detail_id
            ).first()
            if not detail:
                logger.warning(f"Détail de l'équipement non trouvé avec l'ID : {detail_id}")
                raise HTTPException(status_code=404, detail="Détail de l'équipement non trouvé")




from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import logging
from . import models, schemas

# Configuration du logger
logger = logging.getLogger(__name__)


class EquipementOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_equipement(self, equipement_data: dict, detail_data: dict) -> "models.Equipement":
        try:
            numero_serie = equipement_data.get("numero_serie")
            if not numero_serie:
                raise HTTPException(status_code=400, detail="Serial number is required")

            existing_equipement = self.db.query(models.Equipement).filter(
                models.Equipement.numero_serie == numero_serie
            ).first()

            if existing_equipement:
                for key, value in equipement_data.items():
                    if hasattr(existing_equipement, key) and value is not None:
                        setattr(existing_equipement, key, value)
                equipement = existing_equipement
                logger.info(f"Updated equipment with serial number: {numero_serie}")
            else:
                equipement = models.Equipement(**equipement_data)
                self.db.add(equipement)
                self.db.commit()
                self.db.refresh(equipement)
                logger.info(f"Created new equipment with serial number: {numero_serie}")

                # Ajout des détails de l'équipement
                detail_data["id_equipement"] = equipement.id_equipement
                detail = models.DetailEquipement(**detail_data)
                self.db.add(detail)
                logger.info(f"Created new equipment detail with equipment ID : {equipement.id_equipement}")

            self.db.commit()
            self.db.refresh(equipement)
            return equipement

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_equipement(self, equipement_id: int) -> "models.Equipement":
        try:
            equipement = self.db.query(models.Equipement).filter(
                models.Equipement.id_equipement == equipement_id
            ).first()
            if not equipement:
                logger.warning(f"Equipment not found with ID: {equipement_id}")
                raise HTTPException(status_code=404, detail="Equipment not found")
            return equipement

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_all_equipements(self, skip: int = 0, limit: int = 100) -> list["models.Equipement"]:
        try:
            equipements = self.db.query(models.Equipement).offset(skip).limit(limit).all()
            return equipements

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def delete_equipement(self, equipement_id: int) -> "models.Equipement":
        try:
            equipement = self.get_equipement(equipement_id)
            self.db.delete(equipement)
            self.db.commit()
            logger.info(f"Deleted equipment with ID: {equipement_id}")
            return equipement

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

# Création d'un équipement
{
    "equipement_data": {
        "numero_serie": "ABC123",
        "marque": "Dell",
        "modele": "Latitude",
        "date_achat": "2023-01-15"
    },
    "detail_data": {
        "type_connexion": "USB-C",
        "puissance_watts": 65.0
    }
}

# Modification sera automatique si le numéro de série existe déjà




from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional

# Importations locales
from .database import get_db
from .operations import EquipementOperations
from .schemas import EquipementCreate, DetailEquipementCreate

# Création du routeur
# router = APIRouter(prefix="/equipements", tags=["equipements"])

@app.post("/equipements/", response_model=schemas.Equipement)
def create_or_update_equipement(
    equipement_data: Dict,
    detail_data: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """
    Créer ou mettre à jour un équipement avec ses détails optionnels
    
    - Si un équipement avec le même numéro de série existe, il sera mis à jour
    - Les détails peuvent être ajoutés ou mis à jour simultanément
    """
    try:
        operations = EquipementOperations(db)
        equipement = operations.create_or_update_equipement(
            equipement_data, 
            detail_data
        )
        return {
            "message": "Équipement créé ou mis à jour avec succès",
            "equipement": equipement
        }
    except HTTPException as e:
        raise e

@app.get("/equipements/", response_model=List[schemas.Equipement])
def get_equipement_details(
    equipement_id: int, 
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'un équipement spécifique
    """
    operations = EquipementOperations(db)
    return operations.get_equipement_with_details(equipement_id)

@app.delete("/equipements/{equipement_id}", response_model=schemas.Equipement)
def delete_equipement(
    equipement_id: int, 
    db: Session = Depends(get_db)
):
    """
    Supprimer un équipement et ses détails associés
    """
    operations = EquipementOperations(db)
    operations.delete_equipement(equipement_id)
    return {"message": f"Équipement {equipement_id} supprimé avec succès"}



@app.post("/equipements/", response_model=schemas.Equipement)
def create_equipement_endpoint(equipement: schemas.EquipementCreate, db: Session = Depends(get_db)):
    return materiel_operation.create_equipement(db=db, equipement=equipement)

@app.get("/equipements/", response_model=List[schemas.Equipement])
def read_equipements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    equipements = materiel_operation.get_equipements(db, skip=skip, limit=limit)
    return equipements

@app.get("/equipements/{equipement_id}", response_model=schemas.Equipement)
def read_equipement(equipement_id: int, db: Session = Depends(get_db)):
    db_equipement = materiel_operation.get_equipement(db, equipement_id=equipement_id)
    if db_equipement is None:
        raise HTTPException(status_code=404, detail="Equipement not found")
    return db_equipement

@app.put("/equipements/{equipement_id}", response_model=schemas.Equipement)
def update_equipement_endpoint(equipement_id: int, equipement: schemas.EquipementCreate, db: Session = Depends(get_db)):
    return materiel_operation.update_equipement(db=db, equipement_id=equipement_id, equipement=equipement)

@app.delete("/equipements/{equipement_id}", response_model=schemas.Equipement)
def delete_equipement_endpoint(equipement_id: int, db: Session = Depends(get_db)):
    return materiel_operation.delete_equipement(db=db, equipement_id=equipement_id)