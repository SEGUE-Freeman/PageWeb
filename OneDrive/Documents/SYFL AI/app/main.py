"""
Application FastAPI principale
SYFL AI - Assistant juridique togolais
"""
import os
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routes import auth, chat
from app.ai_engine import AIEngine

# Charger les variables d'environnement
load_dotenv()

# Créer les tables
Base.metadata.create_all(bind=engine)
logger.info("✅ Base de données initialisée")

# Initialiser le rate limiter
limiter = Limiter(key_func=get_remote_address)

# Créer l'application FastAPI
app = FastAPI(
    title="SYFL AI API",
    description="API Backend pour SYFL AI - Assistant juridique togolais",
    version="1.0.0"
)

# Ajouter le rate limiter à l'app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:19006",  # Expo web
        "http://localhost:8081",  # Expo mobile
        "https://syfl-ai-frontend.vercel.app",  # Vercel production
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Tous les déploiements Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger la base de connaissances
knowledge_base = {}


def load_knowledge_base():
    """Charge les cas juridiques depuis les fichiers JSON"""
    global knowledge_base
    base_path = Path("bases_connaissances")
    
    if not base_path.exists():
        logger.warning("Dossier bases_connaissances introuvable")
        return
    
    for json_file in base_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                case_id = json_file.stem  # Nom du fichier sans extension
                knowledge_base[case_id] = data
                logger.info(f"Cas chargé: {data.get('titre', case_id)}")
        except Exception as e:
            logger.error(f"Erreur chargement {json_file}: {e}")
    
    logger.info(f"✅ {len(knowledge_base)} cas juridiques chargés")


# Initialiser l'AIEngine
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    logger.error("❌ MISTRAL_API_KEY non trouvée dans .env")
    raise ValueError("MISTRAL_API_KEY manquante")

ai_engine = AIEngine(api_key=MISTRAL_API_KEY)

# Configurer l'AIEngine pour le module chat
chat.set_ai_engine(ai_engine)


@app.on_event("startup")
def startup_event():
    """Événement de démarrage"""
    load_knowledge_base()
    ai_engine.load_knowledge_base(knowledge_base)
    logger.info("🚀 SYFL AI démarré avec succès")


# Inclure les routes
app.include_router(auth.router)
app.include_router(chat.router)

# Importer et inclure les nouvelles routes
from app.routes import export, stats
app.include_router(export.router)
app.include_router(stats.router)


@app.get("/")
def root():
    """Route racine"""
    return {
        "message": "Bienvenue sur SYFL AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "database": "connected",
        "knowledge_base_loaded": len(knowledge_base) > 0,
        "cases_count": len(knowledge_base),
        "mistral_configured": MISTRAL_API_KEY is not None
    }
