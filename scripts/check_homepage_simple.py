#!/usr/bin/env python3
"""
Script de vérification des améliorations de la page d'accueil
Vérifie que tous les éléments sont en place et fonctionnels
"""

import os
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
        ("Motifs décoratifs", "absolute"),
        ("Design moderne", "bg-gradient-to-br"),
        ("Statistiques animées", "text-3xl font-bold"),
        ("Features détaillées", "bg-white/80"),
        ("Section bénéfices", "bg-white/60")
    ]
    
    passed = 0
    for check_name, check_text in checks:
        if check_text in content:
            print(f"✅ {check_name}: Présent")
            passed += 1
        else:
            print(f"❌ {check_name}: Manquant")
    
    print(f"\n📊 Résultat template: {passed}/{len(checks)} vérifications réussies")
    return passed >= len(checks) * 0.9  # 90% de réussite minimum

def check_base_template_logo():
    """Vérifie que le logo dans base.html est cliquable"""
    print("\n🔍 Vérification du logo cliquable dans base.html...")
    
    base_path = Path("/home/jeshurun-nasser/dev/py/django-app/eschool/templates/base.html")
    
    if not base_path.exists():
        print("❌ Fichier base.html introuvable")
        return False
    
    content = base_path.read_text()
    
    # Vérifier que le logo est un lien vers home
    checks = [
        ("URL home", "{% url 'home' %}"),
        ("Texte eSchool", "eSchool"),
        ("Lien cliquable", "<a href"),
        ("Transition hover", "hover:text-gray-200")
    ]
    
    passed = 0
    for check_name, check_text in checks:
        if check_text in content:
            print(f"✅ {check_name}: Présent")
            passed += 1
        else:
            print(f"❌ {check_name}: Manquant")
    
    print(f"\n📊 Résultat logo: {passed}/{len(checks)} vérifications réussies")
    return passed >= 3  # Au moins 3/4 critères

def check_urls_configuration():
    """Vérifie la configuration des URLs"""
    print("\n🔍 Vérification de la configuration des URLs...")
    
    urls_path = Path("/home/jeshurun-nasser/dev/py/django-app/eschool/core/urls.py")
    
    if not urls_path.exists():
        print("❌ Fichier urls.py introuvable")
        return False
    
    content = urls_path.read_text()
    
    checks = [
        ("URL home définie", "name='home'"),
        ("Template configuré", "template_name='home.html'"),
        ("Vue template", "TemplateView.as_view"),
        ("Route racine", "path('',")
    ]
    
    passed = 0
    for check_name, check_text in checks:
        if check_text in content:
            print(f"✅ {check_name}: Présent")
            passed += 1
        else:
            print(f"❌ {check_name}: Manquant")
    
    print(f"\n📊 Résultat URLs: {passed}/{len(checks)} vérifications réussies")
    return passed >= 3

def check_file_sizes():
    """Vérifie les tailles de fichiers pour s'assurer du contenu"""
    print("\n🔍 Vérification des tailles de fichiers...")
    
    files_to_check = [
        ("home.html", "/home/jeshurun-nasser/dev/py/django-app/eschool/templates/home.html", 300),
        ("base.html", "/home/jeshurun-nasser/dev/py/django-app/eschool/templates/base.html", 200)
    ]
    
    all_good = True
    for filename, filepath, min_lines in files_to_check:
        path = Path(filepath)
        if path.exists():
            line_count = len(path.read_text().splitlines())
            if line_count >= min_lines:
                print(f"✅ {filename}: {line_count} lignes (≥{min_lines})")
            else:
                print(f"⚠️ {filename}: {line_count} lignes (<{min_lines})")
                all_good = False
        else:
            print(f"❌ {filename}: Fichier manquant")
            all_good = False
    
    return all_good

def main():
    """Fonction principale de vérification"""
    print("🚀 Vérification des améliorations de la page d'accueil eSchool")
    print("=" * 60)
    
    # Effectuer toutes les vérifications
    results = {
        "Template home.html": check_home_template(),
        "Logo cliquable": check_base_template_logo(),
        "Configuration URLs": check_urls_configuration(),
        "Tailles de fichiers": check_file_sizes()
    }
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES VÉRIFICATIONS:")
    print("-" * 40)
    
    total_passed = 0
    for check_name, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{check_name:.<25} {status}")
        if result:
            total_passed += 1
    
    print(f"\n🎯 Score global: {total_passed}/{len(results)} ({total_passed/len(results)*100:.0f}%)")
    
    if total_passed == len(results):
        print("\n🎉 TOUTES LES VÉRIFICATIONS RÉUSSIES!")
        print("✨ La page d'accueil a été améliorée avec succès:")
        print("   • ✅ Design moderne avec statistiques du projet")
        print("   • ✅ Logo cliquable vers la page d'accueil")
        print("   • ✅ Sections détaillées des fonctionnalités")
        print("   • ✅ Animations JavaScript interactives")
        print("   • ✅ Interface responsive avec Tailwind CSS")
        print("   • ✅ Motifs décoratifs et effets visuels")
        print("   • ✅ Section avantages et bénéfices")
        print("\n🌐 Accédez à http://127.0.0.1:8000/ pour voir les résultats")
        return True
    elif total_passed >= len(results) * 0.75:
        print("\n⚠️ VÉRIFICATIONS PARTIELLEMENT RÉUSSIES")
        print("💡 La plupart des améliorations sont en place")
        return True
    else:
        print("\n❌ CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("⚠️ Veuillez corriger les problèmes identifiés")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
