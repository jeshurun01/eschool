#!/usr/bin/env python3
"""
Script de vérification des améliorations de la page d'accueil
Vérifie que tous les éléments sont en place et fonctionnels
"""

import os
import re
import requests
from pathlib import Path

def check_home_template():
    """Vérifie le contenu du template home.html"""
    print("🔍 Vérification du template home.html...")
    
    home_path = Path("/home/jeshurun-nasser/dev/py/django-app/eschool/templates/home.html")
    
    if not home_path.exists():
        print("❌ Fichier home.html introuvable")
        return False
    
    content = home_path.read_text()
    
    # Vérifications essentielles
    checks = [
        ("Badge de statut", "Système 100% opérationnel"),
        ("Titre principal", "Bienvenue sur"),
        ("Statistiques - Forum", "31"),
        ("Statistiques - Messages", "144"), 
        ("Statistiques - Utilisateurs", "35"),
        ("Statistiques - Progression", "90%"),
        ("Bouton connexion", "Se connecter"),
        ("Bouton inscription", "Créer un compte"),
        ("Section gestion élèves", "Gestion des élèves"),
        ("Section suivi académique", "Suivi académique"),
        ("Section communication", "Communication"),
        ("Section avantages", "Pourquoi choisir eSchool"),
        ("Animation JavaScript", "document.addEventListener"),
        ("Animation compteurs", "setInterval"),
        ("Motifs décoratifs", "absolute")
    ]
    
    for check_name, check_text in checks:
        if check_text in content:
            print(f"✅ {check_name}: Présent")
        else:
            print(f"❌ {check_name}: Manquant")
            return False
    
    print("✅ Template home.html validé avec succès")
    return True

def check_base_template_logo():
    """Vérifie que le logo dans base.html est cliquable"""
    print("\n🔍 Vérification du logo cliquable dans base.html...")
    
    base_path = Path("/home/jeshurun-nasser/dev/py/django-app/eschool/templates/base.html")
    
    if not base_path.exists():
        print("❌ Fichier base.html introuvable")
        return False
    
    content = base_path.read_text()
    
    # Vérifier que le logo est un lien vers home
    if 'href="{% url \'home\' %}"' in content and 'eSchool' in content:
        print("✅ Logo cliquable vers la page d'accueil: Configuré")
        return True
    else:
        print("❌ Logo cliquable: Non configuré")
        return False

def check_urls_configuration():
    """Vérifie la configuration des URLs"""
    print("\n🔍 Vérification de la configuration des URLs...")
    
    urls_path = Path("/home/jeshurun-nasser/dev/py/django-app/eschool/core/urls.py")
    
    if not urls_path.exists():
        print("❌ Fichier urls.py introuvable")
        return False
    
    content = urls_path.read_text()
    
    if "name='home'" in content and "TemplateView.as_view(template_name='home.html')" in content:
        print("✅ URL de la page d'accueil: Configurée")
        return True
    else:
        print("❌ URL de la page d'accueil: Non configurée")
        return False

def check_server_response():
    """Vérifie que le serveur répond correctement"""
    print("\n🔍 Vérification de la réponse du serveur...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur Django: Répond correctement (200)")
            
            # Vérifier quelques éléments clés dans la réponse
            if "eSchool" in response.text and "Système 100% opérationnel" in response.text:
                print("✅ Contenu de la page: Correct")
                return True
            else:
                print("⚠️ Contenu de la page: Incomplet")
                return False
        else:
            print(f"❌ Serveur Django: Erreur {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Serveur Django: Non accessible ({e})")
        return False

def main():
    """Fonction principale de vérification"""
    print("🚀 Vérification des améliorations de la page d'accueil eSchool")
    print("=" * 60)
    
    all_checks = [
        check_home_template(),
        check_base_template_logo(),
        check_urls_configuration(),
        check_server_response()
    ]
    
    print("\n" + "=" * 60)
    if all(all_checks):
        print("🎉 TOUTES LES VÉRIFICATIONS RÉUSSIES!")
        print("✨ La page d'accueil a été améliorée avec succès:")
        print("   • Design moderne avec statistiques du projet")
        print("   • Logo cliquable vers la page d'accueil")
        print("   • Sections détaillées des fonctionnalités")
        print("   • Animations JavaScript interactives")
        print("   • Interface responsive avec Tailwind CSS")
        return True
    else:
        print("❌ CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("⚠️ Veuillez corriger les problèmes identifiés")
        return False

if __name__ == "__main__":
    main()
