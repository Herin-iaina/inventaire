from sqlalchemy import Column, Integer, String, Date, Float, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum

Base = declarative_base()

# Énumérations communes
class Status(str, PyEnum):
    EN_SERVICE = "En service"
    NON_ATTRIBUE = "Non Attribué"
    EN_REPARATION = "En réparation"
    VENDU = "Vendu"
    STOCK = "En stock"

class StorageType(str, PyEnum):
    SSD = "SSD"
    HDD = "HDD"

# Table de base avec les champs communs
class InventoryBase(Base):
    __abstract__ = True
    
    numero_serie = Column(String(50), unique=True, nullable=False)
    marque = Column(String(100))
    modele = Column(String(100))
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    annee_achat = Column(Date)
    localisation = Column(String(100))
    statut = Column(String(50))
    prix = Column(Numeric(10, 2))
    fournisseur = Column(String(100))
    garantie_expire = Column(Date)
    commentaires = Column(Text)

# Modèle SQLAlchemy pour Mac
class MacItemDB(InventoryBase):
    __tablename__ = "mac_inventory"

    id_mac = Column(Integer, primary_key=True, autoincrement=True)
    type_mac = Column(String(50))
    processeur = Column(String(100))
    ram = Column(Integer)
    stockage = Column(Integer)
    stockage_type = Column(String(50))
    ecran_taille = Column(Float)
    resolution_ecran = Column(String(50))
    numero_serie_apple = Column(String(50))
    date_dernier_inventaire = Column(Date)

# Modèle SQLAlchemy pour Écran
class EcranItemDB(InventoryBase):
    __tablename__ = "ecran"

    id_ecran = Column(Integer, primary_key=True, index=True)
    type_ecran = Column(String(50))
    taille_ecran = Column(Numeric(5, 2))
    resolution_largeur = Column(Integer)
    resolution_hauteur = Column(Integer)
    ratio_ecran = Column(String(20))
    technologie = Column(String(50))
    frequence_rafraichissement = Column(Integer)
    connectivite = Column(String(200))
    date_installation = Column(Date)

# Modèle SQLAlchemy pour Catégorie
class CategorieDB(Base):
    __tablename__ = "categories"

    id_categorie = Column(Integer, primary_key=True, autoincrement=True)
    nom_categorie = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    equipements = relationship("EquipementDB", back_populates="categorie")

# Modèle SQLAlchemy pour Équipement
class EquipementDB(InventoryBase):
    __tablename__ = "equipements"

    id_equipement = Column(Integer, primary_key=True, autoincrement=True)
    id_categorie = Column(Integer, ForeignKey('categories.id_categorie'))
    date_mise_en_service = Column(Date)
    
    categorie = relationship("CategorieDB", back_populates="equipements")
    details = relationship("DetailEquipementDB", back_populates="equipement", uselist=False)

# Modèle SQLAlchemy pour Détails Équipement
class DetailEquipementDB(Base):
    __tablename__ = "details_equipement"

    id_detail = Column(Integer, primary_key=True, autoincrement=True)
    id_equipement = Column(Integer, ForeignKey('equipements.id_equipement'))
    type_connexion = Column(String(100))
    puissance_watts = Column(Numeric(10, 2))
    longueur_cable = Column(Numeric(10, 2))
    couleur = Column(String(50))
    compatibilite = Column(String(200))
    caracteristiques_specifiques = Column(Text)
    
    equipement = relationship("EquipementDB", back_populates="details")

# Modèles Pydantic de base
class InventoryBaseSchema(BaseModel):
    numero_serie: str = Field(..., max_length=50)
    marque: Optional[str] = Field(None, max_length=100)
    modele: Optional[str] = Field(None, max_length=100)
    annee_achat: Optional[date] = None
    localisation: Optional[str] = Field(None, max_length=100)
    statut: Optional[Status] = Field(None)
    prix: Optional[Decimal] = None
    fournisseur: Optional[str] = Field(None, max_length=100)
    garantie_expire: Optional[date] = None
    commentaires: Optional[str] = None

    class Config:
        from_attributes = True

# Modèles Pydantic pour Mac
class MacItemCreate(InventoryBaseSchema):
    type_mac: Optional[str] = Field(None, max_length=50)
    processeur: Optional[str] = Field(None, max_length=100)
    ram: Optional[int] = Field(None, gt=0)
    stockage: Optional[int] = Field(None, gt=0)
    stockage_type: Optional[StorageType] = None

class MacItem(MacItemCreate):
    id_mac: int

# Modèles Pydantic pour Écran
class EcranItemCreate(InventoryBaseSchema):
    type_ecran: Optional[str] = Field(None, max_length=50)
    taille_ecran: Optional[Decimal] = Field(None, gt=0)
    resolution_largeur: Optional[int] = Field(None, gt=0)
    resolution_hauteur: Optional[int] = Field(None, gt=0)
    connectivite: Optional[str] = None

class EcranItem(EcranItemCreate):
    id_ecran: int

# Modèles Pydantic pour Catégorie
class CategorieCreate(BaseModel):
    nom_categorie: str = Field(..., max_length=100)
    description: Optional[str] = None

class Categorie(CategorieCreate):
    id_categorie: int
    date_creation: datetime

# Modèles Pydantic pour Équipement
class EquipementCreate(InventoryBaseSchema):
    id_categorie: int
    date_mise_en_service: Optional[date] = None

class DetailEquipementCreate(BaseModel):
    type_connexion: Optional[str] = None
    puissance_watts: Optional[Decimal] = None
    longueur_cable: Optional[Decimal] = None
    couleur: Optional[str] = None
    compatibilite: Optional[str] = None
    caracteristiques_specifiques: Optional[str] = None

class Equipement(EquipementCreate):
    id_equipement: int
    details: Optional[DetailEquipementCreate] = None

# Fonction pour créer toutes les tables
def create_tables(engine):
    Base.metadata.create_all(bind=engine)