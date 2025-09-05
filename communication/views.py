from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .models import (
    Announcement, AnnouncementRead, Message, GroupMessage, 
    GroupMessageRead, Resource, ResourceAccess, Notification
)
from accounts.models import User
from academic.models import ClassRoom, Level


# Fonctions utilitaires pour les permissions
def is_staff_or_admin(user):
    """Vérifie si l'utilisateur est staff ou admin"""
    return user.is_authenticated and (getattr(user, 'role', None) in ['ADMIN', 'SUPER_ADMIN', 'TEACHER'] or user.is_staff)


def admin_required(view_func):
    """Décorateur pour les vues nécessitant des droits admin"""
    return user_passes_test(lambda u: u.is_authenticated and getattr(u, 'role', None) in ['ADMIN', 'SUPER_ADMIN'])(view_func)


def staff_required(view_func):
    """Décorateur pour les vues nécessitant des droits staff"""
    return user_passes_test(is_staff_or_admin)(view_func)


# VUES DES ANNONCES

@login_required
def announcement_list(request):
    """Liste des annonces visibles pour l'utilisateur"""
    user = request.user
    
    # Filtrer les annonces selon le rôle de l'utilisateur
    announcements = Announcement.objects.filter(is_published=True)
    
    if getattr(user, 'role', None) == 'STUDENT':
        announcements = announcements.filter(
            Q(audience__in=['ALL', 'STUDENTS'])
        ).distinct()
    elif getattr(user, 'role', None) == 'PARENT':
        announcements = announcements.filter(
            Q(audience__in=['ALL', 'PARENTS'])
        ).distinct()
    elif getattr(user, 'role', None) == 'TEACHER':
        announcements = announcements.filter(
            Q(audience__in=['ALL', 'TEACHERS', 'STAFF'])
        ).distinct()
    elif getattr(user, 'role', None) in ['ADMIN', 'SUPER_ADMIN']:
        # Les admins voient toutes les annonces
        pass
    
    # Marquer les annonces non lues
    read_announcements = AnnouncementRead.objects.filter(user=user).values_list('announcement_id', flat=True)
    
    # Pagination
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'announcements': page_obj,
        'user': user,
        'total_announcements': announcements.count(),
        'unread_count': announcements.exclude(id__in=read_announcements).count(),
        'read_announcements': read_announcements,
    }
    
    return render(request, 'communication/announcement_list.html', context)


@staff_required
@csrf_protect
def announcement_create(request):
    """Créer une nouvelle annonce"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        type_choice = request.POST.get('type', 'GENERAL')
        audience = request.POST.get('audience', 'ALL')
        priority = int(request.POST.get('priority', 1))
        is_pinned = request.POST.get('is_pinned') == 'on'
        
        if title and content:
            announcement = Announcement.objects.create(
                title=title,
                content=content,
                type=type_choice,
                audience=audience,
                priority=priority,
                is_pinned=is_pinned,
                author=request.user,
                is_published=True,
                publish_date=timezone.now()
            )
            
            messages.success(request, 'Annonce créée avec succès!')
            return redirect('communication:announcement_list')
        else:
            messages.error(request, 'Titre et contenu sont obligatoires.')
    
    context = {
        'announcement_types': Announcement.TYPE_CHOICES,
        'audience_choices': Announcement.AUDIENCE_CHOICES,
    }
    
    return render(request, 'communication/announcement_create.html', context)


@login_required
def announcement_detail(request, announcement_id):
    """Détails d'une annonce"""
    announcement = get_object_or_404(Announcement, id=announcement_id, is_published=True)
    
    # Marquer comme lu
    read_obj, created = AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    context = {
        'announcement': announcement,
        'is_read': not created,
    }
    
    return render(request, 'communication/announcement_detail.html', context)


