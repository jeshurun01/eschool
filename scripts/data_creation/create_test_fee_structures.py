#!/usr/bin/env python
"""
Script pour créer des structures de test pour démontrer le système de filtrage
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import FeeType, FeeStructure
from academic.models import Level, AcademicYear

def create_test_structures():
    """Créer quelques structures de test"""
    print("🔧 Création de structures de test pour le système de filtrage...")
    
    # Récupérer les données de base
    current_year = AcademicYear.objects.filter(is_current=True).first()
    levels = Level.objects.all()[:3]  # Prendre les 3 premiers niveaux
    
    if not current_year:
        print("❌ Aucune année académique courante trouvée")
        return
    
    if not levels:
        print("❌ Aucun niveau trouvé")
        return
    
    print(f"📅 Année académique: {current_year.name}")
    print(f"🎓 Niveaux disponibles: {[l.name for l in levels]}")
    
    # Créer quelques types de frais spéciaux pour les tests
    test_fee_types = [
        {
            'name': 'Frais d\'examen final',
            'description': 'Frais pour les examens de fin d\'année',
            'is_recurring': False,
            'is_mandatory': True
        },
        {
            'name': 'Activités sportives',
            'description': 'Frais pour les activités sportives et clubs',
            'is_recurring': True,
            'is_mandatory': False
        },
        {
            'name': 'Assurance scolaire',
            'description': 'Couverture d\'assurance pour les élèves',
            'is_recurring': False,
            'is_mandatory': True
        }
    ]
    
    created_structures = 0
    
    for fee_data in test_fee_types:
        # Créer ou récupérer le type de frais
        fee_type, created = FeeType.objects.get_or_create(
            name=fee_data['name'],
            defaults={
                'description': fee_data['description'],
                'is_recurring': fee_data['is_recurring'],
                'is_mandatory': fee_data['is_mandatory']
            }
        )
        
        if created:
            print(f"✅ Type de frais créé: {fee_type.name}")
        else:
            print(f"📋 Type de frais existant: {fee_type.name}")
        
        # Créer des structures pour quelques niveaux
        for level in levels:
            existing = FeeStructure.objects.filter(
                fee_type=fee_type,
                level=level,
                academic_year=current_year
            ).first()
            
            if not existing:
                # Montants différents selon le type
                if 'examen' in fee_type.name.lower():
                    amount = 15000 + (level.id * 2000)  # 15k à 25k selon le niveau
                elif 'sport' in fee_type.name.lower():
                    amount = 8000 + (level.id * 1000)   # 8k à 15k selon le niveau
                elif 'assurance' in fee_type.name.lower():
                    amount = 12000 + (level.id * 500)   # 12k à 16k selon le niveau
                else:
                    amount = 10000 + (level.id * 1000)  # Par défaut
                
                structure = FeeStructure.objects.create(
                    fee_type=fee_type,
                    level=level,
                    academic_year=current_year,
                    amount=amount
                )
                
                print(f"   💰 Structure créée: {level.name} - {amount:,} FCFA")
                created_structures += 1
            else:
                print(f"   📋 Structure existante: {level.name} - {existing.amount:,} FCFA")
    
    print(f"\n🎉 {created_structures} nouvelles structures créées!")
    print("\n📊 Résumé des types de frais:")
    
    for fee_type in FeeType.objects.all():
        structure_count = FeeStructure.objects.filter(fee_type=fee_type).count()
        mandatory_text = "✅ Obligatoire" if fee_type.is_mandatory else "⭕ Optionnel"
        recurring_text = "🔄 Récurrent" if fee_type.is_recurring else "1️⃣ Unique"
        
        print(f"  • {fee_type.name}: {structure_count} structures - {mandatory_text}, {recurring_text}")
    
    print("\n🌐 Accédez à http://localhost:8000/finance/fee-types/ pour tester le filtrage!")

if __name__ == "__main__":
    create_test_structures()
