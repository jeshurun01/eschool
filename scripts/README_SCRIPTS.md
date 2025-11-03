# 📋 SCRIPTS DE GESTION DE LA BASE DE DONNÉES

## Vue d'ensemble

Ce document décrit tous les scripts disponibles pour gérer la base de données de l'application eSchool.

---

## 🛠️ Scripts disponibles

### 1. `clean_and_setup.sh` - Réinitialisation complète ⭐ RECOMMANDÉ

**Description** : Script principal qui effectue un nettoyage complet et recrée une base de données vierge.

**Usage** :
```bash
bash scripts/clean_and_setup.sh
```

**Actions effectuées** :
1. ✅ Supprime `db.sqlite3`
2. ✅ Nettoie tous les caches Python
3. ✅ Vide les logs
4. ✅ Supprime les fichiers média temporaires
5. ✅ Nettoie toutes les migrations (sauf `__init__.py`)
6. ✅ Recrée les migrations
7. ✅ Applique les migrations

**Quand l'utiliser** :
- Quand vous voulez repartir de zéro
- Après avoir modifié des modèles Django
- En cas de corruption de la base de données
- Pour nettoyer complètement le projet

---

### 2. `reset_and_populate.py` - Génération de données de test

**Description** : Génère des données de test réalistes pour l'année académique 2025-2026.

**Usage** :
```bash
uv run python scripts/reset_and_populate.py
```

**Données générées** :
- 1 année académique (2025-2026)
- 12 niveaux (CP → Tle)
- 12 matières
- 12 classes
- 10 enseignants
- 68 élèves (5-7 par classe)
- 60 parents (30 couples)
- 784 sessions de cours
- 4400 présences
- 3583 notes
- 68 factures
- 135 paiements

**Durée d'exécution** : ~30 secondes

**Quand l'utiliser** :
- Après avoir exécuté `clean_and_setup.sh`
- Pour tester l'application avec des données réalistes
- Pour démonstration ou formation

---

### 3. `check_database.py` - Vérification de l'état

**Description** : Affiche un rapport détaillé de l'état de la base de données.

**Usage** :
```bash
uv run python scripts/check_database.py
```

**Informations affichées** :
- Année académique active
- Nombre d'utilisateurs par rôle
- Structure académique (classes, matières, inscriptions)
- Données académiques (sessions, présences, notes)
- Finances (factures, paiements, montants)
- Communication (annonces, messages)
- Vérifications d'intégrité

**Quand l'utiliser** :
- Pour vérifier rapidement l'état de la base
- Après la génération de données
- Pour déboguer des problèmes
- Pour obtenir des statistiques

---

### 4. `full_reset.sh` - Ancien script (DEPRECATED)

**Description** : Ancien script de nettoyage, remplacé par `clean_and_setup.sh`.

**Statut** : ⚠️ Obsolète, ne plus utiliser

**Utiliser à la place** : `clean_and_setup.sh`

---

## 🔄 Workflow recommandé

### Scénario 1 : Premier démarrage

```bash
# 1. Nettoyer et créer la base
bash scripts/clean_and_setup.sh

# 2. Générer les données de test
uv run python scripts/reset_and_populate.py

# 3. Vérifier que tout est OK
uv run python scripts/check_database.py

# 4. Lancer le serveur
uv run python manage.py runserver
```

---

### Scénario 2 : Réinitialisation rapide

```bash
# Option A : Tout réinitialiser (recommandé)
bash scripts/clean_and_setup.sh && uv run python scripts/reset_and_populate.py

# Option B : Seulement regénérer les données
# (Si la structure de la base n'a pas changé)
uv run python scripts/reset_and_populate.py
```

---

### Scénario 3 : Vérification après modifications

```bash
# 1. Vérifier l'état actuel
uv run python scripts/check_database.py

# 2. Si problème, réinitialiser
bash scripts/clean_and_setup.sh
uv run python scripts/reset_and_populate.py

# 3. Vérifier à nouveau
uv run python scripts/check_database.py
```

---

## 📝 Création d'un superutilisateur

### Méthode 1 : Avec le script de génération

