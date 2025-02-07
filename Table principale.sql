-- Table principale des catégories de matériel
CREATE TABLE Categories (
    id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_categorie VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Table générique pour tous les équipements
CREATE TABLE Equipement (
    id_equipement INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categorie INTEGER,
    numero_serie VARCHAR(100),
    marque VARCHAR(100),
    modele VARCHAR(100),
    date_achat DATE,
    date_mise_en_service DATE,
    statut VARCHAR(50), -- En service, Réformé, En réparation
    localisation VARCHAR(100),
    prix DECIMAL(10,2),
    fournisseur VARCHAR(100),
    garantie_expire DATE,
    commentaires TEXT,
    FOREIGN KEY (id_categorie) REFERENCES Categories(id_categorie)
);

-- Table des détails spécifiques par type d'équipement
CREATE TABLE DetailEquipement (
    id_detail INTEGER PRIMARY KEY AUTOINCREMENT,
    id_equipement INTEGER UNIQUE,
    type_connexion VARCHAR(50), -- USB-C, Lightning, etc.
    puissance_watts DECIMAL(5,2),
    longueur_cable DECIMAL(5,2),
    couleur VARCHAR(50),
    compatibilite TEXT,
    caracteristiques_specifiques TEXT,
    FOREIGN KEY (id_equipement) REFERENCES Equipement(id_equipement)
);