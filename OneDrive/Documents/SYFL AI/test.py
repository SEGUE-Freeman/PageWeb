"""
Script de test complet pour SYFL AI Backend
Teste: inscription, connexion, chat avec IA
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """Affiche un titre de section"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test 1: Santé de l'API"""
    print_section("TEST 1: Santé de l'API")
    
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
        
        if r.status_code == 200:
            print("✅ API en ligne")
            return True
        else:
            print("❌ Problème avec l'API")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_register_and_login():
    """Test 2: Inscription et connexion"""
    print_section("TEST 2: Inscription et Connexion")
    
    timestamp = int(time.time())
    user_data = {
        "email": f"test{timestamp}@syflai.com",
        "username": f"user{timestamp}",
        "password": "Test123!",
        "full_name": "Utilisateur Test"
    }
    
    # Inscription
    print("Inscription...")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 201:
            data = r.json()
            token = data["access_token"]
            print(f"✅ Inscription réussie")
            print(f"Token: {token[:50]}...")
            return token, user_data["email"]
        else:
            print(f"❌ Erreur: {r.text}")
            return None, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None, None

def test_get_me(token):
    """Test 3: Récupération du profil utilisateur"""
    print_section("TEST 3: Profil Utilisateur")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ Profil récupéré")
            return True
        else:
            print(f"❌ Erreur: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_chat(token):
    """Test 4: Chat avec l'IA"""
    print_section("TEST 4: Chat avec l'IA")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Premier message - détection de cas
    print("📨 Message 1: 'J'ai été licencié sans préavis'")
    message1 = {
        "message": "Bonjour, j'ai été licencié sans préavis par mon employeur"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/chat/send", json=message1, headers=headers)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"\n🤖 Réponse IA:")
            print(f"{data['message'][:300]}...")
            print(f"\nCas détecté: {data.get('case_detected')}")
            print(f"Conversation ID: {data['conversation_id']}")
            print("✅ Premier message réussi")
            
            conversation_id = data['conversation_id']
            
            # Deuxième message - suivi de conversation
            print("\n📨 Message 2: 'Quelles sont mes options?'")
            message2 = {
                "message": "Quelles sont mes options et mes droits?",
                "conversation_id": conversation_id
            }
            
            r2 = requests.post(f"{BASE_URL}/api/chat/send", json=message2, headers=headers)
            print(f"Status: {r2.status_code}")
            
            if r2.status_code == 200:
                data2 = r2.json()
                print(f"\n🤖 Réponse IA:")
                print(f"{data2['message'][:300]}...")
                print("✅ Suivi de conversation réussi")
                return True
            else:
                print(f"❌ Erreur message 2: {r2.text}")
                return False
        else:
            print(f"❌ Erreur message 1: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversations(token):
    """Test 5: Liste des conversations"""
    print_section("TEST 5: Liste des Conversations")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/api/chat/conversations", headers=headers)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Nombre de conversations: {len(data)}")
            
            if data:
                print(f"\nPremière conversation:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            
            print("✅ Liste des conversations récupérée")
            return True, data[0]['id'] if data else None
        else:
            print(f"❌ Erreur: {r.text}")
            return False, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def test_stats(token):
    """Test 6: Statistiques utilisateur"""
    print_section("TEST 6: Statistiques Utilisateur")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.get(f"{BASE_URL}/api/stats", headers=headers)
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ Statistiques récupérées")
            return True
        else:
            print(f"❌ Erreur: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_cases():
    """Test 7: Liste des cas juridiques"""
    print_section("TEST 7: Liste des Cas Juridiques")
    
    try:
        r = requests.get(f"{BASE_URL}/api/chat/cases")
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Nombre de cas: {data['total']}")
            
            if data['cases']:
                print(f"\nPremier cas:")
                first_case = data['cases'][0]
                print(f"ID: {first_case['id']}")
                print(f"Titre: {first_case['titre']}")
                print(f"Type: {first_case['type']}")
            
            print("✅ Liste des cas récupérée")
            return True
        else:
            print(f"❌ Erreur: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_export_pdf(token, conversation_id):
    """Test 8: Export PDF d'une conversation"""
    print_section("TEST 8: Export PDF")
    
    if not conversation_id:
        print("⚠️  Pas de conversation à exporter")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        r = requests.get(
            f"{BASE_URL}/api/export/conversation/{conversation_id}/pdf",
            headers=headers
        )
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            # Vérifier que c'est bien un PDF
            content_type = r.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            
            if 'application/pdf' in content_type:
                pdf_size = len(r.content)
                print(f"Taille du PDF: {pdf_size} bytes")
                
                # Sauvegarder le PDF pour vérification
                with open("test_export.pdf", "wb") as f:
                    f.write(r.content)
                print("PDF sauvegardé: test_export.pdf")
                
                print("✅ Export PDF réussi")
                return True
            else:
                print(f"❌ Type de contenu invalide: {content_type}")
                return False
        else:
            print(f"❌ Erreur: {r.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("  🧪 TESTS COMPLETS SYFL AI BACKEND")
    print("="*60)
    
    results = []
    
    # Test 1: Santé
    results.append(("Santé API", test_health()))
    
    # Test 2: Inscription et connexion
    token, email = test_register_and_login()
    results.append(("Inscription/Connexion", token is not None))
    
    if not token:
        print("\n❌ Tests arrêtés: impossible de s'authentifier")
        return
    
    # Test 3: Profil
    results.append(("Profil utilisateur", test_get_me(token)))
    
    # Test 4: Chat
    results.append(("Chat avec IA", test_chat(token)))
    
    # Test 5: Conversations
    success, conversation_id = test_conversations(token)
    results.append(("Liste conversations", success))
    
    # Test 6: Statistiques
    results.append(("Statistiques", test_stats(token)))
    
    # Test 7: Liste des cas
    results.append(("Liste des cas", test_cases()))
    
    # Test 8: Export PDF
    results.append(("Export PDF", test_export_pdf(token, conversation_id)))
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")

if __name__ == "__main__":
    main()
