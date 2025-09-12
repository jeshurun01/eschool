#!/usr/bin/env python
"""
Test de la vue attendance_list via simulation de requête
Vérifier que les classes filtrées sont correctement passées au template
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from academic.views import attendance_list
from accounts.models import Teacher
from academic.models import ClassRoom, TeacherAssignment

User = get_user_model()

def test_attendance_list_view():
    """Test direct de la vue attendance_list"""
    
    print("=== Test de la vue attendance_list ===\n")
    
    # Créer une requête factice
    factory = RequestFactory()
    
    # Prendre un enseignant
    teacher = Teacher.objects.select_related('user').first()
    if not teacher:
        print("❌ Aucun enseignant trouvé")
        return
    
    print(f"Test avec l'enseignant: {teacher.user.get_full_name()}")
    
    # Créer une requête GET
    request = factory.get('/academic/attendance/')
    request.user = teacher.user
    
    try:
        # Appeler la vue
        response = attendance_list(request)
        
        print(f"Status de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ La vue fonctionne correctement")
            
            # Analyser le contexte (si accessible)
            if hasattr(response, 'context_data'):
                context = response.context_data
                classrooms = context.get('classrooms', [])
                print(f"Nombre de classes dans le contexte: {len(classrooms)}")
                
                for classroom in classrooms:
                    print(f"  - {classroom.name}")
            else:
                print("ℹ️  Contexte non accessible directement")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'appel de la vue: {e}")
    
    print()
    
    # Vérification manuelle de la logique
    print("Vérification manuelle de la logique de filtrage:")
    
    # Toutes les classes
    all_classrooms = ClassRoom.objects.filter(academic_year__is_current=True)
    print(f"Total des classes: {all_classrooms.count()}")
    
    # Assignations de l'enseignant
    teacher_assignments = TeacherAssignment.objects.filter(
        teacher=teacher,
        academic_year__is_current=True
    ).select_related('classroom', 'subject')
    
    classroom_ids = teacher_assignments.values_list('classroom_id', flat=True).distinct()
    filtered_classrooms = all_classrooms.filter(id__in=classroom_ids)
    
    print(f"Classes filtrées pour {teacher.user.get_full_name()}: {filtered_classrooms.count()}")
    for classroom in filtered_classrooms:
        print(f"  - {classroom.name}")
    
    # Vérifier si l'utilisateur a l'attribut teacher_profile
    user = teacher.user
    print(f"\nVérifications sur l'utilisateur:")
    print(f"  hasattr(user, 'teacher_profile'): {hasattr(user, 'teacher_profile')}")
    print(f"  user.is_superuser: {user.is_superuser}")
    
    if hasattr(user, 'teacher_profile'):
        print(f"  user.teacher_profile: {user.teacher_profile}")
        print("  ✅ L'attribut teacher_profile est accessible")
    else:
        print("  ❌ L'attribut teacher_profile n'est pas accessible")
        print("  Vérification des relations:")
        try:
            teacher_profile = Teacher.objects.get(user=user)
            print(f"    Teacher trouvé par requête: {teacher_profile}")
        except Teacher.DoesNotExist:
            print("    ❌ Aucun profil enseignant trouvé")

if __name__ == '__main__':
    test_attendance_list_view()
