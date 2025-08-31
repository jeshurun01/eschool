from django.shortcuts import render
from django.http import HttpResponse

# Vues temporaires (placeholder) - À implémenter plus tard

def academic_year_list(request):
    return HttpResponse("Liste des années scolaires - En cours de développement")

def academic_year_create(request):
    return HttpResponse("Créer une année scolaire - En cours de développement")

def level_list(request):
    return HttpResponse("Liste des niveaux - En cours de développement")

def level_create(request):
    return HttpResponse("Créer un niveau - En cours de développement")

def subject_list(request):
    return HttpResponse("Liste des matières - En cours de développement")

def subject_create(request):
    return HttpResponse("Créer une matière - En cours de développement")

def classroom_list(request):
    return HttpResponse("Liste des classes - En cours de développement")

def classroom_create(request):
    return HttpResponse("Créer une classe - En cours de développement")

def classroom_detail(request, classroom_id):
    return HttpResponse(f"Détails de la classe {classroom_id} - En cours de développement")

def classroom_students(request, classroom_id):
    return HttpResponse(f"Élèves de la classe {classroom_id} - En cours de développement")

def classroom_timetable(request, classroom_id):
    return HttpResponse(f"Emploi du temps de la classe {classroom_id} - En cours de développement")

def timetable_list(request):
    return HttpResponse("Liste des emplois du temps - En cours de développement")

def timetable_create(request):
    return HttpResponse("Créer un emploi du temps - En cours de développement")

def attendance_list(request):
    return HttpResponse("Liste des présences - En cours de développement")

def attendance_take(request):
    return HttpResponse("Faire l'appel - En cours de développement")

def attendance_class(request, classroom_id):
    return HttpResponse(f"Présences de la classe {classroom_id} - En cours de développement")

def grade_list(request):
    return HttpResponse("Liste des notes - En cours de développement")

def grade_add(request):
    return HttpResponse("Ajouter une note - En cours de développement")

def student_grades(request, student_id):
    return HttpResponse(f"Notes de l'élève {student_id} - En cours de développement")

def class_grades(request, classroom_id):
    return HttpResponse(f"Notes de la classe {classroom_id} - En cours de développement")

def student_bulletin(request, student_id):
    return HttpResponse(f"Bulletin de l'élève {student_id} - En cours de développement")

def class_report(request, classroom_id):
    return HttpResponse(f"Rapport de la classe {classroom_id} - En cours de développement")
