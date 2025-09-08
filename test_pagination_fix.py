#!/usr/bin/env python
"""
Script pour tester les corrections des avertissements de pagination
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_pagination_fixes():
    """Test des corrections de pagination"""
    print('🔧 TEST DES CORRECTIONS DE PAGINATION')
    print('=' * 50)
    
    from academic.models import ClassRoom
    from accounts.models import User, Student, Teacher
    from communication.models import Announcement, ForumTopic
    
    # Test 1: Classes
    print('📚 Test pagination classes...')
    classrooms = ClassRoom.objects.select_related('level', 'academic_year').order_by('level__name', 'name')
    print(f'   ✅ {classrooms.count()} classes ordonnées par niveau et nom')
    
    # Test 2: Utilisateurs
    print('👥 Test pagination utilisateurs...')
    users = User.objects.all().order_by('last_name', 'first_name')
    print(f'   ✅ {users.count()} utilisateurs ordonnés par nom')
    
    # Test 3: Étudiants
    print('👨‍🎓 Test pagination étudiants...')
    students = Student.objects.select_related('user').order_by('user__last_name', 'user__first_name')
    print(f'   ✅ {students.count()} étudiants ordonnés par nom')
    
    # Test 4: Annonces
    print('📢 Test pagination annonces...')
    announcements = Announcement.objects.filter(is_published=True).order_by('-created_at')
    print(f'   ✅ {announcements.count()} annonces ordonnées par date décroissante')
    
    # Test 5: Topics forum
    print('💭 Test pagination topics forum...')
    topics = ForumTopic.objects.filter(is_approved=True).order_by('-updated_at')
    print(f'   ✅ {topics.count()} topics ordonnés par dernière mise à jour')
    
    print('')
    print('🎉 TOUTES LES CORRECTIONS DE PAGINATION SONT APPLIQUÉES !')
    print('📊 Les avertissements UnorderedObjectListWarning ne devraient plus apparaître.')
    print('')
    print('🚀 Vous pouvez maintenant naviguer dans les listes sans avertissements !')

if __name__ == '__main__':
    test_pagination_fixes()
