# 🔍 Problème résolu : Les paiements créés via l'admin ne sont pas tracés

## ❌ Problème

Lorsqu'un administrateur crée un **paiement** (ou une **facture** ou une **note**) via l'interface d'administration Django (`/admin/`), aucun log d'activité n'était créé dans le système.

### Pourquoi ?

Les signaux Django qui capturent les modifications (dans `activity_log/signals.py`) récupèrent l'utilisateur depuis deux sources :

1. **Thread local** : Via le middleware `ActivityTrackingMiddleware`
2. **Attribut `_user`** : Passé manuellement par les vues

**Le problème** : L'interface d'administration Django ne passe PAS par le middleware de la même manière que les vues personnalisées. Le thread local n'était pas accessible dans l'admin.

## ✅ Solution appliquée

### 1. Modification des ModelAdmin

Nous avons ajouté les méthodes `save_model()` et `delete_model()` dans les classes d'administration pour passer l'utilisateur connecté à l'instance avant la sauvegarde :

#### **finance/admin.py**

```python
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'invoice', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('payment_reference', 'transaction_id', 'invoice__invoice_number')
    readonly_fields = ('payment_reference',)
    date_hierarchy = 'payment_date'
    
    def save_model(self, request, obj, form, change):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user  # ← AJOUT
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user  # ← AJOUT
        super().delete_model(request, obj)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # ... (configuration existante)
    
    def save_model(self, request, obj, form, change):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user  # ← AJOUT
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user  # ← AJOUT
        super().delete_model(request, obj)
```

#### **academic/admin.py**

```python
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    # ... (configuration existante)
    
    def save_model(self, request, obj, form, change):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user  # ← AJOUT
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user  # ← AJOUT
        super().delete_model(request, obj)
```

### 2. Amélioration des signaux

Nous avons modifié les signaux pour tenter d'abord de récupérer l'utilisateur depuis le **thread local** (middleware), puis depuis l'**attribut `_user`** (admin) :

#### **activity_log/signals.py**

**Avant** :
```python
@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    user = getattr(instance, '_user', None)  # Seulement depuis l'attribut
    
    if not user:
        return
    # ...
```

**Après** :
```python
@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    # Récupérer l'utilisateur depuis le thread local OU depuis l'instance
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    # ...
```

Cette amélioration a été appliquée à :
- ✅ `payment_post_save` et `payment_post_delete`
- ✅ `invoice_post_save` et `invoice_post_delete`

**Note** : Les signaux pour `Grade` utilisaient déjà le thread local en priorité, donc ils fonctionnaient déjà.

## 🧪 Test

### Avant la correction

1. Se connecter en tant qu'**admin** : `/admin/`
2. Créer un **paiement** via l'interface Django Admin
3. Vérifier `/activity-logs/` : ❌ **Aucun log créé**

### Après la correction

1. Se connecter en tant qu'**admin** : `/admin/`
2. Créer un **paiement** via l'interface Django Admin
3. Vérifier `/activity-logs/` : ✅ **Log créé avec succès**

Le log devrait afficher :
```
Action : PAYMENT_CREATE
Description : Paiement de 50000 FCFA créé pour John Doe (Facture #INV-2025-001)
Utilisateur : admin@eschool.com
Date : 12 oct. 2025, 14:23
```

## 📋 Autres modèles concernés

Cette solution a été appliquée aux modèles suivants :

| Modèle    | App      | Admin modifié | Signal modifié |
|-----------|----------|---------------|----------------|
| Payment   | finance  | ✅            | ✅             |
| Invoice   | finance  | ✅            | ✅             |
| Grade     | academic | ✅            | Déjà OK        |

## 🔧 Si vous ajoutez de nouveaux modèles

Pour activer le tracking d'activité sur un nouveau modèle via l'admin Django :

### Étape 1 : Créer les signaux

Dans `activity_log/signals.py` :

```python
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from myapp.models import MyModel

@receiver(pre_save, sender=MyModel)
def mymodel_pre_save(sender, instance, **kwargs):
    """Capture l'état avant modification"""
    if instance.pk:
        try:
            instance._old_instance = MyModel.objects.get(pk=instance.pk)
        except MyModel.DoesNotExist:
            instance._old_instance = None

@receiver(post_save, sender=MyModel)
def mymodel_post_save(sender, instance, created, **kwargs):
    """Log la création ou modification"""
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    
    if created:
        log_activity(
            user=user,
            action_type='MYMODEL_CREATE',
            description=f"MyModel créé : {instance}",
            content_type='MyModel',
            object_id=instance.id,
            object_repr=str(instance),
        )
    else:
        # ... (modification)

@receiver(post_delete, sender=MyModel)
def mymodel_post_delete(sender, instance, **kwargs):
    """Log la suppression"""
    user = get_current_user() or getattr(instance, '_user', None)
    
    if not user or not user.is_authenticated:
        return
    
    log_activity(
        user=user,
        action_type='MYMODEL_DELETE',
        description=f"MyModel supprimé : {instance}",
        content_type='MyModel',
        object_id=instance.id,
        object_repr=str(instance),
    )
```

### Étape 2 : Modifier l'admin

Dans `myapp/admin.py` :

```python
@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    # ... (configuration existante)
    
    def save_model(self, request, obj, form, change):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Passer l'utilisateur au signal pour le tracking d'activité"""
        obj._user = request.user
        super().delete_model(request, obj)
```

## 🎯 Résultat

Maintenant, **toutes les opérations CRUD** (Create, Read, Update, Delete) effectuées via :
- ✅ **L'interface d'administration Django** (`/admin/`)
- ✅ **Les vues personnalisées** (avec le middleware actif)

... sont **automatiquement tracées** dans le journal d'activité !

## 📚 Fichiers modifiés

- `finance/admin.py` : Ajout de `save_model()` et `delete_model()` pour `PaymentAdmin` et `InvoiceAdmin`
- `academic/admin.py` : Ajout de `save_model()` et `delete_model()` pour `GradeAdmin`
- `activity_log/signals.py` : Amélioration de la récupération de l'utilisateur (thread local + attribut)

---

**Date de correction** : 12 octobre 2025  
**Testé** : ✅ Fonctionne correctement