@login_required
@require_http_methods(["POST"])
def announcement_mark_read(request, announcement_id):
    """Marquer une annonce comme lue (AJAX)"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    read_obj, created = AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        user=request.user
    )
    
    return JsonResponse({
        'success': True,
        'created': created
    })


# VUES DES MESSAGES PRIVÉS

@login_required
def message_list(request):
    """Liste des messages de l'utilisateur"""
    tab = request.GET.get('tab', 'received')  # received, sent, all
    
    user = request.user
    
    if tab == 'sent':
        messages_queryset = Message.objects.filter(
            sender=user,
            deleted_by_sender=False
        ).select_related('recipient').order_by('-sent_date')
    elif tab == 'all':
        messages_queryset = Message.objects.filter(
            Q(sender=user, deleted_by_sender=False) |
            Q(recipient=user, deleted_by_recipient=False)
        ).select_related('sender', 'recipient').order_by('-sent_date')
    else:  # received
        messages_queryset = Message.objects.filter(
            recipient=user,
            deleted_by_recipient=False
        ).select_related('sender').order_by('-sent_date')
    
    # Pagination
    paginator = Paginator(messages_queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    unread_count = Message.objects.filter(
        recipient=user,
        is_read=False,
        deleted_by_recipient=False
    ).count()
    
    context = {
        'messages': page_obj,
        'current_tab': tab,
        'unread_count': unread_count,
        'total_received': Message.objects.filter(recipient=user, deleted_by_recipient=False).count(),
        'total_sent': Message.objects.filter(sender=user, deleted_by_sender=False).count(),
    }
    
    return render(request, 'communication/message_list.html', context)


@login_required
@csrf_protect
def message_compose(request):
    """Composer un nouveau message"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        if recipient_id and subject and content:
            try:
                recipient = User.objects.get(id=recipient_id)
                
                # Créer le message
                message = Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    subject=subject,
                    content=content
                )
                
                messages.success(request, 'Message envoyé avec succès!')
                return redirect('communication:message_list')
                
            except User.DoesNotExist:
                messages.error(request, 'Destinataire introuvable.')
        else:
            messages.error(request, 'Tous les champs sont obligatoires.')
    
    # Récupérer les utilisateurs possibles
    users = User.objects.exclude(id=request.user.id).order_by('first_name', 'last_name')
    
    context = {
        'users': users,
    }
    
    return render(request, 'communication/message_compose.html', context)


@login_required
def message_detail(request, message_id):
    """Détails d'un message"""
    message = get_object_or_404(
        Message,
        Q(id=message_id) &
        (Q(sender=request.user, deleted_by_sender=False) |
         Q(recipient=request.user, deleted_by_recipient=False))
    )
    
    # Marquer comme lu si c'est le destinataire
    if message.recipient == request.user:
        message.mark_as_read()
    
    context = {
        'message': message,
        'can_reply': True,
    }
    
    return render(request, 'communication/message_detail.html', context)


@login_required
def message_reply(request, message_id):
    """Répondre à un message"""
    return redirect(f"{reverse('communication:message_compose')}?reply_to={message_id}")


# VUES DES NOTIFICATIONS

@login_required
def notification_list(request):
    """Liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
        'total_count': notifications.count(),
    }
    
    return render(request, 'communication/notification_list.html', context)


@login_required
@require_http_methods(["POST"])
def notification_mark_read(request, notification_id):
    """Marquer une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'notification_id': notification_id
    })


@login_required
@require_http_methods(["POST"])
def notification_mark_all_read(request):
    """Marquer toutes les notifications comme lues"""
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    count = notifications.count()
    notifications.update(is_read=True, read_date=timezone.now())
    
    return JsonResponse({
        'success': True,
        'marked_count': count
    })


# VUES DES MESSAGES DE GROUPE (Placeholder)
def group_message_list(request):
    return HttpResponse("Messages de groupe - En développement")

def group_message_compose(request):
    return HttpResponse("Composer message de groupe - En développement")

def group_message_detail(request, message_id):
    return HttpResponse(f"Détail message de groupe {message_id} - En développement")


# VUES DU FORUM DE CLASSE

