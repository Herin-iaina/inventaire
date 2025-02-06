from fastapi import FastAPI, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from . import mac_operations
from . import screen_operation
from .database import get_db
from .models import MacItem, MacItemCreate, MacItemUpdate
from .models import EcranItems, EcranCreate, EcranUpdate

app = FastAPI(title="MAC Inventory API")

@app.post("/mac-items/", response_model=MacItem)
def create_mac_item(mac_item: MacItemCreate, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    return ops.create_or_update_mac_item(mac_item.dict())

@app.put("/mac-items/{item_id}", response_model=MacItem)
def update_mac_item(item_id: int, mac_item: MacItemUpdate, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    mac_item_dict = mac_item.dict(exclude_unset=True)
    mac_item_dict["id_mac"] = item_id
    return ops.create_or_update_mac_item(mac_item_dict)

@app.get("/mac-items/{item_id}", response_model=MacItem)
def read_mac_item(item_id: int, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    return ops.get_mac_item(item_id)

@app.get("/mac-items/", response_model=List[MacItem])
def read_mac_items(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db)
):
    ops = mac_operations.MacOperations(db)
    return ops.list_mac_items(skip, limit)

@app.delete("/mac-items/{item_id}")
def delete_mac_item(item_id: int, db: Session = Depends(get_db)):
    ops = mac_operations.MacOperations(db)
    ops.delete_mac_item(item_id)
    return {"message": "Item deleted successfully"}

@app.get("/mac-items/search/", response_model=List[MacItem])
def search_mac_items(
    numero_serie: Optional[str] = None,
    modele: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ops = mac_operations.MacOperations(db)
    return ops.search_mac_items(numero_serie, modele, statut)


#ercan

@app.post("/ecran-items/", response_model=EcranItems)
def create_ecran_item(ecran_item: EcranCreate, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    return ops.create_or_update_ecran_item(ecran_item.dict())

@app.put("/ecran-items/{item_id}", response_model=EcranItems)
def update_ecran_item(item_id: int, ecran_item: EcranUpdate, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    ecran_item_dict = ecran_item.dict(exclude_unset=True)
    ecran_item_dict["id_ecran"] = item_id
    return ops.create_or_update_ecran_item(ecran_item_dict)

@app.get("/ecran-items/{item_id}", response_model=EcranItems)
def read_ecran_item(item_id: int, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    return ops.get_ecran_item(item_id)

@app.get("/ecran-items/", response_model=List[EcranItems])
def read_ecran_items(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db)
):
    ops = screen_operation.ScreenOperations(db)
    return ops.list_ecran_items(skip, limit)

@app.delete("/ecran-items/{item_id}")
def delete_ecran_item(item_id: int, db: Session = Depends(get_db)):
    ops = screen_operation.ScreenOperations(db)
    ops.delete_ecran_item(item_id)
    return {"message": "Screen deleted successfully"}

@app.get("/ecran-items/search/", response_model=List[EcranItems])
def search_ecran_items(
    numero_serie: Optional[str] = None,
    modele: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ops = screen_operation.ScreenOperations(db)
    return ops.search_ecran_items(numero_serie, modele, statut)