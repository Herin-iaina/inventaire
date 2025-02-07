from fastapi import FastAPI, Depends, Query, HTTPException
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from . import mac_operations, screen_operation, materiel_operation
from .database import get_db
from .models import MacItem, MacItemCreate, MacItemUpdate, EcranItems, EcranCreate, EcranUpdate
from . import schemas

app = FastAPI(title="MAC and Screen Inventory API")

# MAC endpoints
@app.post("/mac-items/", response_model=MacItem)
def create_mac_item(mac_item: MacItemCreate, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    return ops.create_or_update_mac_item(mac_item.dict())

@app.get("/mac-items/search", response_model=List[MacItem])  # Removed trailing slash
def search_mac_items(
    numero_serie: Optional[str] = None,
    modele: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ops = mac_operations.MacOperations(db)
    return ops.search_mac_items(numero_serie, modele, statut)

@app.get("/mac-items/", response_model=List[MacItem])
def read_mac_items(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=100),  # Added ge=1 for validation
    db: Session = Depends(get_db)
):
    ops = mac_operations.MacOperations(db)
    return ops.list_mac_items(skip, limit)

@app.get("/mac-items/{item_id}", response_model=MacItem)
def read_mac_item(item_id: int, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    return ops.get_mac_item(item_id)

@app.put("/mac-items/{item_id}", response_model=MacItem)
def update_mac_item(item_id: int, mac_item: MacItemUpdate, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    mac_item_dict = mac_item.dict(exclude_unset=True)
    mac_item_dict["id_mac"] = item_id
    return ops.create_or_update_mac_item(mac_item_dict)

@app.delete("/mac-items/{item_id}")
def delete_mac_item(item_id: int, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    ops.delete_mac_item(item_id)
    return {"message": "Item deleted successfully"}

# Screen endpoints
@app.post("/ecran-items/", response_model=EcranItems)
def create_ecran_item(ecran_item: EcranCreate, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    return ops.create_or_update_ecran_item(ecran_item.dict())

@app.get("/ecran-items/search", response_model=List[EcranItems])  # Removed trailing slash
def search_ecran_items(
    numero_serie: Optional[str] = None,
    modele: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ops = screen_operation.ScreenOperations(db)
    return ops.search_ecran_items(numero_serie, modele, statut)

@app.get("/ecran-items/", response_model=List[EcranItems])
def read_ecran_items(
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=100),  # Added ge=1 for validation
    db: Session = Depends(get_db)
):
    ops = screen_operation.ScreenOperations(db)
    return ops.list_ecran_items(skip, limit)

@app.get("/ecran-items/{item_id}", response_model=EcranItems)
def read_ecran_item(item_id: int, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    return ops.get_ecran_item(item_id)

@app.put("/ecran-items/{item_id}", response_model=EcranItems)
def update_ecran_item(item_id: int, ecran_item: EcranUpdate, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    ecran_item_dict = ecran_item.dict(exclude_unset=True)
    ecran_item_dict["id_ecran"] = item_id
    return ops.create_or_update_ecran_item(ecran_item_dict)

@app.delete("/ecran-items/{item_id}")
def delete_ecran_item(item_id: int, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    ops.delete_ecran_item(item_id)
    return {"message": "Screen deleted successfully"}

# Endpoints pour Categorie
@app.post("/categories/", response_model=schemas.Categorie)
def create_categorie_endpoint(categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    return materiel_operation.create_categorie(db=db, categorie=categorie)

@app.get("/categories/", response_model=List[schemas.Categorie])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = materiel_operation.get_categories(db, skip=skip, limit=limit)
    return categories

@app.get("/categories/{categorie_id}", response_model=schemas.Categorie)
def read_categorie(categorie_id: int, db: Session = Depends(get_db)):
    db_categorie = materiel_operation.get_categorie(db, categorie_id=categorie_id)
    if db_categorie is None:
        raise HTTPException(status_code=404, detail="Categorie not found")
    return db_categorie

@app.put("/categories/{categorie_id}", response_model=schemas.Categorie)
def update_categorie_endpoint(categorie_id: int, categorie: schemas.CategorieCreate, db: Session = Depends(get_db)):
    return materiel_operation.update_categorie(db=db, categorie_id=categorie_id, categorie=categorie)

@app.delete("/categories/{categorie_id}", response_model=schemas.Categorie)
def delete_categorie_endpoint(categorie_id: int, db: Session = Depends(get_db)):
    return materiel_operation.delete_categorie(db=db, categorie_id=categorie_id)

# Endpoints pour Equipement
@app.post("/equipements/", response_model=schemas.Equipement)
def create_or_update_equipement(
    equipement_data: Dict,
    detail_data: Optional[Dict] = None,
    db: Session = Depends(get_db)
):
    """
    Créer ou mettre à jour un équipement avec ses détails optionnels
    """
    try:
        operations = materiel_operation.EquipementOperations(db)
        equipement = operations.create_or_update_equipement(
            equipement_data, 
            detail_data
        )
        return equipement
    except HTTPException as e:
        raise e

@app.get("/equipements/", response_model=List[schemas.Equipement])
def list_equipements(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupérer la liste des équipements
    """
    operations = materiel_operation.EquipementOperations(db)
    return operations.get_all_equipements(skip, limit)

@app.get("/equipements/{equipement_id}")
def get_equipement_details(
    equipement_id: int, 
    db: Session = Depends(get_db)
):
    """
    Récupérer les détails d'un équipement spécifique
    """
    operations = materiel_operation.EquipementOperations(db)
    return operations.get_equipement_with_details(equipement_id)

@app.delete("/equipements/{equipement_id}", response_model=schemas.Equipement)
def delete_equipement(
    equipement_id: int, 
    db: Session = Depends(get_db)
):
    """
    Supprimer un équipement et ses détails associés
    """
    operations = materiel_operation.EquipementOperations(db)
    return operations.delete_equipement(equipement_id)


# Endpoints pour DetailEquipement
@app.post("/details/", response_model=schemas.DetailEquipement)
def create_detail_endpoint(detail: schemas.DetailEquipementCreate, db: Session = Depends(get_db)):
    return materiel_operation.create_detail_equipement(db=db, detail=detail)

@app.get("/details/{detail_id}", response_model=schemas.DetailEquipement)
def read_detail(detail_id: int, db: Session = Depends(get_db)):
    db_detail = materiel_operation.get_detail_equipement(db, detail_id=detail_id)
    if db_detail is None:
        raise HTTPException(status_code=404, detail="Detail not found")
    return db_detail

@app.put("/details/{detail_id}", response_model=schemas.DetailEquipement)
def update_detail_endpoint(detail_id: int, detail: schemas.DetailEquipementCreate, db: Session = Depends(get_db)):
    return materiel_operation.update_detail_equipement(db=db, detail_id=detail_id, detail=detail)

@app.delete("/details/{detail_id}", response_model=schemas.DetailEquipement)
def delete_detail_endpoint(detail_id: int, db: Session = Depends(get_db)):
    return materiel_operation.delete_detail_equipement(db=db, detail_id=detail_id)