@login_required
def forum_index(request):
    """Page d'accueil du forum - Liste des classes/forums accessibles"""
    user = request.user
    accessible_classrooms = []
    
    if user.role in ['ADMIN', 'SUPER_ADMIN']:
        # Les admins voient toutes les classes
        from academic.models import ClassRoom
        accessible_classrooms = ClassRoom.objects.all()
    elif user.role == 'TEACHER':
        # Les enseignants voient leurs classes
        if hasattr(user, 'teacher_profile'):
            accessible_classrooms = user.teacher_profile.assigned_classes.all()
    elif user.role == 'STUDENT':
        # Les étudiants voient leur classe
        if hasattr(user, 'student_profile') and user.student_profile.current_class:
            accessible_classrooms = [user.student_profile.current_class]
    elif user.role == 'PARENT':
        # Les parents voient les classes de leurs enfants
        if hasattr(user, 'parent_profile'):
            children_classes = []
            for child in user.parent_profile.children.all():
                if child.current_class:
                    children_classes.append(child.current_class)
            accessible_classrooms = children_classes
    
    # Ajouter les statistiques pour chaque classe
    from .models import ForumTopic
    for classroom in accessible_classrooms:
        classroom.topics_count = ForumTopic.objects.filter(classroom=classroom).count()
        classroom.recent_topics = ForumTopic.objects.filter(classroom=classroom).order_by('-updated_at')[:3]
    
    context = {
        'accessible_classrooms': accessible_classrooms,
        'user': user,
    }
    
    return render(request, 'communication/forum/forum_index.html', context)


@login_required
def forum_classroom(request, classroom_id):
    """Forum d'une classe spécifique"""
    from academic.models import ClassRoom
    from .models import ForumTopic
    
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    
    # Vérifier les permissions d'accès
    if not can_user_access_classroom_forum(request.user, classroom):
        messages.error(request, "Vous n'avez pas accès au forum de cette classe.")
        return redirect('communication:forum_index')
    
    # Récupérer les topics
    topics = ForumTopic.objects.filter(
        classroom=classroom,
        is_approved=True
    ).select_related('author').prefetch_related('forum_posts')
    
    # Pagination
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Permissions pour créer des topics
    can_create_topic = can_user_create_topic(request.user, classroom)
    
    context = {
        'classroom': classroom,
        'topics': page_obj,
        'can_create_topic': can_create_topic,
        'user': request.user,
    }
    
    return render(request, 'communication/forum/forum_classroom.html', context)


