#!/usr/bin/env python3
"""
Script to check existing fee types and structures
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from finance.models import FeeType, FeeStructure
from academic.models import Level, AcademicYear
from accounts.models import Student

def check_fee_data():
    """Check existing fee data for invoice generation"""
    print("=== Données de frais pour génération de factures ===")
    
    # Fee Types
    fee_types = FeeType.objects.all()
    print(f"\n📋 Types de frais ({fee_types.count()}):")
    for ft in fee_types:
        print(f"   - {ft.name}: {ft.description}")
        print(f"     Récurrent: {'✅' if ft.is_recurring else '❌'} | Obligatoire: {'✅' if ft.is_mandatory else '❌'}")
    
    # Fee Structures
    fee_structures = FeeStructure.objects.select_related('fee_type', 'level', 'academic_year')
    print(f"\n💰 Structures de frais ({fee_structures.count()}):")
    for fs in fee_structures[:10]:  # Limite à 10 pour éviter trop d'affichage
        print(f"   - {fs.fee_type.name} pour {fs.level.name}: {fs.amount}€")
        print(f"     Année: {fs.academic_year.name} | Échéance: {fs.due_date}")
    
    # Levels
    levels = Level.objects.all()
    print(f"\n🎓 Niveaux disponibles ({levels.count()}):")
    for level in levels:
        print(f"   - {level.name}")
    
    # Students
    students = Student.objects.select_related('user')
    print(f"\n👨‍🎓 Élèves disponibles ({students.count()}):")
    for student in students[:5]:  # Limite à 5
        print(f"   - {student.user.get_full_name()}")
    
    # Academic Years
    academic_years = AcademicYear.objects.all()
    print(f"\n📅 Années académiques ({academic_years.count()}):")
    for year in academic_years:
        current = "⭐ ACTUELLE" if year.is_current else ""
        print(f"   - {year.name} {current}")

if __name__ == "__main__":
    check_fee_data()
