#!/usr/bin/env python
"""
Script de validation des timezones - Vérifie qu'il n'y a plus de dates naïves
"""

import os
import sys
import django
import warnings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from finance.models import Payment
from django.utils import timezone
from django.conf import settings

def validate_timezone_configuration():
    """Valide la configuration des timezones"""
    print("🔍 Validation de la configuration timezone...")
    print(f"   ✅ USE_TZ: {settings.USE_TZ}")
    print(f"   ✅ TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   ✅ Timezone active: {timezone.get_current_timezone()}")
    print(f"   ✅ Datetime maintenant: {timezone.now()}")
    
    if not settings.USE_TZ:
        print("   ⚠️  WARNING: USE_TZ est désactivé!")
        return False
    
    return True

def validate_database_datetimes():
    """Valide que toutes les dates en base sont timezone-aware"""
    print("\n🔍 Validation des dates en base de données...")
    
    # Vérifier les Users
    naive_users = 0
    total_users = 0
    
    for user in User.objects.filter(date_joined__isnull=False):
        total_users += 1
        if user.date_joined and timezone.is_naive(user.date_joined):
            naive_users += 1
            print(f"   ❌ User {user.email}: date_joined naïve")
    
    print(f"   ✅ Users: {total_users} vérifiés, {naive_users} naïfs")
    
    # Vérifier les Payments
    naive_payments = 0
    total_payments = 0
    
    for payment in Payment.objects.filter(payment_date__isnull=False):
        total_payments += 1
        if payment.payment_date and timezone.is_naive(payment.payment_date):
            naive_payments += 1
            print(f"   ❌ Payment {payment.pk}: payment_date naïve")
    
    print(f"   ✅ Payments: {total_payments} vérifiés, {naive_payments} naïfs")
    
    total_naive = naive_users + naive_payments
    total_checked = total_users + total_payments
    
    print(f"\n📊 Résumé: {total_checked} dates vérifiées, {total_naive} naïves")
    
    return total_naive == 0

def test_warning_capture():
    """Test de capture des warnings timezone"""
    print("\n🔍 Test de capture des warnings...")
    
    # Activer la capture des warnings
    warnings.resetwarnings()
    warnings.simplefilter('always')
    
    # Créer une liste pour capturer les warnings
    warning_list = []
    
    def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
        if "DateTimeField" in str(message) and "naive datetime" in str(message):
            warning_list.append(str(message))
    
    # Installer le handler personnalisé
    old_showwarning = warnings.showwarning
    warnings.showwarning = custom_warning_handler
    
    try:
        # Lire toutes les données pour déclencher d'éventuels warnings
        list(User.objects.all())
        list(Payment.objects.all())
        
        if warning_list:
            print(f"   ❌ {len(warning_list)} warnings détectés:")
            for warning in warning_list:
                print(f"      - {warning}")
            return False
        else:
            print("   ✅ Aucun warning timezone détecté")
            return True
            
    finally:
        # Restaurer le handler original
        warnings.showwarning = old_showwarning

def main():
    """Fonction principale de validation"""
    print("🕐 Démarrage de la validation des timezones...")
    
    # Valider la configuration
    config_ok = validate_timezone_configuration()
    
    # Valider les données
    data_ok = validate_database_datetimes()
    
    # Tester la capture des warnings
    warnings_ok = test_warning_capture()
    
    # Résultat final
    print("\n" + "="*50)
    print("🎯 RÉSULTAT DE LA VALIDATION")
    print("="*50)
    
    if config_ok and data_ok and warnings_ok:
        print("✅ ✅ ✅ SUCCÈS: Toutes les validations passées!")
        print("✅ Configuration timezone correcte")
        print("✅ Aucune date naïve en base")
        print("✅ Aucun warning timezone détecté")
        print("\n🎉 Le système est exempt de problèmes timezone!")
        return True
    else:
        print("❌ ÉCHEC: Des problèmes ont été détectés")
        if not config_ok:
            print("❌ Configuration timezone incorrecte")
        if not data_ok:
            print("❌ Dates naïves détectées en base")
        if not warnings_ok:
            print("❌ Warnings timezone détectés")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