@login_required
def forum_topic_detail(request, topic_id):
    """Détail d'un topic avec ses posts"""
    from .models import ForumTopic, ForumPost
    
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Vérifier les permissions d'accès
    if not topic.can_user_access(request.user):
        messages.error(request, "Vous n'avez pas accès à ce sujet.")
        return redirect('communication:forum_index')
    
    # Incrémenter les vues
    topic.increment_views()
    
    # Récupérer les posts
    posts = ForumPost.objects.filter(
        topic=topic,
        is_approved=True
    ).select_related('author').order_by('created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Permissions
    can_reply = can_user_create_post(request.user, topic)
    can_moderate = can_user_moderate_forum(request.user, topic.classroom)
    
    context = {
        'topic': topic,
        'posts': page_obj,
        'can_reply': can_reply,
        'can_moderate': can_moderate,
        'user': request.user,
    }
    
    return render(request, 'communication/forum/forum_topic_detail.html', context)


@login_required
@csrf_protect
def forum_topic_create(request, classroom_id):
    """Créer un nouveau topic"""
    from academic.models import ClassRoom
    from .models import ForumTopic
    
    classroom = get_object_or_404(ClassRoom, id=classroom_id)
    
    # Vérifier les permissions
    if not can_user_create_topic(request.user, classroom):
        messages.error(request, "Vous n'avez pas le droit de créer un sujet dans cette classe.")
        return redirect('communication:forum_classroom', classroom_id=classroom_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title and content:
            topic = ForumTopic.objects.create(
                title=title,
                content=content,
                classroom=classroom,
                author=request.user,
                is_approved=True  # Auto-approuvé pour les enseignants/admins
            )
            
            messages.success(request, 'Sujet créé avec succès!')
            return redirect('communication:forum_topic_detail', topic_id=topic.id)
        else:
            messages.error(request, 'Titre et contenu sont obligatoires.')
    
    context = {
        'classroom': classroom,
    }
    
    return render(request, 'communication/forum/forum_topic_create.html', context)


@login_required
@csrf_protect
def forum_post_create(request, topic_id):
    """Créer une réponse à un topic"""
    from .models import ForumTopic, ForumPost
    
    topic = get_object_or_404(ForumTopic, id=topic_id)
    
    # Vérifier les permissions
    if not can_user_create_post(request.user, topic):
        messages.error(request, "Vous n'avez pas le droit de répondre à ce sujet.")
        return redirect('communication:forum_topic_detail', topic_id=topic_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_post_id = request.POST.get('parent_post')
        
        if content:
            parent_post = None
            if parent_post_id:
                try:
                    parent_post = ForumPost.objects.get(id=parent_post_id, topic=topic)
                except ForumPost.DoesNotExist:
                    pass
            
            post = ForumPost.objects.create(
                topic=topic,
                author=request.user,
                content=content,
                parent_post=parent_post,
                is_approved=True
            )
            
            # Mettre à jour la date du topic
            topic.save()
            
            messages.success(request, 'Réponse ajoutée avec succès!')
            return redirect('communication:forum_topic_detail', topic_id=topic_id)
        else:
            messages.error(request, 'Le contenu est obligatoire.')
    
    return redirect('communication:forum_topic_detail', topic_id=topic_id)


# Fonctions utilitaires pour les permissions du forum

def can_user_access_classroom_forum(user, classroom):
    """Vérifie si un utilisateur peut accéder au forum d'une classe"""
    if user.role in ['ADMIN', 'SUPER_ADMIN']:
        return True
    elif user.role == 'TEACHER':
        return hasattr(user, 'teacher_profile') and classroom in user.teacher_profile.assigned_classes.all()
    elif user.role == 'STUDENT':
        return hasattr(user, 'student_profile') and user.student_profile.current_class == classroom
    elif user.role == 'PARENT':
        if hasattr(user, 'parent_profile'):
            children_classes = [child.current_class for child in user.parent_profile.children.all() if child.current_class]
            return classroom in children_classes
    return False


def can_user_create_topic(user, classroom):
    """Vérifie si un utilisateur peut créer un topic"""
    if user.role in ['ADMIN', 'SUPER_ADMIN', 'TEACHER']:
        return can_user_access_classroom_forum(user, classroom)
    # Les étudiants et parents peuvent généralement créer des topics
    return can_user_access_classroom_forum(user, classroom)


def can_user_create_post(user, topic):
    """Vérifie si un utilisateur peut créer un post"""
    if topic.is_locked and user.role not in ['ADMIN', 'SUPER_ADMIN', 'TEACHER']:
        return False
    return can_user_access_classroom_forum(user, topic.classroom)


def can_user_moderate_forum(user, classroom):
    """Vérifie si un utilisateur peut modérer le forum"""
    if user.role in ['ADMIN', 'SUPER_ADMIN']:
        return True
    elif user.role == 'TEACHER':
        return hasattr(user, 'teacher_profile') and classroom in user.teacher_profile.assigned_classes.all()
    return False


# VUES DES RESSOURCES (Placeholder)
def resource_list(request):
    return HttpResponse("Ressources - En développement")

def resource_upload(request):
    return HttpResponse("Upload ressource - En développement")

def resource_detail(request, resource_id):
    return HttpResponse(f"Détail ressource {resource_id} - En développement")

def resource_download(request, resource_id):
    return HttpResponse(f"Téléchargement ressource {resource_id} - En développement")
