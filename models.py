from sqlalchemy import Column, Integer, String, Date, Float, Text, create_engine, Numeric
from decimal import Decimal
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import os
from enum import Enum as PyEnum
from database import Base, engine, get_db



class MacStatus(str, PyEnum):
    EN_SERVICE = "En service"
    NON_ATTRIBUE = "Non Attribué"
    EN_REPARATION = "En réparation"
    VENDUE = "Vendue"

class StorageType(str, PyEnum):
    SSD = "SSD"
    HDD = "HDD"

# SQLAlchemy Model
class MacItemDB(Base):
    __tablename__ = "mac_inventory"

    id_mac = Column(Integer, primary_key=True, autoincrement=True)
    numero_serie = Column(String(50), unique=True, nullable=False)
    modele = Column(String(100))
    type_mac = Column(String(50))
    annee_achat = Column(Date)
    processeur = Column(String(100))
    ram = Column(Integer)
    stockage = Column(Integer)
    stockage_type = Column(String(50))
    ecran_taille = Column(Float)
    resolution_ecran = Column(String(50))
    numero_serie_apple = Column(String(50))
    statut = Column(String(50))
    localisation = Column(String(100))
    date_dernier_inventaire = Column(Date)
    commentaires = Column(Text)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Model for API
class MacItem(BaseModel):
    id_mac: Optional[int] = None
    numero_serie: str = Field(..., max_length=50)
    modele: Optional[str] = Field(None, max_length=100)
    type_mac: Optional[str] = Field(None, max_length=50)
    annee_achat: Optional[date] = None
    processeur: Optional[str] = Field(None, max_length=100)
    ram: Optional[int] = Field(None, gt=0)
    stockage: Optional[int] = Field(None, gt=0)
    stockage_type: Optional[str] = Field(None, max_length=50)
    ecran_taille: Optional[float] = Field(None, gt=0)
    resolution_ecran: Optional[str] = Field(None, max_length=50)
    numero_serie_apple: Optional[str] = Field(None, max_length=50)
    statut: Optional[str] = Field(None, max_length=50)
    localisation: Optional[str] = Field(None, max_length=100)
    date_dernier_inventaire: Optional[date] = None
    commentaires: Optional[str] = None

    class Config:
        orm_mode = True

    # Model for creating new items
class MacItemCreate(MacItem):
    annee_achat: Optional[date] = None
    processeur: Optional[str] = Field(None, max_length=100)
    ecran_taille: Optional[float] = Field(None, gt=0)
    resolution_ecran: Optional[str] = Field(None, max_length=50)
    numero_serie_apple: Optional[str] = Field(None, max_length=50)
    localisation: Optional[str] = Field(None, max_length=100)
    date_dernier_inventaire: Optional[date] = None
    commentaires: Optional[str] = None

# Model for updating existing items
class MacItemUpdate(BaseModel):
    modele: Optional[str] = Field(None, max_length=100)
    type_mac: Optional[str] = Field(None, max_length=50)
    ram: Optional[int] = Field(None, gt=0)
    stockage: Optional[int] = Field(None, gt=0)
    stockage_type: Optional[StorageType] = None
    statut: Optional[MacStatus] = None
    localisation: Optional[str] = Field(None, max_length=100)
    commentaires: Optional[str] = None


# Ecran
# Modèle SQLAlchemy pour la table écran
class EcranItemsDB(Base):
    __tablename__ = "ecran"

    id_ecran = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String(50), unique=True, nullable=False)
    marque = Column(String(100))
    modele = Column(String(100))
    type_ecran = Column(String(50))
    taille_ecran = Column(Numeric(5,2))
    resolution_largeur = Column(Integer)
    resolution_hauteur = Column(Integer)
    ratio_ecran = Column(String(20))
    technologie = Column(String(50))
    frequence_rafraichissement = Column(Integer)
    connectivite = Column(String(200))
    annee_achat = Column(Date)
    date_installation = Column(Date)
    localisation = Column(String(100))
    statut = Column(String(50))
    garantie_expire = Column(Date)
    prix = Column(Numeric(10,2))
    fournisseur = Column(String(100))
    commentaires = Column(Text)

# Modèle Pydantic pour la validation des données
class EcranItems(BaseModel):
    numero_serie: str
    marque: Optional[str] = None
    modele: Optional[str] = None
    type_ecran: Optional[str] = None
    taille_ecran: Optional[Decimal] = None
    resolution_largeur: Optional[int] = None
    resolution_hauteur: Optional[int] = None
    ratio_ecran: Optional[str] = None
    technologie: Optional[str] = None
    frequence_rafraichissement: Optional[int] = None
    connectivite: Optional[str] = None
    annee_achat: Optional[date] = None
    date_installation: Optional[date] = None
    localisation: Optional[str] = None
    statut: Optional[str] = None
    garantie_expire: Optional[date] = None
    prix: Optional[Decimal] = None
    fournisseur: Optional[str] = None
    commentaires: Optional[str] = None

class EcranCreate(EcranItems):
    numero_serie: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    connectivite: Optional[str] = None


class EcranUpdate(EcranItems):
    numero_serie: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    connectivite: Optional[str] = None

class EcranInDB(EcranItems):
    id_ecran: int

        