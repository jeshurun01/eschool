# 🧹 GUIDE DE RÉINITIALISATION DE LA BASE DE DONNÉES

## Vue d'ensemble

Ce guide explique comment nettoyer complètement la base de données et régénérer les données de test pour l'année académique **2025-2026**.

---

## 📋 Prérequis

- Python 3.12+ installé
- `uv` (gestionnaire de packages) installé
- Accès au répertoire du projet : `/home/jeshurun-nasser/dev/py/django-app/eschool`

---

## 🚀 Processus de réinitialisation complète

### Option 1 : Script automatique (RECOMMANDÉ)

Utilisez le script tout-en-un qui gère tout automatiquement :

```bash
cd /home/jeshurun-nasser/dev/py/django-app/eschool
bash scripts/clean_and_setup.sh
```

Ce script effectue les opérations suivantes :
1. ✅ Supprime la base de données `db.sqlite3`
2. ✅ Nettoie tous les caches Python (`__pycache__`, `.pyc`, `.pyo`)
3. ✅ Vide les logs Django
4. ✅ Supprime les fichiers média temporaires
5. ✅ Nettoie toutes les migrations (sauf `__init__.py`)
6. ✅ Recrée les migrations pour toutes les applications
7. ✅ Applique toutes les migrations

---

### Option 2 : Étapes manuelles

Si vous préférez contrôler chaque étape :

#### Étape 1 : Supprimer la base de données et les caches

```bash
# Supprimer la base de données
rm db.sqlite3

# Nettoyer les caches Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Vider les logs
> logs/django.log
```

#### Étape 2 : Nettoyer les migrations

```bash
# Pour chaque application (accounts, academic, communication, finance)
find accounts/migrations -type f -name "*.py" ! -name "__init__.py" -delete
find academic/migrations -type f -name "*.py" ! -name "__init__.py" -delete
find communication/migrations -type f -name "*.py" ! -name "__init__.py" -delete
find finance/migrations -type f -name "*.py" ! -name "__init__.py" -delete
```

#### Étape 3 : Recréer les migrations

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

---

## 📊 Génération des données de test

### Exécuter le script de génération

```bash
uv run python scripts/reset_and_populate.py
```

### Créer le superutilisateur

```bash
uv run python manage.py shell -c "
from accounts.models import User
admin = User.objects.create_superuser(
    email='admin@eschool.cd',
    password='admin123',
    first_name='Admin',
    last_name='Principal',
    role='ADMIN'
)
print(f'✅ Superutilisateur créé: {admin.email}')
"
```

---

## 📈 Données générées

### Année académique

- **Nom** : 2025-2026
- **Début** : 1er septembre 2025
- **Fin** : 30 juin 2026
- **Statut** : Active (is_current=True)

### Structure académique

| Type | Quantité | Détails |
|------|----------|---------|
| Niveaux | 12 | CP, CE1, CE2, CM1, CM2, 6ème, 5ème, 4ème, 3ème, 2nde, 1ère, Tle |
| Matières | 12 | Français, Mathématiques, Sciences, Histoire-Géo, etc. |
| Classes | 12 | Une classe par niveau |
| Enseignants | 10 | Avec attributions multiples |
| Élèves | 68 | 5-7 par classe, répartition équitable |
| Parents | 60 | 30 couples, max 3 enfants par famille |

### Données académiques

| Type | Quantité |
|------|----------|
| Inscriptions | 68 |
| Attributions enseignants | 98 |
| Sessions de cours | 784 |
| Présences (session) | 4400 |
| Résumés journaliers | 2040 |
| Devoirs | 42 |
| Notes | 3583 |

### Données financières

| Type | Quantité |
|------|----------|
| Types de frais | 5 |
| Structures de frais | 36 |
| Factures | 68 |
| Paiements | 135 |

---

## 🔑 Comptes de test

### Superutilisateur (Admin)

```
Email: admin@eschool.cd
Mot de passe: admin123
Rôle: ADMIN
```

### Enseignant

```
Email: marie.dubois@eschool.com
Mot de passe: password123
Rôle: TEACHER
```

### Parent

```
Email: sophie.dubois@gmail.com
Mot de passe: password123
Rôle: PARENT
```

### Élèves

```
6ème: alexandre.simon0@student.eschool.com / password123
1ère: raphael.vincent0@student.eschool.com / password123
```

> **Note importante** : Les accents sont supprimés des emails pour faciliter la connexion
> Exemple : Véronique → veronique, François → francois

---

## 🌐 Accès à l'application

- **Application principale** : http://localhost:8000/
- **Interface admin** : http://localhost:8000/admin/
- **Comptes** : http://localhost:8000/accounts/

---

## 🔧 Dépannage

### Problème : "no such table"

**Solution** : Réexécutez les migrations

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Problème : Migrations en conflit

**Solution** : Supprimez toutes les migrations et recommencez

```bash
bash scripts/clean_and_setup.sh
```

### Problème : Données corrompues

**Solution** : Réinitialisez complètement

```bash
bash scripts/clean_and_setup.sh
uv run python scripts/reset_and_populate.py
```

---

## ⚠️ Avertissements

### ❌ À NE PAS FAIRE

1. **Ne supprimez PAS** les fichiers `__init__.py` dans les dossiers migrations
2. **Ne modifiez PAS** les modèles pendant la génération des données
3. **Ne lancez PAS** plusieurs scripts de génération en parallèle

### ✅ Bonnes pratiques

1. **Toujours** utiliser `uv run` pour les commandes Python
2. **Toujours** vérifier que la base est vide avant de générer des données
3. **Toujours** créer le superutilisateur après la génération
4. **Sauvegarder** la base de données avant des tests majeurs :
   ```bash
   cp db.sqlite3 db.sqlite3.backup
   ```

---

## 📝 Historique des modifications

### 2025-10-13
- ✅ Changement année académique : 2024-2025 → **2025-2026**
- ✅ Création du script `clean_and_setup.sh`
- ✅ Correction du script `reset_and_populate.py`
- ✅ Suppression des erreurs de table manquante
- ✅ Documentation complète du processus

---

## 📚 Scripts disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `clean_and_setup.sh` | Nettoyage complet + migrations | `bash scripts/clean_and_setup.sh` |
| `reset_and_populate.py` | Génération données test | `uv run python scripts/reset_and_populate.py` |
| `full_reset.sh` | Ancien script (deprecated) | N/A |

---

## 🆘 Support

En cas de problème persistant :

1. Vérifiez les logs : `tail -f logs/django.log`
2. Vérifiez les migrations : `uv run python manage.py showmigrations`
3. Testez la base : `uv run python manage.py check`

---

**Dernière mise à jour** : 13 octobre 2025
