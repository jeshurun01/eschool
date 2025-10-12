"""
Signaux pour le tracking automatique des activités
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone

from academic.models import Grade
from finance.models import Invoice, Payment
from activity_log.models import ActivityLog, log_activity
from activity_log.utils import get_current_user, get_current_request


# ==================== GRADES ====================

@receiver(pre_save, sender=Grade)
def grade_pre_save(sender, instance, **kwargs):
    """Capture l'état avant modification d'une note"""
    if instance.pk:
        try:
            instance._old_instance = Grade.objects.get(pk=instance.pk)
        except Grade.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Grade)
def grade_post_save(sender, instance, created, **kwargs):
    """Log la création ou modification d'une note"""
    # Récupérer l'utilisateur depuis le thread local ou le teacher
    user = get_current_user() or (instance.teacher.user if instance.teacher else None)
    
    if not user or not user.is_authenticated:
        return
    
    request = get_current_request()
    
    if created:
        # Création d'une nouvelle note
        description = (
            f"Note créée pour {instance.student.user.get_full_name()} "
            f"en {instance.subject.name}: {instance.score}/{instance.max_score}"
        )
        
        log_activity(
            user=user,
            action_type='GRADE_CREATE',
            description=description,
            content_type='Grade',
            object_id=instance.id,
            object_repr=str(instance),
            new_values={
                'student': instance.student.user.get_full_name(),
                'subject': instance.subject.name,
                'score': float(instance.score),
                'max_score': float(instance.max_score),
                'coefficient': float(instance.coefficient) if instance.coefficient else 1.0,
                'evaluation_type': instance.evaluation_type,
            },
            request=getattr(instance, '_request', None)
        )
    else:
        # Modification d'une note existante
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            description = (
                f"Note modifiée pour {instance.student.user.get_full_name()} "
                f"en {instance.subject.name}"
            )
            
            old_values = {
                'score': float(old_instance.score),
                'max_score': float(old_instance.max_score),
                'coefficient': float(old_instance.coefficient) if old_instance.coefficient else 1.0,
                'evaluation_type': old_instance.evaluation_type,
            }
            
            new_values = {
                'score': float(instance.score),
                'max_score': float(instance.max_score),
                'coefficient': float(instance.coefficient) if instance.coefficient else 1.0,
                'evaluation_type': instance.evaluation_type,
            }
            
            log_activity(
                user=user,
                action_type='GRADE_UPDATE',
                description=description,
                content_type='Grade',
                object_id=instance.id,
                object_repr=str(instance),
                old_values=old_values,
                new_values=new_values,
                request=getattr(instance, '_request', None)
            )


@receiver(post_delete, sender=Grade)
def grade_post_delete(sender, instance, **kwargs):
    """Log la suppression d'une note"""
    user = getattr(instance, '_user', None) or (instance.teacher.user if instance.teacher else None)
    
    if not user:
        return
    
    description = (
        f"Note supprimée pour {instance.student.user.get_full_name()} "
        f"en {instance.subject.name}: {instance.score}/{instance.max_score}"
    )
    
    log_activity(
        user=user,
        action_type='GRADE_DELETE',
        description=description,
        content_type='Grade',
        object_id=instance.id,
        object_repr=str(instance),
        old_values={
            'student': instance.student.user.get_full_name(),
            'subject': instance.subject.name,
            'score': float(instance.score),
            'max_score': float(instance.max_score),
            'coefficient': float(instance.coefficient) if instance.coefficient else 1.0,
            'evaluation_type': instance.evaluation_type,
        },
        request=getattr(instance, '_request', None)
    )


# ==================== INVOICES ====================

@receiver(pre_save, sender=Invoice)
def invoice_pre_save(sender, instance, **kwargs):
    """Capture l'état avant modification d'une facture"""
    if instance.pk:
        try:
            instance._old_instance = Invoice.objects.get(pk=instance.pk)
        except Invoice.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Invoice)
def invoice_post_save(sender, instance, created, **kwargs):
    """Log la création ou modification d'une facture"""
    # Récupérer l'utilisateur depuis le thread local OU depuis l'instance
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    
    if created:
        # Création d'une nouvelle facture
        description = (
            f"Facture #{instance.invoice_number} créée pour "
            f"{instance.student.user.get_full_name()}: {instance.total_amount} FCFA"
        )
        
        log_activity(
            user=user,
            action_type='INVOICE_CREATE',
            description=description,
            content_type='Invoice',
            object_id=instance.id,
            object_repr=str(instance),
            new_values={
                'student': instance.student.user.get_full_name(),
                'invoice_number': instance.invoice_number,
                'total_amount': float(instance.total_amount),
                'status': instance.status,
                'due_date': instance.due_date.isoformat() if instance.due_date else None,
            },
            request=getattr(instance, '_request', None)
        )
    else:
        # Modification d'une facture existante
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            description = f"Facture #{instance.invoice_number} modifiée"
            
            old_values = {
                'total_amount': float(old_instance.total_amount),
                'status': old_instance.status,
                'due_date': old_instance.due_date.isoformat() if old_instance.due_date else None,
            }
            
            new_values = {
                'total_amount': float(instance.total_amount),
                'status': instance.status,
                'due_date': instance.due_date.isoformat() if instance.due_date else None,
            }
            
            log_activity(
                user=user,
                action_type='INVOICE_UPDATE',
                description=description,
                content_type='Invoice',
                object_id=instance.id,
                object_repr=str(instance),
                old_values=old_values,
                new_values=new_values,
                request=getattr(instance, '_request', None)
            )


