#!/usr/bin/env python
"""
Script de vérification rapide de l'état de la base de données
Usage: uv run python scripts/check_database.py
"""

import os
import sys
import django

# Configuration Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher, Parent
from academic.models import AcademicYear, ClassRoom, Subject, Grade, Enrollment, Session, SessionAttendance, DailyAttendanceSummary
from finance.models import Invoice, Payment
from communication.models import Announcement, Message
from django.db.models import Count, Sum, Avg

def print_separator(char="=", length=80):
    print(char * length)

def print_header(text):
    print_separator()
    print(f"  {text}")
    print_separator()
    print()

def print_section(title):
    print(f"\n📊 {title}")
    print("-" * 80)

print_header("🔍 VÉRIFICATION DE LA BASE DE DONNÉES - eSchool")

# ============================================================================
# 1. ANNÉE ACADÉMIQUE
# ============================================================================
print_section("Année académique")
academic_years = AcademicYear.objects.all()
if academic_years.exists():
    for year in academic_years:
        status = "✅ ACTIVE" if year.is_current else "⚪ Inactive"
        print(f"   {status} {year.name}")
        print(f"      Période: {year.start_date} → {year.end_date}")
else:
    print("   ❌ Aucune année académique trouvée")

# ============================================================================
# 2. UTILISATEURS
# ============================================================================
print_section("Utilisateurs")

# Superutilisateurs
superusers = User.objects.filter(is_superuser=True)
print(f"   👑 Superutilisateurs: {superusers.count()}")
for admin in superusers:
    print(f"      - {admin.email} ({admin.get_full_name()})")

# Par rôle
roles_count = {
    'ADMIN': User.objects.filter(role='ADMIN', is_superuser=False).count(),
    'TEACHER': User.objects.filter(role='TEACHER').count(),
    'STUDENT': User.objects.filter(role='STUDENT').count(),
    'PARENT': User.objects.filter(role='PARENT').count(),
}
print(f"\n   Répartition par rôle:")
for role, count in roles_count.items():
    print(f"      {role:10s}: {count:3d}")

# ============================================================================
# 3. PROFILS
# ============================================================================
print_section("Profils")
print(f"   👨‍🏫 Enseignants: {Teacher.objects.count()}")
print(f"   🎓 Élèves: {Student.objects.count()}")
print(f"   👪 Parents: {Parent.objects.count()}")

# Élèves avec/sans classe
students_with_class = Student.objects.filter(current_class__isnull=False).count()
students_without_class = Student.objects.filter(current_class__isnull=True).count()
print(f"\n   Élèves inscrits: {students_with_class}")
print(f"   Élèves non inscrits: {students_without_class}")

# ============================================================================
# 4. STRUCTURE ACADÉMIQUE
# ============================================================================
print_section("Structure académique")
print(f"   📚 Classes: {ClassRoom.objects.count()}")
print(f"   📖 Matières: {Subject.objects.count()}")
print(f"   📝 Inscriptions: {Enrollment.objects.count()}")
print(f"      └─ Actives: {Enrollment.objects.filter(is_active=True).count()}")

# ============================================================================
# 5. DONNÉES ACADÉMIQUES
# ============================================================================
print_section("Données académiques")
print(f"   📅 Sessions de cours: {Session.objects.count()}")
print(f"   ✅ Présences (sessions): {SessionAttendance.objects.count()}")
print(f"      └─ Présent: {SessionAttendance.objects.filter(status='PRESENT').count()}")
print(f"      └─ Absent: {SessionAttendance.objects.filter(status='ABSENT').count()}")
print(f"      └─ En retard: {SessionAttendance.objects.filter(status='LATE').count()}")
print(f"   📊 Résumés journaliers: {DailyAttendanceSummary.objects.count()}")
print(f"   📈 Notes: {Grade.objects.count()}")

# Moyenne des notes
avg_grade = Grade.objects.aggregate(avg=Avg('score'))['avg']
if avg_grade:
    print(f"      └─ Moyenne générale: {avg_grade:.2f}/20")

# ============================================================================
# 6. FINANCES
# ============================================================================
print_section("Finances")
invoices = Invoice.objects.all()
print(f"   💰 Factures: {invoices.count()}")
if invoices.exists():
    paid = invoices.filter(status='PAID').count()
    partial = invoices.filter(status='PARTIAL').count()
    unpaid = invoices.filter(status='UNPAID').count()
    print(f"      └─ Payées: {paid}")
    print(f"      └─ Partielles: {partial}")
    print(f"      └─ Impayées: {unpaid}")

payments = Payment.objects.all()
print(f"   💳 Paiements: {payments.count()}")
if payments.exists():
    total_payments = payments.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0
    print(f"      └─ Total encaissé: {total_payments:,.0f} FCFA")

# ============================================================================
# 7. COMMUNICATION
# ============================================================================
print_section("Communication")
print(f"   📢 Annonces: {Announcement.objects.count()}")
print(f"   ✉️  Messages: {Message.objects.count()}")

# ============================================================================
# 8. INTÉGRITÉ DES DONNÉES
# ============================================================================
print_section("Vérifications d'intégrité")

issues = []

# Élèves sans inscription active
students_no_enrollment = Student.objects.filter(
    current_class__isnull=False
).exclude(
    enrollments__is_active=True
).count()
if students_no_enrollment > 0:
    issues.append(f"⚠️  {students_no_enrollment} élève(s) avec classe mais sans inscription active")

# Classes sans élèves
empty_classes = ClassRoom.objects.annotate(
    student_count=Count('students')
).filter(student_count=0).count()
if empty_classes > 0:
    issues.append(f"⚠️  {empty_classes} classe(s) sans élèves")

# Factures sans étudiant
invoices_no_student = Invoice.objects.filter(student__isnull=True).count()
if invoices_no_student > 0:
    issues.append(f"⚠️  {invoices_no_student} facture(s) sans étudiant")

if issues:
    for issue in issues:
        print(f"   {issue}")
else:
    print("   ✅ Aucun problème détecté")

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print()
print_separator()
print("✅ VÉRIFICATION TERMINÉE")
print_separator()
print()
print("💡 Commandes utiles:")
print("   - Lancer le serveur : uv run python manage.py runserver")
print("   - Réinitialiser BD  : bash scripts/clean_and_setup.sh")
print("   - Générer données   : uv run python scripts/reset_and_populate.py")
print()
