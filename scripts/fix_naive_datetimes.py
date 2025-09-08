#!/usr/bin/env python
"""
Script pour corriger les dates naïves dans la base de données.
Convertit toutes les dates naïves en dates avec timezone.
"""

import os
import sys
import django
from datetime import datetime
from django.utils import timezone
from django.conf import settings

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from finance.models import Payment

def fix_naive_datetimes():
    """Corrige toutes les dates naïves dans la base de données"""
    
    print("🔧 Correction des dates naïves...")
    
    # Correction des User.date_joined
    naive_users = User.objects.filter(date_joined__isnull=False)
    user_count = 0
    
    for user in naive_users:
        if user.date_joined and timezone.is_naive(user.date_joined):
            # Convertir en date aware avec la timezone configurée
            user.date_joined = timezone.make_aware(user.date_joined)
            user.save(update_fields=['date_joined'])
            user_count += 1
            print(f"✅ User {user.email}: date_joined corrigée")
    
    # Correction des Payment.payment_date
    naive_payments = Payment.objects.filter(payment_date__isnull=False)
    payment_count = 0
    
    for payment in naive_payments:
        if payment.payment_date and timezone.is_naive(payment.payment_date):
            # Convertir en date aware avec la timezone configurée
            payment.payment_date = timezone.make_aware(payment.payment_date)
            payment.save(update_fields=['payment_date'])
            payment_count += 1
            print(f"✅ Payment {payment.pk}: payment_date corrigée")
    
    print(f"\n🎯 Résumé des corrections:")
    print(f"   - Users corrigés: {user_count}")
    print(f"   - Payments corrigés: {payment_count}")
    print(f"   - Total: {user_count + payment_count} dates corrigées")
    
    if user_count == 0 and payment_count == 0:
        print("✅ Aucune date naïve trouvée - Base de données déjà correcte!")
    else:
        print("✅ Toutes les dates naïves ont été corrigées!")

def verify_timezone_settings():
    """Vérifie la configuration des timezones"""
    print("\n📋 Vérification de la configuration timezone:")
    print(f"   - USE_TZ: {settings.USE_TZ}")
    print(f"   - TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   - Timezone actuelle: {timezone.get_current_timezone()}")
    print(f"   - Datetime maintenant: {timezone.now()}")

if __name__ == "__main__":
    print("🕐 Démarrage de la correction des timezones...")
    
    # Vérifier la configuration
    verify_timezone_settings()
    
    # Corriger les dates naïves
    fix_naive_datetimes()
    
    print("\n🎉 Script terminé avec succès!")
