# 🚀 Guide de Déploiement SYFL AI

## Backend sur Railway

### 1. Prérequis
- Compte GitHub (pour connecter le repo)
- Compte Railway : https://railway.app
- Compte Mistral AI (clé API)

### 2. Déploiement Backend

#### Option A : Via Interface Railway (Recommandé)

1. **Créer un projet Railway**
   - Aller sur https://railway.app/new
   - Cliquer sur "Deploy from GitHub repo"
   - Sélectionner le repository `PageWeb`
   - Railway détectera automatiquement le `Procfile`

2. **Ajouter PostgreSQL**
   - Dans le projet Railway, cliquer "New" → "Database" → "Add PostgreSQL"
   - Railway créera automatiquement la variable `DATABASE_URL`

3. **Configurer les variables d'environnement**
   ```
   MISTRAL_API_KEY=votre_cle_mistral_ici
   SECRET_KEY=votre_secret_jwt_ici (générer avec: openssl rand -hex 32)
   DATABASE_URL=postgresql://... (auto-créé par Railway)
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   ```

4. **Ajouter domaines CORS**
   - Une fois déployé, copier l'URL du backend (ex: https://syfl-ai.railway.app)
   - Mettre à jour `app/main.py` :
   ```python
   allow_origins=[
       "http://localhost:3000",
       "https://votre-frontend.vercel.app",  # À ajouter après déploiement Vercel
   ]
   ```

5. **Déployer**
   - Railway déploie automatiquement
   - Suivre les logs en temps réel
   - Tester : https://votre-app.railway.app/health

#### Option B : Via Railway CLI

```bash
# Installer Railway CLI
npm install -g @railway/cli

# Login
railway login

# Lier au projet
railway link

# Déployer
railway up

# Ajouter PostgreSQL
railway add postgresql

# Configurer variables
railway variables set MISTRAL_API_KEY=xxx
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Voir les logs
railway logs
```

### 3. Migration Base de Données

```bash
# Après premier déploiement, exécuter les migrations
railway run alembic upgrade head
```

---

## Frontend Web sur Vercel

### 1. Prérequis
- Compte Vercel : https://vercel.com
- Repository GitHub avec le code frontend

### 2. Déploiement

#### Via Interface Vercel (Recommandé)

1. **Importer le projet**
   - Aller sur https://vercel.com/new
   - Importer le repository GitHub
   - Sélectionner le dossier `syfl-web`
   - Framework preset : Next.js (détecté automatiquement)

2. **Configurer les variables d'environnement**
   ```
   NEXT_PUBLIC_API_URL=https://votre-backend.railway.app
   ```

3. **Déployer**
   - Cliquer "Deploy"
   - Vercel build et déploie automatiquement
   - URL : https://syfl-ai.vercel.app

#### Via Vercel CLI

```bash
cd syfl-web

# Installer Vercel CLI
npm install -g vercel

# Login
vercel login

# Déployer
vercel

# Production
vercel --prod

# Configurer variables
vercel env add NEXT_PUBLIC_API_URL
```

### 3. Mettre à jour le CORS Backend

Une fois le frontend déployé, ajouter son URL dans `app/main.py` :

```python
allow_origins=[
    "http://localhost:3000",
    "https://syfl-ai.vercel.app",  # URL Vercel
]
```

Puis redéployer le backend.

---

## Application Mobile avec Expo EAS

### 1. Prérequis
- Compte Expo : https://expo.dev
- Compte Apple Developer (pour iOS, 99$/an)
- Compte Google Play (pour Android, 25$ one-time)

### 2. Configuration

```bash
cd syfl-mobile

# Installer EAS CLI
npm install -g eas-cli

# Login
eas login

# Configurer le projet
eas build:configure
```

### 3. Mettre à jour l'URL de l'API

Modifier `lib/api.ts` :

```typescript
const API_BASE_URL = 'https://votre-backend.railway.app';
```

### 4. Build Android

```bash
# Build APK pour tests
eas build --platform android --profile preview

# Build AAB pour Google Play Store
eas build --platform android --profile production
```

