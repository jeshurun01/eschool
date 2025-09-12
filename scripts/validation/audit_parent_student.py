#!/usr/bin/env python3
"""
Audit complet des interfaces Parent/Élève
"""

import os
import sys
import django

# Configuration de Django
sys.path.append('/home/jeshurun-nasser/dev/py/django-app/eschool')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Parent, Teacher
from academic.models import ClassRoom, Subject, Grade, Enrollment, Attendance
from finance.models import Invoice, Payment, FeeType, FeeStructure
from communication.models import Announcement

def audit_users():
    """Audit des utilisateurs par rôle"""
    print("👥 AUDIT DES UTILISATEURS")
    print("=" * 50)
    
    roles = User.ROLE_CHOICES
    for role_code, role_name in roles:
        count = User.objects.filter(role=role_code, is_active=True).count()
        print(f"   {role_name}: {count} utilisateur(s)")
    
    print(f"\n   Total actifs: {User.objects.filter(is_active=True).count()}")
    print(f"   Total inactifs: {User.objects.filter(is_active=False).count()}")

def audit_academic():
    """Audit du module académique"""
    print("\n📚 AUDIT MODULE ACADÉMIQUE")
    print("=" * 50)
    
    # Classes et inscriptions
    total_classes = ClassRoom.objects.count()
    total_subjects = Subject.objects.count()
    total_enrollments = Enrollment.objects.count()
    active_enrollments = Enrollment.objects.filter(withdrawal_date__isnull=True).count()
    
    print(f"   Classes: {total_classes}")
    print(f"   Matières: {total_subjects}")
    print(f"   Inscriptions totales: {total_enrollments}")
    print(f"   Inscriptions actives: {active_enrollments}")
    
    # Notes et présences
    total_grades = Grade.objects.count()
    total_attendances = Attendance.objects.count()
    
    print(f"   Notes enregistrées: {total_grades}")
    print(f"   Présences enregistrées: {total_attendances}")
    
    # Répartition par classe
    print(f"\n   📊 Répartition par classe:")
    for classroom in ClassRoom.objects.all()[:5]:  # Top 5
        student_count = classroom.students.count()
        print(f"      {classroom.name}: {student_count} élèves")

def audit_finance():
    """Audit du module financier"""
    print("\n💰 AUDIT MODULE FINANCIER")
    print("=" * 50)
    
    # Factures par statut
    statuses = ['DRAFT', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED']
    print("   📋 Factures par statut:")
    for status in statuses:
        count = Invoice.objects.filter(status=status).count()
        print(f"      {status}: {count} factures")
    
    # Paiements
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status='COMPLETED').count()
    print(f"\n   💳 Paiements:")
    print(f"      Total: {total_payments}")
    print(f"      Complétés: {completed_payments}")
    
    # Types de frais et structures
    fee_types = FeeType.objects.count()
    fee_structures = FeeStructure.objects.count()
    print(f"\n   🏗️  Configuration:")
    print(f"      Types de frais: {fee_types}")
    print(f"      Structures tarifaires: {fee_structures}")

def audit_student_parent_relationships():
    """Audit des relations parent-enfant"""
    print("\n👨‍👩‍👧‍👦 AUDIT RELATIONS PARENT-ENFANT")
    print("=" * 50)
    
    students_with_parents = 0
    parents_with_children = 0
    orphaned_students = 0
    
    for student in Student.objects.all():
        if student.parents.exists():
            students_with_parents += 1
        else:
            orphaned_students += 1
    
    for parent in Parent.objects.all():
        if parent.children.exists():
            parents_with_children += 1
    
    print(f"   Élèves avec parents: {students_with_parents}")
    print(f"   Élèves sans parents: {orphaned_students}")
    print(f"   Parents avec enfants: {parents_with_children}")
    print(f"   Parents sans enfants: {Parent.objects.count() - parents_with_children}")

def audit_communication():
    """Audit du module communication"""
    print("\n📢 AUDIT MODULE COMMUNICATION")
    print("=" * 50)
    
    try:
        total_announcements = Announcement.objects.count()
        recent_announcements = Announcement.objects.filter(
            created_at__gte=django.utils.timezone.now() - django.utils.timezone.timedelta(days=30)
        ).count()
        
        print(f"   Annonces totales: {total_announcements}")
        print(f"   Annonces récentes (30j): {recent_announcements}")
    except Exception as e:
        print(f"   ⚠️  Erreur module communication: {e}")

def audit_templates():
    """Audit des templates existants"""
    print("\n🎨 AUDIT DES TEMPLATES")
    print("=" * 50)
    
    template_dirs = [
        'templates/accounts/',
        'templates/academic/',
        'templates/finance/',
        'templates/communication/'
    ]
    
    base_path = '/home/jeshurun-nasser/dev/py/django-app/eschool'
    
    for template_dir in template_dirs:
        full_path = os.path.join(base_path, template_dir)
        if os.path.exists(full_path):
            files = [f for f in os.listdir(full_path) if f.endswith('.html')]
            print(f"   {template_dir}: {len(files)} templates")
            
            # Templates spécifiques pour parent/étudiant
            if template_dir == 'templates/accounts/':
                key_templates = ['student_dashboard.html', 'parent_dashboard.html', 'teacher_dashboard.html']
                for template in key_templates:
                    status = "✅" if template in files else "❌"
                    print(f"      {status} {template}")

def audit_urls():
    """Audit de la configuration des URLs"""
    print("\n🔗 AUDIT DES URLS")
    print("=" * 50)
    
    # Vérifier les fichiers d'URLs
    url_files = [
        'core/urls.py',
        'accounts/urls.py', 
        'academic/urls.py',
        'finance/urls.py'
    ]
    
    base_path = '/home/jeshurun-nasser/dev/py/django-app/eschool'
    
    for url_file in url_files:
        full_path = os.path.join(base_path, url_file)
        if os.path.exists(full_path):
            print(f"   ✅ {url_file}")
        else:
            print(f"   ❌ {url_file}")

def recommendations():
    """Recommandations d'amélioration"""
    print("\n💡 RECOMMANDATIONS D'AMÉLIORATION")
    print("=" * 50)
    
    print("   🎯 Interface Élève:")
    print("      ✅ Dashboard existant - À améliorer")
    print("      📝 Vue détaillée des notes par matière")
    print("      📅 Calendrier des devoirs et examens")
    print("      💰 Historique et statut des paiements")
    print("      📊 Graphiques de progression")
    
    print("\n   🎯 Interface Parent:")
    print("      ✅ Dashboard existant - À améliorer")
    print("      👥 Sélection multi-enfants")
    print("      📈 Comparaison de performance")
    print("      💬 Communication avec enseignants")
    print("      🔔 Notifications personnalisées")
    
    print("\n   🎯 Module Académique:")
    print("      📚 Vue emploi du temps interactif")
    print("      📝 Gestion des devoirs/assignments")
    print("      📊 Rapports de progression détaillés")
    print("      🎯 Objectifs et suivis individuels")
    
    print("\n   🎯 Module Finance:")
    print("      💳 Portail de paiement en ligne") 
    print("      📄 Génération de reçus PDF")
    print("      📊 Historique des transactions")
    print("      ⚠️  Alertes d'échéances")

if __name__ == '__main__':
    print("🔍 AUDIT COMPLET DES INTERFACES PARENT/ÉLÈVE")
    print("=" * 60)
    
    audit_users()
    audit_academic()
    audit_finance()
    audit_student_parent_relationships()
    audit_communication()
    audit_templates()
    audit_urls()
    recommendations()
    
    print(f"\n✅ Audit terminé - {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
