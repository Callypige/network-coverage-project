# 🗼 Network Coverage Project

Application web pour vérifier la couverture réseau mobile en France. Recherche d'adresse via l'API gouvernementale et affichage de la couverture 2G/3G/4G pour Orange, SFR, Bouygues et Free.

## 📋 Vue d'ensemble

- **Backend** : FastAPI (Python, async, REST)
- **Frontend** : Angular 20 avec signals, Playwright pour E2E
- **Données** : Fichier CSV (antennes, technologie/réseau)
- **Géocodage** : API Adresse gouvernementale (data.gouv.fr)

## 🚀 Démarrage rapide

### 1. Backend (obligatoire)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou .\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
ng serve
```

### 3. Accès
- **Application** : http://localhost:4200
- **API docs** : http://localhost:8000/docs

## 🐍 Backend (Python/FastAPI)

### Prérequis
- Python 3.8+
- pip

### Installation détaillée

```bash
git clone https://github.com/Callypige/network-coverage-project.git
cd network-coverage-project/backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# Windows CMD
.\venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Dépendances principales
- `fastapi` - Framework web moderne
- `uvicorn[standard]` - Serveur ASGI
- `polars` - Manipulation de données performante
- `aiohttp` - Client HTTP asynchrone
- `pyproj` - Transformations géographiques
- `pydantic` - Validation de données
- `pytest` - Tests unitaires

### Lancement

```bash
# Mode développement (recommandé)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Alternative
python main.py
```

### Vérification
- **Documentation OpenAPI** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health
- **Accueil API** : http://localhost:8000/

## 🅰️ Frontend (Angular)

### Prérequis
- Node.js 18+
- npm
- Angular CLI 20+

### Installation

```bash
cd frontend
npm install
```

### Configuration
Vérifier l'URL de l'API dans `src/app/coverage.service.ts` :

```typescript
export class CoverageService {
  private apiUrl = 'http://localhost:8000'; // URL du backend
}
```

### Lancement

```bash
ng serve
# ou
npm start
```

L'application sera accessible sur http://localhost:4200

## 📱 Utilisation

1. **Ouvrir** http://localhost:4200
2. **Taper** une adresse (ex: "157 boulevard Mac Donald 75019 Paris")
3. **Sélectionner** une suggestion dans la liste
4. **Cliquer** sur "Vérifier la couverture"
5. **Consulter** les résultats par opérateur et technologie

## 📡 API Endpoints

### `POST /coverage`
Vérifie la couverture réseau pour une ou plusieurs adresses.

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
Vérifie l'état de l'API et la disponibilité des données.

### `GET /`
Informations générales sur l'API.

## 🧪 Tests

### Backend
```bash
cd backend
pytest tests -v
```

### Frontend
```bash
cd frontend

# Tests unitaires
npm test

# Tests E2E (nécessite que l'app tourne)
npm run e2e
```

**Détail des tests frontend :**
* **Unitaires :** `npm test`
* **E2E (Playwright) :** `npm run e2e`

### Test manuel de l'API
```bash
# Test de couverture
curl -X POST "http://localhost:8000/coverage" \
  -H "Content-Type: application/json" \
  -d '{"id1": "157 boulevard Mac Donald 75019 Paris"}'

# Health check
curl http://localhost:8000/health
```

## 🐛 Dépannage

### Le géocodage ne fonctionne pas
- Vérifier la connexion internet
- Tester directement l'API : https://api-adresse.data.gouv.fr/search/?q=Paris&limit=1

### CORS errors
- S'assurer que le backend tourne sur le port 8000
- Vérifier l'URL dans `coverage.service.ts`

### Tests Playwright qui échouent
- S'assurer que `ng serve` tourne sur le port 4200
- Vider le cache du navigateur

## 👨‍💻 Auteur

**Sophie / Callypige** - [GitHub](https://github.com/Callypige)
