#!/usr/bin/env python
"""
Script de test pour le système de suivi d'activité
Teste la création manuelle de logs et l'affichage
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from activity_log.models import ActivityLog, log_activity
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def test_activity_log():
    print("=== Test du système de suivi d'activité ===\n")
    
    # 1. Vérifier l'état initial
    initial_count = ActivityLog.objects.count()
    print(f"1. État initial : {initial_count} logs existants")
    
    # 2. Obtenir un utilisateur (ou en créer un)
    user = User.objects.first()
    if not user:
        print("   ⚠️  Aucun utilisateur trouvé, création d'un utilisateur de test...")
        user = User.objects.create_user(
            username='test_activity',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        print(f"   ✓ Utilisateur créé : {user.get_full_name()}")
    else:
        print(f"   ✓ Utilisateur trouvé : {user.get_full_name()}")
    
    # 3. Créer un log de test (GRADE_CREATE)
    print("\n2. Création d'un log de test (GRADE_CREATE)...")
    log1 = log_activity(
        user=user,
        action_type='GRADE_CREATE',
        description='Note créée pour test - Mathématiques - Score: 15/20',
        content_type='Grade',
        object_id=999,
        object_repr='Test Grade - Math - 15/20',
        new_values={
            'subject': 'Mathématiques',
            'score': 15,
            'max_score': 20,
            'coefficient': 2
        }
    )
    print(f"   ✓ Log créé avec ID: {log1.id}")
    print(f"   - Type: {log1.get_action_type_display()}")
    print(f"   - Catégorie: {log1.action_category}")
    print(f"   - Icône: {log1.icon_class}")
    
    # 4. Créer un log de modification (INVOICE_UPDATE)
    print("\n3. Création d'un log de modification (INVOICE_UPDATE)...")
    log2 = log_activity(
        user=user,
        action_type='INVOICE_UPDATE',
        description='Facture #2024-001 modifiée - Montant changé',
        content_type='Invoice',
        object_id=123,
        object_repr='Facture #2024-001',
        old_values={
            'amount': 1000.00,
            'status': 'draft'
        },
        new_values={
            'amount': 1200.00,
            'status': 'sent'
        }
    )
    print(f"   ✓ Log créé avec ID: {log2.id}")
    print(f"   - Changements détectés: {len(log2.get_changes())} champs")
    for field, change in log2.get_changes().items():
        print(f"     * {field}: {change['old']} → {change['new']}")
    
    # 5. Créer un log de suppression (PAYMENT_DELETE)
    print("\n4. Création d'un log de suppression (PAYMENT_DELETE)...")
    log3 = log_activity(
        user=user,
        action_type='PAYMENT_DELETE',
        description='Paiement #PAY-789 supprimé',
        content_type='Payment',
        object_id=789,
        object_repr='Paiement #PAY-789 - 500.00€',
        old_values={
            'amount': 500.00,
            'method': 'cash',
            'date': '2024-10-01'
        }
    )
    print(f"   ✓ Log créé avec ID: {log3.id}")
    
    # 6. Créer un log de connexion (USER_LOGIN)
    print("\n5. Création d'un log de connexion (USER_LOGIN)...")
    log4 = log_activity(
        user=user,
        action_type='USER_LOGIN',
        description=f'Connexion de {user.get_full_name()}',
        content_type='User',
        object_id=user.id,
        object_repr=str(user)
    )
    print(f"   ✓ Log créé avec ID: {log4.id}")
    
    # 7. Statistiques finales
    print("\n6. Statistiques finales...")
    final_count = ActivityLog.objects.count()
    new_logs = final_count - initial_count
    print(f"   ✓ Total de logs : {final_count}")
    print(f"   ✓ Nouveaux logs créés : {new_logs}")
    
    # 8. Répartition par type
    print("\n7. Répartition par type d'action...")
    action_counts = {}
    for action_code, action_label in ActivityLog.ACTION_TYPES:
        count = ActivityLog.objects.filter(action_type=action_code).count()
        if count > 0:
            action_counts[action_label] = count
    
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {action}: {count}")
    
    # 9. Logs récents
    print("\n8. Les 5 derniers logs...")
    recent_logs = ActivityLog.objects.all()[:5]
    for log in recent_logs:
        print(f"   - [{log.timestamp.strftime('%H:%M:%S')}] {log.user.get_full_name() if log.user else 'Système'} : {log.get_action_type_display()}")
        print(f"     {log.description[:60]}...")
    
    # 10. Test des propriétés
    print("\n9. Test des propriétés du modèle...")
    test_log = ActivityLog.objects.first()
    if test_log:
        print(f"   - __str__: {test_log}")
        print(f"   - action_category: {test_log.action_category}")
        print(f"   - action_verb: {test_log.action_verb}")
        print(f"   - icon_class: {test_log.icon_class}")
        print(f"   - color_class: {test_log.color_class}")
    
    print("\n" + "="*50)
    print("✅ Test terminé avec succès!")
    print(f"✅ {new_logs} nouveaux logs créés")
    print(f"✅ Système de suivi d'activité opérationnel")
    print("="*50)
    
    print("\n📝 Prochaines étapes :")
    print("   1. Visiter http://localhost:8000/activity-logs/")
    print("   2. Créer/modifier des notes pour tester le tracking automatique")
    print("   3. Vérifier dans l'admin : /admin/activity_log/activitylog/")

if __name__ == '__main__':
    try:
        test_activity_log()
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