Le script `reset_and_populate.py` ne crée PAS de superutilisateur automatiquement. Utilisez :

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

### Méthode 2 : Manuellement

```bash
uv run python manage.py createsuperuser
```

---

## ⚙️ Configuration

### Modifier l'année académique

Dans `scripts/reset_and_populate.py`, ligne 117-118 :

```python
academic_year = AcademicYear.objects.create(
    name="2025-2026",  # ← Modifier ici
    start_date=date(2025, 9, 1),  # ← Et ici
    end_date=date(2026, 6, 30),   # ← Et ici
    is_current=True
)
```

### Modifier le nombre d'élèves par classe

Dans `scripts/reset_and_populate.py`, ligne ~220 :

```python
students_per_class = random.randint(5, 7)  # ← Modifier ici
```

### Modifier le nombre d'enseignants

Dans `scripts/reset_and_populate.py`, ligne ~380 :

```python
for i in range(10):  # ← Modifier ici (actuellement 10)
    # Création d'enseignants...
```

---

## 🔍 Dépannage

### Problème : "no such table"

**Cause** : Les migrations ne sont pas appliquées

**Solution** :
```bash
bash scripts/clean_and_setup.sh
```

---

### Problème : "UNIQUE constraint failed"

**Cause** : Tentative de créer des données en double

**Solution** :
```bash
# Supprimer les données existantes d'abord
bash scripts/clean_and_setup.sh
uv run python scripts/reset_and_populate.py
```

---

### Problème : Script `reset_and_populate.py` échoue

**Cause** : Base de données corrompue ou migrations manquantes

**Solution** :
```bash
# Réinitialiser complètement
bash scripts/clean_and_setup.sh
uv run python scripts/reset_and_populate.py
```

---

### Problème : Données incohérentes

**Cause** : Script interrompu ou exécuté plusieurs fois

**Solution** :
```bash
# Vérifier l'état
uv run python scripts/check_database.py

# Si problème, réinitialiser
bash scripts/clean_and_setup.sh
uv run python scripts/reset_and_populate.py
```

---

## ⚠️ Avertissements

### À NE PAS FAIRE

❌ Ne supprimez **JAMAIS** les fichiers `__init__.py` dans les migrations  
❌ Ne modifiez **JAMAIS** les modèles pendant l'exécution d'un script  
❌ Ne lancez **JAMAIS** plusieurs scripts en parallèle  
❌ N'utilisez **JAMAIS** `rm -rf migrations/` directement

### À FAIRE

✅ Toujours utiliser `bash scripts/clean_and_setup.sh` pour nettoyer  
✅ Toujours vérifier avec `check_database.py` après génération  
✅ Toujours sauvegarder avant des tests majeurs :
```bash
cp db.sqlite3 db.sqlite3.backup
```

---

## 📊 Statistiques typiques

Après génération complète avec `reset_and_populate.py` :

| Élément | Quantité | Notes |
|---------|----------|-------|
| Utilisateurs totaux | 139 | 1 admin + 10 profs + 68 élèves + 60 parents |
| Classes | 12 | Une par niveau |
| Inscriptions actives | 68 | Tous les élèves inscrits |
| Sessions de cours | 784 | ~65 par classe |
| Présences | 4400 | ~90% présents |
| Notes | 3583 | Moyenne ~14/20 |
| Factures | 68 | Une par élève |
| Paiements | 135 | ~2 par élève |
| Total encaissé | ~11M FCFA | Varie selon génération |

---

## 🔗 Liens utiles

- **Guide complet** : `docs/DATABASE_RESET_GUIDE.md`
- **Documentation Django** : https://docs.djangoproject.com/
- **Scripts** : `/scripts/`

---

## 📞 Support

En cas de problème non résolu :

1. Consultez `docs/DATABASE_RESET_GUIDE.md`
2. Vérifiez les logs : `tail -f logs/django.log`
3. Vérifiez les migrations : `uv run python manage.py showmigrations`
4. Testez la base : `uv run python manage.py check`

---

**Dernière mise à jour** : 13 octobre 2025  
**Version** : 1.0  
**Année académique** : 2025-2026
