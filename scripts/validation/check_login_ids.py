#!/usr/bin/env python3
"""
Script pour vérifier les IDs sur les pages d'authentification
"""

import os
import re
from collections import defaultdict

def check_login_page_ids():
    template_dir = "/home/jeshurun-nasser/dev/py/django-app/eschool/templates"
    auth_templates = [
        "account/login.html",
        "account/signup.html", 
        "account/password_reset.html",
        "account/password_change.html"
    ]
    
    print("🔍 VÉRIFICATION DES IDs - PAGES D'AUTHENTIFICATION")
    print("=" * 60)
    
    all_ids = defaultdict(list)
    
    for template in auth_templates:
        filepath = os.path.join(template_dir, template)
        if os.path.exists(filepath):
            print(f"\n📄 Analyse: {template}")
            print("-" * 40)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Rechercher tous les IDs
            id_pattern = r'id=["\']([^"\']+)["\']'
            matches = re.findall(id_pattern, content)
            
            template_ids = set()
            
            for match in matches:
                # Ignorer les IDs dynamiques Django
                if not ("{{" in match and "}}" in match):
                    if match in template_ids:
                        print(f"❌ ID dupliqué dans le même fichier: '{match}'")
                    else:
                        print(f"✅ ID trouvé: '{match}'")
                        template_ids.add(match)
                        all_ids[match].append(template)
                else:
                    print(f"🔧 ID dynamique Django: '{match}'")
        else:
            print(f"⚠️  Fichier non trouvé: {template}")
    
    # Vérifier les IDs dupliqués entre fichiers
    print(f"\n🔍 VÉRIFICATION DES IDs ENTRE FICHIERS")
    print("=" * 50)
    
    duplicates_found = False
    for id_name, templates in all_ids.items():
        if len(templates) > 1:
            duplicates_found = True
            print(f"❌ ID dupliqué: '{id_name}'")
            for template in templates:
                print(f"   - {template}")
            print()
    
    if not duplicates_found:
        print("✅ Aucun ID dupliqué entre les fichiers d'authentification!")
    
    return all_ids

def check_login_specific_elements():
    login_file = "/home/jeshurun-nasser/dev/py/django-app/eschool/templates/account/login.html"
    
    print(f"\n🎯 ANALYSE SPÉCIFIQUE - PAGE DE LOGIN")
    print("=" * 50)
    
    if not os.path.exists(login_file):
        print("❌ Fichier login.html non trouvé!")
        return
    
    with open(login_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Vérifications spécifiques
    issues = []
    
    # Rechercher les éléments critiques
    critical_elements = {
        'email_input': False,
        'password_input': False,
        'submit_button': False,
        'remember_checkbox': False,
        'password_toggle': False
    }
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Vérifier input email
        if 'type="email"' in line and 'id=' in line:
            critical_elements['email_input'] = True
            print(f"✅ Input Email trouvé ligne {line_num}")
        
        # Vérifier input password
        if 'type="password"' in line and 'id=' in line:
            critical_elements['password_input'] = True
            print(f"✅ Input Password trouvé ligne {line_num}")
        
        # Vérifier checkbox remember me
        if 'type="checkbox"' in line and 'id=' in line:
            critical_elements['remember_checkbox'] = True
            print(f"✅ Checkbox Remember Me trouvé ligne {line_num}")
        
        # Vérifier bouton submit
        if 'type="submit"' in line:
            critical_elements['submit_button'] = True
            print(f"✅ Bouton Submit trouvé ligne {line_num}")
        
        # Vérifier toggle password (eye icons)
        if 'id="eye-' in line:
            critical_elements['password_toggle'] = True
            print(f"✅ Toggle Password trouvé ligne {line_num}")
    
    # Résumé des vérifications
    print(f"\n📊 RÉSUMÉ DES ÉLÉMENTS CRITIQUES")
    print("-" * 40)
    
    all_good = True
    for element, found in critical_elements.items():
        status = "✅" if found else "❌"
        print(f"{status} {element.replace('_', ' ').title()}: {'Trouvé' if found else 'Manquant'}")
        if not found:
            all_good = False
    
    if all_good:
        print(f"\n🎉 TOUS LES ÉLÉMENTS CRITIQUES SONT PRÉSENTS!")
    else:
        print(f"\n⚠️  Certains éléments critiques sont manquants")
    
    return critical_elements

def check_form_accessibility():
    login_file = "/home/jeshurun-nasser/dev/py/django-app/eschool/templates/account/login.html"
    
    print(f"\n♿ VÉRIFICATION ACCESSIBILITÉ - LABELS ET INPUTS")
    print("=" * 60)
    
    with open(login_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher les labels et leurs attributs for
    label_pattern = r'<label[^>]+for=["\']([^"\']+)["\'][^>]*>'
    labels = re.findall(label_pattern, content)
    
    # Rechercher les inputs et leurs IDs
    input_pattern = r'<input[^>]+id=["\']([^"\']+)["\'][^>]*>'
    inputs = re.findall(input_pattern, content)
    
    print(f"📝 Labels trouvés:")
    for label in labels:
        print(f"   - for='{label}'")
    
    print(f"\n🔤 Inputs trouvés:")
    for input_id in inputs:
        print(f"   - id='{input_id}'")
    
    print(f"\n🔗 VÉRIFICATION CORRESPONDANCE LABEL ↔ INPUT:")
    accessibility_ok = True
    
    for label in labels:
        if label in inputs:
            print(f"✅ Label '{label}' → Input correspondant trouvé")
        else:
            print(f"❌ Label '{label}' → AUCUN input correspondant!")
            accessibility_ok = False
    
    if accessibility_ok:
        print(f"\n🎉 ACCESSIBILITÉ PARFAITE - Tous les labels sont liés!")
    else:
        print(f"\n⚠️  Problèmes d'accessibilité détectés")

if __name__ == "__main__":
    # Vérification générale des IDs
    all_ids = check_login_page_ids()
    
    # Analyse spécifique de la page de login
    critical_elements = check_login_specific_elements()
    
    # Vérification accessibilité
    check_form_accessibility()
    
    print(f"\n" + "="*60)
    print(f"🎯 CONCLUSION GÉNÉRALE")
    print(f"="*60)
    print(f"✅ Analyse terminée avec succès!")
