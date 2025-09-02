# 🗼 Network Coverage Project

Application web pour vérifier la couverture réseau mobile en France.

## 🚀 Démarrage rapide

### Docker (Recommandé)
```bash
git clone https://github.com/Callypige/network-coverage-project.git
cd network-coverage-project
docker-compose up --build
```

### Installation manuelle
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (nouveau terminal)
cd frontend
npm install && ng serve
```

**Accès :** http://localhost:4200 | **API :** http://localhost:8000/docs

## 📋 Stack technique

- **Backend** : FastAPI, Polars, Python 3.11+
- **Frontend** : Angular 20, Node.js 20+
- **Docker** : Multi-stage builds, nginx

## 📡 API

```bash
# Test rapide
curl -X POST "http://localhost:8000/coverage" \
  -H "Content-Type: application/json" \
  -d '{"addr1": "157 boulevard Mac Donald 75019 Paris"}'
```

## 🧪 Tests

```bash
# Backend
cd backend && pytest

# Frontend  
cd frontend && npm test && npm run e2e
```

## 🐛 Dépannage

- **Docker virtualization error** → Activer dans BIOS + WSL2
- **Port 4200/8000 occupé** → `docker-compose down`
- **CORS errors** → Vérifier que backend tourne sur :8000

**Auteur :** Sophie / Callypige
