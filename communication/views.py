from django.shortcuts import render
from django.http import HttpResponse

# Vues temporaires (placeholder) - À implémenter plus tard

def announcement_list(request):
    return HttpResponse("Liste des annonces - En cours de développement")

def announcement_create(request):
    return HttpResponse("Créer une annonce - En cours de développement")

def announcement_detail(request, announcement_id):
    return HttpResponse(f"Détails de l'annonce {announcement_id} - En cours de développement")

def announcement_mark_read(request, announcement_id):
    return HttpResponse(f"Marquer l'annonce {announcement_id} comme lue - En cours de développement")

def message_list(request):
    return HttpResponse("Liste des messages - En cours de développement")

def message_compose(request):
    return HttpResponse("Composer un message - En cours de développement")

def message_detail(request, message_id):
    return HttpResponse(f"Détails du message {message_id} - En cours de développement")

def message_reply(request, message_id):
    return HttpResponse(f"Répondre au message {message_id} - En cours de développement")

def group_message_list(request):
    return HttpResponse("Liste des messages de groupe - En cours de développement")

def group_message_compose(request):
    return HttpResponse("Composer un message de groupe - En cours de développement")

def group_message_detail(request, message_id):
    return HttpResponse(f"Détails du message de groupe {message_id} - En cours de développement")

def resource_list(request):
    return HttpResponse("Liste des ressources - En cours de développement")

def resource_upload(request):
    return HttpResponse("Télécharger une ressource - En cours de développement")

def resource_detail(request, resource_id):
    return HttpResponse(f"Détails de la ressource {resource_id} - En cours de développement")

def resource_download(request, resource_id):
    return HttpResponse(f"Télécharger la ressource {resource_id} - En cours de développement")

def notification_list(request):
    return HttpResponse("Liste des notifications - En cours de développement")

def notification_mark_read(request, notification_id):
    return HttpResponse(f"Marquer la notification {notification_id} comme lue - En cours de développement")

def notification_mark_all_read(request):
    return HttpResponse("Marquer toutes les notifications comme lues - En cours de développement")
