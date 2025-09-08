#!/usr/bin/env python
"""
Script de résumé des données de test et vérification de connexion
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Student, Teacher, Parent
from academic.models import ClassRoom, Subject, Enrollment, Grade, Attendance
from finance.models import Invoice, Payment
from communication.models import Announcement, Message, ForumTopic, ForumPost

def main():
    print('🎉 RÉSUMÉ COMPLET DES DONNÉES CRÉÉES')
    print('=' * 50)
    print(f'👥 Utilisateurs: {User.objects.count()}')
    print(f'👨‍🎓 Étudiants: {Student.objects.count()}')
    print(f'👨‍🏫 Enseignants: {Teacher.objects.count()}')
    print(f'👨‍👩‍👧‍👦 Parents: {Parent.objects.count()}')
    print(f'🏫 Classes: {ClassRoom.objects.count()}')
    print(f'📚 Matières: {Subject.objects.count()}')
    print(f'📝 Inscriptions: {Enrollment.objects.count()}')
    print(f'📊 Notes: {Grade.objects.count()}')
    print(f'📅 Présences: {Attendance.objects.count()}')
    print(f'💰 Factures: {Invoice.objects.count()}')
    print(f'💳 Paiements: {Payment.objects.count()}')
    print(f'📢 Annonces: {Announcement.objects.count()}')
    print(f'💬 Messages: {Message.objects.count()}')
    print(f'💭 Sujets Forum: {ForumTopic.objects.count()}')
    print(f'📝 Posts Forum: {ForumPost.objects.count()}')
    print('')
    
    print('🔑 COMPTES DE TEST DISPONIBLES:')
    print('=' * 40)
    print('🔐 Super Admin: nasser@eschool.com / admin123')
    print('👨‍💼 Admin: admin@eschool.com / admin123')
    
    # Afficher quelques enseignants
    teachers = Teacher.objects.select_related('user')[:3]
    if teachers:
        print('\n👨‍🏫 Enseignants (exemples):')
        for teacher in teachers:
            print(f'   - {teacher.user.email} / teacher123')
    
    # Afficher quelques parents
    parents = Parent.objects.select_related('user')[:3]
    if parents:
        print('\n👨‍👩‍👧‍👦 Parents (exemples):')
        for parent in parents:
            print(f'   - {parent.user.email} / parent123')
    
    # Afficher quelques étudiants
    students = Student.objects.select_related('user')[:3]
    if students:
        print('\n👨‍🎓 Étudiants (exemples):')
        for student in students:
            print(f'   - {student.user.email} / student123')
    
    print('')
    print('🌐 URLS IMPORTANTES:')
    print('=' * 30)
    print('🏠 Accueil: http://127.0.0.1:8000/')
    print('🔐 Connexion: http://127.0.0.1:8000/accounts/login/')
    print('📊 Dashboard: http://127.0.0.1:8000/accounts/')
    print('👥 Administration: http://127.0.0.1:8000/admin/')
    print('')
    print('✅ Base de données prête pour les tests!')
    print('📋 Vous pouvez maintenant vous connecter avec les comptes ci-dessus.')

if __name__ == '__main__':
    main()
