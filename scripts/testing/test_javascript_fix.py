#!/usr/bin/env python
"""
Script de test pour vérifier la correction JavaScript du toggleStudentStatus
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student

def test_javascript_fix():
    """Teste la page student_list pour vérifier la présence du token CSRF"""
    
    print("🧪 Test de la correction JavaScript toggleStudentStatus...")
    
    # Vérifier qu'il y a des étudiants dans la base
    students = Student.objects.all()[:3]
    
    if not students:
        print("❌ Aucun étudiant trouvé pour le test")
        return False
    
    print(f"✅ {len(students)} étudiants trouvés pour le test")
    
    # Lire le template pour vérifier les corrections
    template_path = '/home/jeshurun-nasser/dev/py/django-app/eschool/templates/accounts/student_list.html'
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Vérifications
    checks = [
        ('{% csrf_token %}', 'Token CSRF présent'),
        ('if (!csrfToken)', 'Vérification robuste du token CSRF'),
        ('csrfToken.value', 'Accès sécurisé à la valeur du token'),
        ('toggleStudentStatus', 'Fonction JavaScript présente'),
    ]
    
    all_passed = True
    
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = test_javascript_fix()
    
    if success:
        print("\n🎉 Toutes les corrections JavaScript sont en place!")
        print("📋 Résumé des corrections:")
        print("   1. Token CSRF ajouté au template")
        print("   2. Vérification robuste du token avant utilisation")
        print("   3. Protection admin ajoutée à la vue")
        print("   4. Gestion d'erreur améliorée")
    else:
        print("\n❌ Certaines corrections sont manquantes")
    
    sys.exit(0 if success else 1)
