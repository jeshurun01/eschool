#!/usr/bin/env python3
"""
Script pour tester les conversions Decimal et identifier les problèmes
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from decimal import Decimal, InvalidOperation

def test_decimal_conversions():
    """Teste différents cas de conversion Decimal"""
    
    test_cases = [
        # Cas valides
        "100.50",
        "0",
        "1000",
        "99.99",
        "0.01",
        
        # Cas avec formatage différent
        "100,50",  # Virgule au lieu du point
        " 100.50 ",  # Espaces
        "1,234.56",  # Séparateur de milliers
        
        # Cas invalides
        "",
        "abc",
        "100.50.25",
        "100,50,25",
        None,
        "inf",
        "nan"
    ]
    
    print("=== Test des conversions Decimal ===\n")
    
    for i, test_value in enumerate(test_cases):
        print(f"Test {i+1}: '{test_value}'")
        
        try:
            # Test direct
            if test_value is None:
                print("  ❌ Valeur None - ignorée")
                continue
                
            if not test_value or not str(test_value).strip():
                print("  ❌ Valeur vide - ignorée")
                continue
            
            # Nettoyage comme dans le code
            clean_value = str(test_value).strip().replace(',', '.')
            result = Decimal(clean_value)
            print(f"  ✅ Succès: {result}")
            
        except (ValueError, InvalidOperation) as e:
            print(f"  ❌ Erreur: {type(e).__name__} - {e}")
        except Exception as e:
            print(f"  ❌ Erreur inattendue: {type(e).__name__} - {e}")
        
        print()

def test_invoice_data():
    """Teste avec des données réelles de facture"""
    
    print("=== Test avec données de facture ===\n")
    
    from finance.models import Invoice
    
    try:
        # Prendre la première facture disponible
        invoice = Invoice.objects.first()
        if invoice:
            print(f"Facture trouvée: {invoice.invoice_number}")
            print(f"  Sous-total: {invoice.subtotal}")
            print(f"  Remise: {invoice.discount}")
            print(f"  Total: {invoice.total_amount}")
            
            # Test de modification de remise
            test_discounts = ["10.50", "0", "5,25", "invalid", ""]
            
            for discount_str in test_discounts:
                print(f"\nTest remise: '{discount_str}'")
                try:
                    if discount_str and discount_str.strip():
                        clean_discount = discount_str.strip().replace(',', '.')
                        discount = Decimal(clean_discount)
                        if discount >= 0 and discount <= invoice.subtotal:
                            print(f"  ✅ Remise valide: {discount}")
                        else:
                            print(f"  ❌ Remise hors limites: {discount} (max: {invoice.subtotal})")
                    else:
                        print("  ⚠️  Remise vide - ignorée")
                except (ValueError, InvalidOperation) as e:
                    print(f"  ❌ Erreur conversion: {e}")
        else:
            print("Aucune facture trouvée dans la base de données")
            
    except Exception as e:
        print(f"Erreur lors du test: {e}")

if __name__ == "__main__":
    test_decimal_conversions()
    test_invoice_data()
    print("\n=== Tests terminés ===")
