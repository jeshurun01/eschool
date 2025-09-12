#!/usr/bin/env python
"""
Script pour corriger tous les default=timezone.now dans les modèles
"""

import os
import re

def fix_timezone_defaults():
    """Corrige les default=timezone.now problématiques"""
    
    # Fichiers à corriger
    files_to_fix = [
        'communication/models.py'
    ]
    
    base_path = '/home/jeshurun-nasser/dev/py/django-app/eschool'
    
    for file_path in files_to_fix:
        full_path = os.path.join(base_path, file_path)
        
        print(f"🔧 Correction de {file_path}...")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacements pour les champs DateTimeField
        content = re.sub(
            r'models\.DateTimeField\(default=timezone\.now,',
            'models.DateTimeField(default=get_current_datetime,',
            content
        )
        
        # Remplacements pour les champs DateField
        content = re.sub(
            r'models\.DateField\(default=timezone\.now,',
            'models.DateField(default=get_current_date,',
            content
        )
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_path} corrigé")

if __name__ == "__main__":
    print("🕐 Correction des default=timezone.now...")
    fix_timezone_defaults()
    print("🎉 Corrections terminées!")