@receiver(post_delete, sender=Invoice)
def invoice_post_delete(sender, instance, **kwargs):
    """Log la suppression d'une facture"""
    # Récupérer l'utilisateur depuis le thread local OU depuis l'instance
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    
    description = (
        f"Facture #{instance.invoice_number} supprimée pour "
        f"{instance.student.user.get_full_name()}: {instance.total_amount} FCFA"
    )
    
    log_activity(
        user=user,
        action_type='INVOICE_DELETE',
        description=description,
        content_type='Invoice',
        object_id=instance.id,
        object_repr=str(instance),
        old_values={
            'student': instance.student.user.get_full_name(),
            'invoice_number': instance.invoice_number,
            'total_amount': float(instance.total_amount),
            'status': instance.status,
        },
        request=getattr(instance, '_request', None)
    )


# ==================== PAYMENTS ====================

@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    """Capture l'état avant modification d'un paiement"""
    if instance.pk:
        try:
            instance._old_instance = Payment.objects.get(pk=instance.pk)
        except Payment.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Log la création ou modification d'un paiement"""
    # Récupérer l'utilisateur depuis le thread local OU depuis l'instance
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    
    if created:
        # Création d'un nouveau paiement
        description = (
            f"Paiement de {instance.amount} FCFA créé pour "
            f"{instance.invoice.student.user.get_full_name()} "
            f"(Facture #{instance.invoice.invoice_number})"
        )
        
        log_activity(
            user=user,
            action_type='PAYMENT_CREATE',
            description=description,
            content_type='Payment',
            object_id=instance.id,
            object_repr=str(instance),
            new_values={
                'invoice': instance.invoice.invoice_number,
                'amount': float(instance.amount),
                'payment_method': instance.payment_method.name if instance.payment_method else 'N/A',
                'status': instance.status,
                'payment_date': instance.payment_date.isoformat() if instance.payment_date else None,
            },
            request=getattr(instance, '_request', None)
        )
    else:
        # Modification d'un paiement existant
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            description = f"Paiement modifié (Facture #{instance.invoice.invoice_number})"
            
            old_values = {
                'amount': float(old_instance.amount),
                'payment_method': old_instance.payment_method.name if old_instance.payment_method else 'N/A',
                'status': old_instance.status,
                'payment_date': old_instance.payment_date.isoformat() if old_instance.payment_date else None,
            }
            
            new_values = {
                'amount': float(instance.amount),
                'payment_method': instance.payment_method.name if instance.payment_method else 'N/A',
                'status': instance.status,
                'payment_date': instance.payment_date.isoformat() if instance.payment_date else None,
            }
            
            log_activity(
                user=user,
                action_type='PAYMENT_UPDATE',
                description=description,
                content_type='Payment',
                object_id=instance.id,
                object_repr=str(instance),
                old_values=old_values,
                new_values=new_values,
                request=getattr(instance, '_request', None)
            )


@receiver(post_delete, sender=Payment)
def payment_post_delete(sender, instance, **kwargs):
    """Log la suppression d'un paiement"""
    # Récupérer l'utilisateur depuis le thread local OU depuis l'instance
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    
    description = (
        f"Paiement de {instance.amount} FCFA supprimé "
        f"(Facture #{instance.invoice.invoice_number})"
    )
    
    log_activity(
        user=user,
        action_type='PAYMENT_DELETE',
        description=description,
        content_type='Payment',
        object_id=instance.id,
        object_repr=str(instance),
        old_values={
            'invoice': instance.invoice.invoice_number,
            'amount': float(instance.amount),
            'payment_method': instance.payment_method.name if instance.payment_method else 'N/A',
            'status': instance.status,
        },
        request=getattr(instance, '_request', None)
    )


# ==================== USER LOGIN/LOGOUT ====================

@receiver(user_logged_in)
def user_login_log(sender, request, user, **kwargs):
    """Log la connexion d'un utilisateur"""
    description = f"{user.get_full_name()} s'est connecté"
    
    log_activity(
        user=user,
        action_type='USER_LOGIN',
        description=description,
        content_type='User',
        object_id=user.id,
        object_repr=str(user),
        request=request
    )


@receiver(user_logged_out)
def user_logout_log(sender, request, user, **kwargs):
    """Log la déconnexion d'un utilisateur"""
    if user:
        description = f"{user.get_full_name()} s'est déconnecté"
        
        log_activity(
            user=user,
            action_type='USER_LOGOUT',
            description=description,
            content_type='User',
            object_id=user.id,
            object_repr=str(user),
            request=request
        )
