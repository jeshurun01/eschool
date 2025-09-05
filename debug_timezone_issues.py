#!/usr/bin/env python
"""
Script pour identifier et corriger les datetime naïfs spécifiques qui causent les avertissements
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
from django.db import connection

def find_and_fix_specific_issues():
    """Identifie et corrige les problèmes spécifiques de datetime"""
    
    print("🔍 Recherche des datetime problématiques...")
    
    # Rechercher les paiements avec des dates spécifiques mentionnées dans l'erreur
    problematic_payments = Payment.objects.filter(
        payment_date__date__in=['2025-08-06', '2025-08-29']
    )
    
    print(f"💰 {problematic_payments.count()} paiements trouvés avec dates problématiques")
    
    for payment in problematic_payments:
        if timezone.is_naive(payment.payment_date):
            print(f"  - Paiement {payment.id}: {payment.payment_date} (naïf)")
            payment.payment_date = timezone.make_aware(payment.payment_date)
            payment.save()
            print(f"    ✅ Corrigé: {payment.payment_date}")
        else:
            print(f"  - Paiement {payment.id}: {payment.payment_date} (déjà aware)")
    
    # Rechercher les utilisateurs avec date_joined problématique
    problematic_users = User.objects.filter(
        date_joined__date='2025-08-29'
    )
    
    print(f"👤 {problematic_users.count()} utilisateurs trouvés avec date_joined problématique")
    
    for user in problematic_users:
        if timezone.is_naive(user.date_joined):
            print(f"  - Utilisateur {user.email}: {user.date_joined} (naïf)")
            user.date_joined = timezone.make_aware(user.date_joined)
            user.save()
            print(f"    ✅ Corrigé: {user.date_joined}")
        else:
            print(f"  - Utilisateur {user.email}: {user.date_joined} (déjà aware)")
    
    # Mettre à jour tous les datetime potentiellement naïfs
    print("\n🛠️  Correction en lot de tous les datetime naïfs...")
    
    # Requête SQL pour identifier les champs datetime
    with connection.cursor() as cursor:
        # Vérifier les paiements
        cursor.execute("""
            SELECT id, payment_date FROM finance_payment 
            WHERE payment_date IS NOT NULL
        """)
        payment_results = cursor.fetchall()
        
        print(f"📊 Analysé {len(payment_results)} paiements dans la base")
        
        # Vérifier les utilisateurs
        cursor.execute("""
            SELECT id, email, date_joined FROM accounts_user 
            WHERE date_joined IS NOT NULL
        """)
        user_results = cursor.fetchall()
        
        print(f"📊 Analysé {len(user_results)} utilisateurs dans la base")
    
    print("🎉 Analyse terminée !")

if __name__ == '__main__':
    find_and_fix_specific_issues()
