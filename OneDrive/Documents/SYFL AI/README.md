# SYFL AI - Assistant Juridique Togolais

Assistant juridique intelligent spécialisé en droit du travail togolais, avec intelligence artificielle (Mistral AI).

## 🚀 Architecture

### Backend (FastAPI)
- **Base de données**: SQLite + SQLAlchemy
- **Authentification**: JWT avec pbkdf2_sha256
- **IA**: Mistral AI (mistral-small-latest)
- **API**: REST avec documentation automatique

### Structure du projet

```
SYFL AI/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Configuration SQLAlchemy
│   ├── models.py            # Modèles de données
│   ├── schemas.py           # Schémas Pydantic
│   ├── auth.py              # Authentification JWT
│   ├── ai_engine.py         # Moteur IA Mistral
│   └── routes/
│       ├── auth.py          # Routes authentification
│       └── chat.py          # Routes chat/conversations
├── bases_connaissances/     # Cas juridiques (JSON)
├── test.py                  # Script de test complet
├── .env                     # Variables d'environnement
└── requirements.txt         # Dépendances Python
```

## 📋 Prérequis

- Python 3.11+
- Compte Mistral AI (clé API gratuite)

## 🔧 Installation

### 1. Cloner le projet

```bash
cd "C:\Users\DELL\OneDrive\Documents\SYFL AI"
```

### 2. Créer l'environnement virtuel

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` :

```env
# Clé API Mistral AI (gratuit : 1M tokens/mois)
MISTRAL_API_KEY=votre_cle_api_mistral

# Clé secrète JWT (générer une clé aléatoire longue)
SECRET_KEY=votre_cle_secrete_jwt_tres_longue_et_aleatoire

# Base de données (SQLite par défaut)
DATABASE_URL=sqlite:///./syfl_ai.db
```

### 5. Obtenir une clé API Mistral

1. Aller sur https://console.mistral.ai/
2. Créer un compte (gratuit)
3. Générer une clé API
4. Copier la clé dans `.env`

## 🚀 Démarrage

### Démarrer le backend

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Le serveur démarre sur : **http://127.0.0.1:8000**

### Documentation API

- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## 🧪 Tests

Exécuter les tests complets :

```powershell
python test.py
```

Tests inclus :
- ✅ Santé de l'API
- ✅ Inscription utilisateur
- ✅ Connexion utilisateur
- ✅ Profil utilisateur
- ✅ Chat avec IA (détection de cas)
- ✅ Historique des conversations

## 📡 API Endpoints

### Authentification

```
POST /api/auth/register    # Inscription
POST /api/auth/login       # Connexion
GET  /api/auth/me          # Profil utilisateur
```

### Chat

```
POST   /api/chat/send                      # Envoyer un message
GET    /api/chat/conversations             # Liste des conversations
GET    /api/chat/conversations/{id}        # Détails d'une conversation
DELETE /api/chat/conversations/{id}        # Supprimer une conversation
```

### Santé

```
GET /health    # Vérification de santé
GET /          # Informations API
```

## 💾 Base de données

### Modèles

- **User** : Utilisateurs (email, username, mot de passe)
- **Conversation** : Conversations (titre, type de cas)
- **Message** : Messages (user/assistant, contenu)
- **Case** : Cas juridiques de référence

### Migrations

Les tables sont créées automatiquement au démarrage.

Pour réinitialiser la base :

```powershell
Remove-Item syfl_ai.db
# Redémarrer le serveur
```

## 🤖 Intelligence Artificielle

### Mistral AI

- **Modèle** : mistral-small-latest
- **Fonction** : 
  - Détection automatique du type de cas juridique
  - Génération de réponses contextuelles
  - Conseils juridiques en droit togolais

### Base de connaissances

10 cas juridiques togolais :
1. Absence de contrat écrit
2. Contrat à durée déterminée abusif
3. Harcèlement au travail
4. Heures supplémentaires non payées
5. Licenciement abusif
6. Licenciement sans préavis
7. Non-remise du certificat de travail
8. Période d'essai abusive
9. Salaire impayé
10. Travail forcé

## 🔐 Sécurité

- Mots de passe hashés avec **pbkdf2_sha256**
- Authentification par **JWT** (tokens)
- Tokens valides 7 jours
- CORS configuré pour dev (localhost)

## 📦 Dépendances principales

```
fastapi==0.115.0
uvicorn==0.25.0
sqlalchemy==2.0.45
mistralai==1.2.4
python-jose[cryptography]==3.3.0
passlib==1.7.4
pydantic==2.10.3
python-dotenv==1.0.1
loguru==0.7.3
```

## 🎯 Prochaines étapes

### Frontend Web (Next.js)
- Interface utilisateur moderne
- Chat en temps réel
- Gestion des conversations
- Authentification

### Frontend Mobile (React Native + Expo)
- Application iOS/Android
- Même API backend
- Push notifications
- Mode hors-ligne

## 📝 Licence

Projet privé - SYFL AI © 2025

## 🆘 Support

Pour toute question technique, consulter la documentation API : http://127.0.0.1:8000/docs