### 5. Build iOS

```bash
# Build pour TestFlight
eas build --platform ios --profile preview

# Build pour App Store
eas build --platform ios --profile production
```

### 6. Submit aux stores

```bash
# Android
eas submit --platform android

# iOS
eas submit --platform ios
```

---

## Configuration PostgreSQL en Production

### Migration de SQLite vers PostgreSQL

1. **Mettre à jour `app/database.py`** (déjà compatible)

2. **Variables d'environnement**
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

3. **Exécuter migrations**
   ```bash
   alembic upgrade head
   ```

---

## Checklist de Déploiement

### Backend ✅
- [x] `requirements.txt` nettoyé
- [x] `Procfile` créé
- [x] `runtime.txt` spécifié (Python 3.13)
- [x] `railway.toml` configuré
- [ ] Variables d'environnement configurées sur Railway
- [ ] PostgreSQL ajouté
- [ ] CORS mis à jour avec URLs production
- [ ] Migrations exécutées
- [ ] Health check testé

### Frontend Web ✅
- [ ] Projet déployé sur Vercel
- [ ] `NEXT_PUBLIC_API_URL` configuré
- [ ] Build réussi
- [ ] Tests de connexion au backend

### Mobile 📱
- [ ] API URL mise à jour
- [ ] Build Android créé
- [ ] Build iOS créé (optionnel)
- [ ] Tests sur devices réels

---

## URLs de Production (À compléter)

| Service | URL | Status |
|---------|-----|--------|
| Backend API | https://_____.railway.app | ⏳ À déployer |
| Frontend Web | https://_____.vercel.app | ⏳ À déployer |
| Mobile Android | Google Play Store | ⏳ À soumettre |
| Mobile iOS | App Store | ⏳ À soumettre |

---

## Commandes Rapides

```bash
# Logs Backend (Railway)
railway logs

# Redéployer Backend
git push origin main  # Railway auto-deploy

# Redéployer Frontend
git push origin main  # Vercel auto-deploy

# Créer nouvelle migration
alembic revision --autogenerate -m "description"

# Appliquer migrations
railway run alembic upgrade head
```

---

## Monitoring et Maintenance

### Logs
- **Railway** : Dashboard → Logs
- **Vercel** : Dashboard → Logs

### Erreurs Communes

1. **500 Internal Server Error**
   - Vérifier les logs Railway
   - Vérifier variables d'environnement
   - Vérifier connexion PostgreSQL

2. **CORS Error**
   - Ajouter URL frontend dans `allow_origins`
   - Redéployer backend

3. **Database Error**
   - Exécuter migrations : `railway run alembic upgrade head`
   - Vérifier `DATABASE_URL`

### Support
- Railway : https://docs.railway.app
- Vercel : https://vercel.com/docs
- Expo : https://docs.expo.dev

---

## Sécurité en Production

✅ **Checklist Sécurité**
- [ ] `SECRET_KEY` généré avec `openssl rand -hex 32`
- [ ] `MISTRAL_API_KEY` non exposé dans le code
- [ ] HTTPS activé partout (automatique sur Railway/Vercel)
- [ ] Rate limiting activé (slowapi)
- [ ] Validation des entrées (Pydantic)
- [ ] Pas de secrets dans Git
- [ ] PostgreSQL avec SSL

---

## Budget Estimé

| Service | Plan | Prix |
|---------|------|------|
| Railway | Hobby | 5$/mois |
| Vercel | Hobby | Gratuit |
| Mistral AI | Free Tier | Gratuit (1M tokens/mois) |
| PostgreSQL | Inclus Railway | Inclus |
| **Total mensuel** | | **~5$/mois** |

Pour production à grande échelle, considérer les plans payants.

---

**Prochaines étapes :**
1. Créer compte Railway
2. Déployer le backend
3. Tester l'API en production
4. Déployer le frontend Vercel
5. Build mobile (optionnel)

Bon déploiement ! 🚀
