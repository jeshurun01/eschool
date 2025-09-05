#!/usr/bin/env python3
"""
Script pour détecter les IDs dupliqués dans les templates HTML
"""

import os
import re
from collections import defaultdict

def find_duplicate_ids():
    template_dir = "/home/jeshurun-nasser/dev/py/django-app/eschool/templates"
    id_counts = defaultdict(list)
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Rechercher tous les IDs
                id_pattern = r'id=["\']([^"\']+)["\']'
                matches = re.findall(id_pattern, content)
                
                for match in matches:
                    id_counts[match].append(filepath)
    
    # Afficher les IDs dupliqués
    print("🔍 DÉTECTION DES IDs DUPLIQUÉS")
    print("=" * 50)
    
    duplicates_found = False
    for id_name, files in id_counts.items():
        if len(files) > 1:
            duplicates_found = True
            print(f"❌ ID dupliqué: '{id_name}'")
            for file in files:
                rel_path = file.replace(template_dir, "templates")
                print(f"   - {rel_path}")
            print()
    
    if not duplicates_found:
        print("✅ Aucun ID dupliqué trouvé!")
    
    # Rechercher les IDs potentiellement problématiques dans le même fichier
    print("\n🔍 VÉRIFICATION DES IDs DANS CHAQUE FICHIER")
    print("=" * 50)
    
    id_pattern = r'id=["\']([^"\']+)["\']'  # Redéfinir le pattern
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                file_ids = defaultdict(list)
                for line_num, line in enumerate(lines, 1):
                    matches = re.findall(id_pattern, line)
                    for match in matches:
                        file_ids[match].append(line_num)
                
                # Vérifier les doublons dans le même fichier
                for id_name, line_numbers in file_ids.items():
                    if len(line_numbers) > 1:
                        rel_path = filepath.replace(template_dir, "templates")
                        print(f"❌ ID dupliqué dans {rel_path}: '{id_name}' aux lignes {line_numbers}")

if __name__ == "__main__":
    find_duplicate_ids()
