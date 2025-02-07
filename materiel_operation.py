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
                raise HTTPException(status_code=400, detail="Category name is required")

            existing_categorie = self.db.query(models.Categorie).filter(
                models.Categorie.nom_categorie == nom_categorie
            ).first()

            if existing_categorie:
                for key, value in categorie_data.items():
                    if hasattr(existing_categorie, key) and value is not None:
                        setattr(existing_categorie, key, value)
                categorie = existing_categorie
                logger.info(f"Updated category with name: {nom_categorie}")
            else:
                categorie = models.Categorie(**categorie_data)
                self.db.add(categorie)
                logger.info(f"Created new category with name: {nom_categorie}")

            self.db.commit()
            self.db.refresh(categorie)
            return categorie

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_categorie(self, categorie_id: int) -> "models.Categorie":
        try:
            categorie = self.db.query(models.Categorie).filter(
                models.Categorie.id_categorie == categorie_id
            ).first()
            if not categorie:
                logger.warning(f"Category not found with ID: {categorie_id}")
                raise HTTPException(status_code=404, detail="Category not found")
            return categorie

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_all_categories(self, skip: int = 0, limit: int = 100) -> list["models.Categorie"]:
        try:
            categories = self.db.query(models.Categorie).offset(skip).limit(limit).all()
            return categories

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def delete_categorie(self, categorie_id: int) -> "models.Categorie":
        try:
            categorie = self.get_categorie(categorie_id)
            self.db.delete(categorie)
            self.db.commit()
            logger.info(f"Deleted category with ID: {categorie_id}")
            return categorie

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")


class EquipementOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_equipement(self, equipement_data: dict, detail_data: dict = None) -> "models.Equipement":
        try:
            numero_serie = equipement_data.get("numero_serie")
            if not numero_serie:
                raise HTTPException(status_code=400, detail="Serial number is required")

            # Recherche de l'équipement existant
            existing_equipement = self.db.query(models.Equipement).filter(
                models.Equipement.numero_serie == numero_serie
            ).first()

            if existing_equipement:
                # Mise à jour de l'équipement existant
                for key, value in equipement_data.items():
                    if hasattr(existing_equipement, key) and value is not None:
                        setattr(existing_equipement, key, value)
                equipement = existing_equipement
                logger.info(f"Updated equipment with serial number: {numero_serie}")

                # Mise à jour des détails si fournis
                if detail_data:
                    existing_detail = self.db.query(models.DetailEquipement).filter(
                        models.DetailEquipement.id_equipement == equipement.id_equipement
                    ).first()

                    if existing_detail:
                        for key, value in detail_data.items():
                            if hasattr(existing_detail, key) and value is not None:
                                setattr(existing_detail, key, value)
                    else:
                        detail_data["id_equipement"] = equipement.id_equipement
                        detail = models.DetailEquipement(**detail_data)
                        self.db.add(detail)
            else:
                # Création d'un nouvel équipement
                equipement = models.Equipement(**equipement_data)
                self.db.add(equipement)
                self.db.commit()
                self.db.refresh(equipement)
                logger.info(f"Created new equipment with serial number: {numero_serie}")

                # Création des détails si fournis
                if detail_data:
                    detail_data["id_equipement"] = equipement.id_equipement
                    detail = models.DetailEquipement(**detail_data)
                    self.db.add(detail)
                    logger.info(f"Created new equipment detail with equipment ID: {equipement.id_equipement}")

            self.db.commit()
            self.db.refresh(equipement)
            return equipement

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_equipement_with_details(self, equipement_id: int) -> dict:
        try:
            equipement = self.db.query(models.Equipement).filter(
                models.Equipement.id_equipement == equipement_id
            ).first()
            if not equipement:
                logger.warning(f"Equipment not found with ID: {equipement_id}")
                raise HTTPException(status_code=404, detail="Equipment not found")

            detail = self.db.query(models.DetailEquipement).filter(
                models.DetailEquipement.id_equipement == equipement_id
            ).first()

            return {
                "equipement": equipement,
                "details": detail
            }

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
            # Suppression des détails associés
            detail = self.db.query(models.DetailEquipement).filter(
                models.DetailEquipement.id_equipement == equipement_id
            ).first()
            if detail:
                self.db.delete(detail)

            # Suppression de l'équipement
            equipement = self.get_equipement_with_details(equipement_id)["equipement"]
            self.db.delete(equipement)
            
            self.db.commit()
            logger.info(f"Deleted equipment with ID: {equipement_id}")
            return equipement

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

class DetailEquipementOperations:
    def __init__(self, db: Session):
        self.db = db

    def create_or_update_detail(self, detail_data: dict) -> "models.DetailEquipement":
        try:
            id_equipement = detail_data.get("id_equipement")
            if not id_equipement:
                raise HTTPException(status_code=400, detail="Equipment ID is required")

            existing_detail = self.db.query(models.DetailEquipement).filter(
                models.DetailEquipement.id_equipement == id_equipement
            ).first()

            if existing_detail:
                for key, value in detail_data.items():
                    if hasattr(existing_detail, key) and value is not None:
                        setattr(existing_detail, key, value)
                detail = existing_detail
                logger.info(f"Updated equipment detail with equipment ID: {id_equipement}")
            else:
                detail = models.DetailEquipement(**detail_data)
                self.db.add(detail)
                logger.info(f"Created new equipment detail with equipment ID: {id_equipement}")

            self.db.commit()
            self.db.refresh(detail)
            return detail

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def get_detail(self, detail_id: int) -> "models.DetailEquipement":
        try:
            detail = self.db.query(models.DetailEquipement).filter(
                models.DetailEquipement.id_detail == detail_id
            ).first()
            if not detail:
                logger.warning(f"Equipment detail not found with ID: {detail_id}")
                raise HTTPException(status_code=404, detail="Equipment detail not found")
            return detail

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")

    def delete_detail(self, detail_id: int) -> "models.DetailEquipement":
        try:
            detail = self.get_detail(detail_id)
            self.db.delete(detail)
            self.db.commit()
            logger.info(f"Deleted equipment detail with ID: {detail_id}")
            return detail

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")