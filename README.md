# 🗼 Network Coverage Project

Application web pour vérifier la couverture réseau mobile en France. Recherche d'adresse (API gouvernementale) et affichage de la couverture 2G/3G/4G pour Orange, SFR, Bouygues et Free.

---

## 📋 Vue d'ensemble

- **Backend** : FastAPI (Python, async, REST)
- **Frontend** : Angular 20 avec signals, Playwright pour E2E
- **Données** : Fichier CSV (antennes, techno/réseau)
- **Géocodage** : API Adresse gouvernementale (data.gouv.fr)

---

## 🐍 Backend (Python/FastAPI)

### Prérequis

- Python 3.8+
- pip ou conda

### Installation

```bash
git clone https://github.com/Callypige/network-coverage-project.git
cd network-coverage-project/backend

# Créer un venv
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Windows CMD
.\venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

**Dépendances principales :**  
- fastapi, uvicorn[standard], polars, aiohttp, pyproj, pydantic, pytest, pytest-asyncio, httpx

### Lancement

```bash
# Mode développement (rechargement auto)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ou directement (non recommandé)
python main.py
```

### Vérification API

- **Docs OpenAPI** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health
- **Test de base** : http://localhost:8000/

---

## 🅰️ Frontend (Angular)

### Prérequis

- Node.js 18+
- npm ou yarn
- Angular CLI 20+

### Installation

```bash
cd ../frontend
npm install
```

### Dépendances principales

```json
{
  "@angular/core": "^20.1.0",
  "@angular/common": "^20.1.0",
  "@angular/forms": "^20.1.0",
  "@angular/platform-browser": "^20.1.0",
  "@angular/router": "^20.1.0",
  "@playwright/test": "^1.54.2",
  "rxjs": "~7.8.0",
  "tslib": "^2.3.0",
  "zone.js": "~0.15.0"
}
```

### Configuration de l'API

Dans `src/app/coverage.service.ts`, vérifier l’URL :

```typescript
export class CoverageService {
  private apiUrl = 'http://localhost:8000'; // ✅ URL du backend
}
```

### Lancement du serveur de dev

```bash
ng serve
# ou
npm start
```

---

### ▶️ Utiliser l'application

1. Ouvrir http://localhost:4200
2. Taper une adresse (ex: "157 boulevard Mac Donald 75019 Paris")
3. Sélectionner une suggestion
4. Cliquer sur "Vérifier la couverture"
5. Résultats par opérateur & techno affichés

---

## 📡 API Endpoints

### `POST /coverage`
Vérifie la couverture pour une ou plusieurs adresses.

**Request :**
```json
{
  "id1": "157 boulevard Mac Donald 75019 Paris"
}
```

**Response :**
```json
{
  "id1": {
    "orange": {"2G": true, "3G": true, "4G": false},
    "SFR": {"2G": true, "3G": false, "4G": true},
    "bouygues": {"2G": false, "3G": true, "4G": true},
    "Free": {"2G": false, "3G": false, "4G": true}
  }
}
```

### `GET /health`
Vérifie l’état de l’API et la disponibilité des données.

### `GET /`
Informations générales sur l’API.

---

## 🧪 Tests & Debug

### Lancer les tests backend

```bash
pytest tests -v
```

### Tester l’API manuellement

```bash
curl -X POST "http://localhost:8000/coverage" \
  -H "Content-Type: application/json" \
  -d '{"id1": "157 boulevard Mac Donald 75019 Paris"}'

curl http://localhost:8000/health
```

### Géocodage qui échoue

- Vérifier la connexion internet
- Tester directement : https://api-adresse.data.gouv.fr/search/?q=Paris&limit=1

---

## 🧑‍💻 Développement & Tests Frontend

- **Unitaires :** `npm test`
- **E2E (Playwright) :** `npm run e2e`

## 👨‍💻 Auteur

**Callypige** - [GitHub](https://github.com/Callypige)
