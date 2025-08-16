# 🗼 Network Coverage Project

Une application webpour vérifier la couverture réseau mobile en France. L'application permet de rechercher une adresse et d'afficher la couverture 2G/3G/4G pour les opérateurs Orange, SFR, Bouygues et Free.

## 📋 Vue d'ensemble

- **Backend** : FastAPI (Python) pour l'API REST
- **Frontend** : Angular version 20 avec signals
- **Données** : Fichier CSV avec les mesures de couverture réseau
- **Géocodage** : API Adresse du gouvernement français

## 🐍 Configuration du Backend

### Prérequis

- Python 3.8+
- pip ou conda

### Installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/Callypige/network-coverage-project.git
   cd network-coverage-project
   ```

2. **Naviguer vers le backend**
   ```bash
   cd backend
   ```

3. **Créer un environnement virtuel**
   ```bash
   # Avec venv
   python -m venv venv
   
   # Activer l'environnement
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   # Windows CMD
   .\venv\Scripts\activate.bat
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```
### Lancement du serveur

```bash
# Mode développement avec rechargement automatique
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ou directement
python main.py
```

### Vérification

- **API Documentation** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health
- **Test de base** : http://localhost:8000/


## 🅰️ Configuration du Frontend

### Prérequis

- Node.js 18+
- npm ou yarn
- Angular CLI 17+

### Installation

1. **Naviguer vers le frontend**
   ```bash
   cd frontend
   ```

2. **Installer Angular CLI (si pas déjà installé)**
   ```bash
   npm install -g @angular/cli@17
   ```

3. **Installer les dépendances**
   ```bash
   npm install
   ```

### Dépendances principales

```json
{
  "@angular/core": "^17.0.0",
  "@angular/common": "^17.0.0",
  "@angular/forms": "^17.0.0",
  "@angular/platform-browser": "^17.0.0",
  "rxjs": "~7.8.0",
  "typescript": "~5.2.0"
}
```

### Configuration de l'API

Dans `src/app/coverage.service.ts`, vérifier l'URL de l'API :

```typescript
export class CoverageService {
  private apiUrl = 'http://localhost:8000'; // ✅ URL du backend
}
```

### Lancement du serveur de développement

```bash
# Serveur de développement
ng serve ou npm start



### 3. Utiliser l'application
1. Ouvrir http://localhost:4200
2. Taper une adresse (ex: "157 boulevard Mac Donald 75019 Paris")
3. Sélectionner dans les suggestions
4. Cliquer sur "Vérifier la couverture"
5. Voir les résultats par opérateur et technologie

---

## 📡 API Endpoints

### `POST /coverage`
Vérifier la couverture pour une ou plusieurs adresses.

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
Vérifier l'état de l'API et des données.

### `GET /`
Information générale sur l'API.

---

## 🧪 Tests et Debug

### Tester l'API directement

Lancer les tests côté backend :
```bash
pytest tests -v                                                           
```

Test avec curl :
```bash
curl -X POST "http://localhost:8000/coverage" \
  -H "Content-Type: application/json" \
  -d '{"id1": "157 boulevard Mac Donald 75019 Paris"}'

# Test de santé
curl http://localhost:8000/health
```

### Géocodage qui échoue
- Vérifier la connectivité internet
- Tester l'API gouv.fr directement : https://api-adresse.data.gouv.fr/search/?q=Paris&limit=1


## 📄 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

**Callypige** - [GitHub](https://github.com/Callypige)
