"""
Moteur IA avec Mistral pour SYFL AI
"""
from mistralai import Mistral
from loguru import logger
from typing import List, Dict, Optional
import json


class AIEngine:
    """Moteur IA pour détecter les cas juridiques et générer des réponses"""
    
    def __init__(self, api_key: str, model: str = "mistral-small-latest"):
        """
        Initialise le moteur IA
        
        Args:
            api_key: Clé API Mistral
            model: Modèle à utiliser
        """
        self.client = Mistral(api_key=api_key)
        self.model = model
        self.knowledge_base = {}
        logger.info(f"AIEngine initialisé avec {model}")
    
    def load_knowledge_base(self, cases: Dict[str, Dict]):
        """Charge la base de connaissances des cas juridiques"""
        self.knowledge_base = cases
        logger.info(f"Base de connaissances chargée: {len(cases)} cas")
    
    def detect_case(self, user_message: str) -> Optional[str]:
        """
        Détecte le type de cas juridique depuis le message
        
        Args:
            user_message: Message de l'utilisateur
            
        Returns:
            ID du cas détecté ou None
        """
        if not self.knowledge_base:
            return None
        
        # Créer une liste des cas disponibles
        cases_list = "\n".join([
            f"- {case_id}: {data.get('titre', '')}"
            for case_id, data in self.knowledge_base.items()
        ])
        
        prompt = f"""Tu es un expert en droit du travail togolais. Analyse le message de l'utilisateur et identifie quel cas juridique correspond le mieux.

CAS DISPONIBLES:
{cases_list}

MESSAGE UTILISATEUR: "{user_message}"

Réponds UNIQUEMENT avec l'ID du cas (ex: licenciement_abusif), ou "aucun" si aucun cas ne correspond clairement.
Pas d'explication, juste l'ID."""
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=50
            )
            
            detected_id = response.choices[0].message.content.strip().lower()
            
            # Vérifier que l'ID existe
            if detected_id in self.knowledge_base:
                logger.info(f"Cas détecté: {detected_id}")
                return detected_id
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur détection cas: {e}")
            return None
    
    def generate_response(
        self,
        user_message: str,
        case_id: Optional[str] = None,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Génère une réponse à partir du message utilisateur
        
        Args:
            user_message: Message de l'utilisateur
            case_id: ID du cas juridique détecté (optionnel)
            conversation_history: Historique de conversation (optionnel)
            
        Returns:
            Réponse générée par l'IA
        """
        # Construire le contexte
        system_prompt = """Tu es SYFL AI, un assistant juridique spécialisé en droit du travail togolais.
Tu es empathique, professionnel et tu donnes des conseils pratiques et clairs.

RÈGLES:
1. Sois clair et accessible (pas de jargon inutile)
2. Structure tes réponses (points, étapes)
3. Cite les articles du Code du travail togolais quand pertinent
4. Propose des actions concrètes
5. Reste dans le cadre du droit du travail togolais"""
        
        # Ajouter les informations du cas si disponible
        if case_id and case_id in self.knowledge_base:
            case_data = self.knowledge_base[case_id]
            system_prompt += f"\n\nCAS IDENTIFIÉ: {case_data.get('titre', '')}\n"
            system_prompt += f"INFORMATIONS: {json.dumps(case_data, ensure_ascii=False, indent=2)}"
        
        # Construire les messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Ajouter l'historique si disponible
        if conversation_history:
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Ajouter le message actuel
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur génération réponse: {e}")
            return "Désolé, je rencontre un problème technique. Pouvez-vous reformuler votre question ?"
