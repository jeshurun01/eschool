#!/usr/bin/env python
"""
Script pour corriger les datetime naïfs dans la base de données
"""
import os
import django
from django.utils import timezone
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User
from finance.models import Payment

def fix_naive_datetimes():
    """Convertit les datetime naïfs en datetime avec timezone"""
    
    print("🔧 Correction des datetime naïfs...")
    
    # Corriger les date_joined des utilisateurs
    naive_users = User.objects.filter(date_joined__isnull=False)
    updated_users = 0
    
    for user in naive_users:
        if user.date_joined and timezone.is_naive(user.date_joined):
            # Convertir en datetime avec timezone
            aware_datetime = timezone.make_aware(user.date_joined)
            user.date_joined = aware_datetime
            user.save(update_fields=['date_joined'])
            updated_users += 1
    
    print(f"✅ {updated_users} utilisateurs corrigés (date_joined)")
    
    # Corriger les payment_date des paiements
    naive_payments = Payment.objects.filter(payment_date__isnull=False)
    updated_payments = 0
    
    for payment in naive_payments:
        if payment.payment_date and timezone.is_naive(payment.payment_date):
            # Convertir en datetime avec timezone
            aware_datetime = timezone.make_aware(payment.payment_date)
            payment.payment_date = aware_datetime
            payment.save(update_fields=['payment_date'])
            updated_payments += 1
    
    print(f"✅ {updated_payments} paiements corrigés (payment_date)")
    
    print("🎉 Correction terminée ! Plus d'avertissements de timezone.")

if __name__ == '__main__':
    fix_naive_datetimes()
