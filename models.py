from sqlalchemy import Column, Integer, String, Date, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import os
from database import Base, engine, get_db





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

        