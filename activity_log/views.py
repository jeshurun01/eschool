"""
Vues pour le système de suivi d'activité
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from activity_log.models import ActivityLog
from core.decorators.permissions import admin_required


@admin_required
def activity_log_list(request):
    """Liste des activités avec filtres et recherche"""
    # Récupérer les paramètres de filtre
    search_query = request.GET.get('search', '')
    action_type = request.GET.get('action_type', '')
    user_id = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    category = request.GET.get('category', '')
    
    # Requête de base
    logs = ActivityLog.objects.select_related('user').all()
    
    # Filtres
    if search_query:
        logs = logs.filter(
            Q(description__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(object_repr__icontains=search_query)
        )
    
    if action_type:
        logs = logs.filter(action_type=action_type)
    
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    
    if date_to:
        # Ajouter 1 jour pour inclure toute la journée
        logs = logs.filter(timestamp__lt=date_to)
    
    if category:
        logs = logs.filter(action_type__startswith=category)
    
    # Statistiques
    today = timezone.now().date()
    stats = {
        'total': logs.count(),
        'today': logs.filter(timestamp__date=today).count(),
        'this_week': logs.filter(timestamp__gte=today - timedelta(days=7)).count(),
        'this_month': logs.filter(timestamp__gte=today - timedelta(days=30)).count(),
    }
    
    # Statistiques par catégorie
    category_stats = {}
    for action_type_tuple in ActivityLog.ACTION_TYPES:
        action_code = action_type_tuple[0]
        category_name = action_code.split('_')[0] if '_' in action_code else action_code
        if category_name not in category_stats:
            category_stats[category_name] = 0
        category_stats[category_name] += logs.filter(action_type=action_code).count()
    
    # Top utilisateurs actifs
    top_users = logs.values(
        'user__id',
        'user__first_name',
        'user__last_name',
        'user__role'
    ).annotate(
        activity_count=Count('id')
    ).order_by('-activity_count')[:10]
    
    # Pagination
    paginator = Paginator(logs, 50)  # 50 logs par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'category_stats': category_stats,
        'top_users': top_users,
        'action_types': ActivityLog.ACTION_TYPES,
        'search_query': search_query,
        'selected_action_type': action_type,
        'selected_user': user_id,
        'date_from': date_from,
        'date_to': date_to,
        'selected_category': category,
        'categories': ['GRADE', 'INVOICE', 'PAYMENT', 'ATTENDANCE', 'DOCUMENT', 'SESSION', 'USER'],
    }
    
    return render(request, 'activity_log/activity_log_list.html', context)


@admin_required
def activity_log_detail(request, log_id):
    """Détails d'un log d'activité"""
    log = get_object_or_404(ActivityLog, id=log_id)
    
    # Récupérer les logs liés (même objet)
    related_logs = ActivityLog.objects.filter(
        content_type=log.content_type,
        object_id=log.object_id
    ).exclude(id=log.id).select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'log': log,
        'related_logs': related_logs,
        'changes': log.get_changes(),
    }
    
    return render(request, 'activity_log/activity_log_detail.html', context)


@admin_required
def user_activity_log(request, user_id):
    """Historique d'activité d'un utilisateur spécifique"""
    from accounts.models import User
    
    user = get_object_or_404(User, id=user_id)
    logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')
    
    # Statistiques de l'utilisateur
    stats = {
        'total': logs.count(),
        'today': logs.filter(timestamp__date=timezone.now().date()).count(),
        'this_week': logs.filter(timestamp__gte=timezone.now() - timedelta(days=7)).count(),
        'this_month': logs.filter(timestamp__gte=timezone.now() - timedelta(days=30)).count(),
    }
    
    # Actions par type
    action_breakdown = {}
    for action_type_tuple in ActivityLog.ACTION_TYPES:
        action_code = action_type_tuple[0]
        count = logs.filter(action_type=action_code).count()
        if count > 0:
            action_breakdown[action_type_tuple[1]] = count
    
    # Pagination
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'target_user': user,
        'page_obj': page_obj,
        'stats': stats,
        'action_breakdown': action_breakdown,
    }
    
    return render(request, 'activity_log/user_activity_log.html', context)
