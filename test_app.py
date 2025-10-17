#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application AES Connect fonctionne correctement
"""

import sys
import requests
import time
from app import init_db

def test_database():
    """Test d'initialisation de la base de données"""
    print("🔍 Test 1: Initialisation de la base de données...")
    try:
        init_db()
        print("✅ Base de données initialisée avec succès\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}\n")
        return False

def test_imports():
    """Test d'importation des modules"""
    print("🔍 Test 2: Vérification des imports...")
    try:
        import flask
        import flask_cors
        import werkzeug
        import sqlite3
        print("✅ Tous les modules nécessaires sont disponibles\n")
        return True
    except ImportError as e:
        print(f"❌ Module manquant: {e}\n")
        return False

def test_app_creation():
    """Test de création de l'application Flask"""
    print("🔍 Test 3: Création de l'application Flask...")
    try:
        from app import app
        print(f"✅ Application Flask créée (debug={app.debug})\n")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}\n")
        return False

def test_health_endpoint(base_url="http://localhost:5000"):
    """Test du endpoint de santé"""
    print(f"🔍 Test 4: Endpoint de santé ({base_url}/health)...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Serveur en ligne: {data}\n")
            return True
        else:
            print(f"❌ Code HTTP {response.status_code}\n")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur\n")
        print("💡 Assurez-vous que le serveur est démarré avec: python3 app.py\n")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}\n")
        return False

def test_home_page(base_url="http://localhost:5000"):
    """Test de la page d'accueil"""
    print(f"🔍 Test 5: Page d'accueil ({base_url})...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            content_length = len(response.text)
            print(f"✅ Page d'accueil accessible ({content_length} caractères)\n")
            return True
        else:
            print(f"❌ Code HTTP {response.status_code}\n")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}\n")
        return False

def run_all_tests(server_running=False):
    """Exécute tous les tests"""
    print("=" * 60)
    print("🧪 TESTS DE L'APPLICATION AES CONNECT")
    print("=" * 60)
    print()
    
    results = []
    
    # Tests sans serveur
    results.append(("Initialisation DB", test_database()))
    results.append(("Imports", test_imports()))
    results.append(("Création App", test_app_creation()))
    
    # Tests avec serveur
    if server_running:
        time.sleep(2)  # Attendre que le serveur démarre
        results.append(("Endpoint Health", test_health_endpoint()))
        results.append(("Page Accueil", test_home_page()))
    else:
        print("⚠️  Les tests du serveur sont ignorés (serveur non démarré)")
        print("💡  Pour les tests complets, démarrez d'abord le serveur\n")
    
    # Résumé
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        return 0
    else:
        print("⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    server_running = "--server" in sys.argv
    exit_code = run_all_tests(server_running)
    sys.exit(exit_code)
