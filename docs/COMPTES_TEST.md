# 🔑 Comptes de Test - eSchool

Ce document liste tous les comptes de test créés par le script `scripts/reset_and_populate.py`.

**Mot de passe universel :** `password123`

## 📧 Important : Emails sans accents

Les accents sont automatiquement supprimés des emails pour faciliter la connexion :
- `Véronique` → `veronique.durand@gmail.com`
- `François` → `francois.petit@gmail.com`
- `Élisabeth` → `elisabeth.bonnet@gmail.com`

## 👨‍🏫 Comptes Enseignants (10)

| Email | Matière principale |
|-------|-------------------|
| marie.dubois@eschool.com | Français |
| jean.martin@eschool.com | Mathématiques |
| sophie.bernard@eschool.com | Anglais |
| pierre.durand@eschool.com | Histoire-Géographie |
| isabelle.moreau@eschool.com | Sciences Physiques |
| thomas.laurent@eschool.com | SVT |
| catherine.simon@eschool.com | Éducation Physique |
| nicolas.michel@eschool.com | Informatique |
| emilie.lefebvre@eschool.com | Arts Plastiques |
| alexandre.garcia@eschool.com | Espagnol |

## 👨‍👩‍👧‍👦 Comptes Parents (60 - 30 couples)

### Couples 1-10
| Couple | Mère | Père |
|--------|------|------|
| 1 | sophie.dubois@gmail.com | marc.dubois@gmail.com |
| 2 | marie.martin@gmail.com | pierre.martin@gmail.com |
| 3 | claire.bernard@gmail.com | jean.bernard@gmail.com |
| 4 | isabelle.petit@gmail.com | francois.petit@gmail.com |
| 5 | catherine.robert@gmail.com | philippe.robert@gmail.com |
| 6 | nathalie.richard@gmail.com | laurent.richard@gmail.com |
| 7 | veronique.durand@gmail.com | alain.durand@gmail.com |
| 8 | sandrine.leroy@gmail.com | michel.leroy@gmail.com |
| 9 | sylvie.moreau@gmail.com | patrick.moreau@gmail.com |
| 10 | christine.simon@gmail.com | daniel.simon@gmail.com |

### Couples 11-20
| Couple | Mère | Père |
|--------|------|------|
| 11 | brigitte.laurent@gmail.com | thierry.laurent@gmail.com |
| 12 | monique.lefebvre@gmail.com | gerard.lefebvre@gmail.com |
| 13 | annie.roux@gmail.com | christian.roux@gmail.com |
| 14 | nicole.morel@gmail.com | dominique.morel@gmail.com |
| 15 | martine.fournier@gmail.com | pascal.fournier@gmail.com |
| 16 | francoise.girard@gmail.com | jacques.girard@gmail.com |
| 17 | elisabeth.bonnet@gmail.com | andre.bonnet@gmail.com |
| 18 | jacqueline.fontaine@gmail.com | bernard.fontaine@gmail.com |
| 19 | chantal.rousseau@gmail.com | christophe.rousseau@gmail.com |
| 20 | danielle.vincent@gmail.com | stephane.vincent@gmail.com |

### Couples 21-30
| Couple | Mère | Père |
|--------|------|------|
| 21 | valerie.muller@gmail.com | olivier.muller@gmail.com |
| 22 | laurence.lefevre@gmail.com | bruno.lefevre@gmail.com |
| 23 | corinne.mercier@gmail.com | eric.mercier@gmail.com |
| 24 | agnes.blanc@gmail.com | didier.blanc@gmail.com |
| 25 | patricia.guerin@gmail.com | yves.guerin@gmail.com |
| 26 | helene.boyer@gmail.com | serge.boyer@gmail.com |
| 27 | odette.garnier@gmail.com | rene.garnier@gmail.com |
| 28 | laure.chevalier@gmail.com | henri.chevalier@gmail.com |
| 29 | pauline.francois@gmail.com | georges.francois@gmail.com |
| 30 | juliette.legrand@gmail.com | louis.legrand@gmail.com |

## 👨‍🎓 Comptes Élèves (74 - 5-7 par classe)

### Exemples par niveau

| Niveau | Email exemple | Nombre d'élèves |
|--------|--------------|-----------------|
| CP | dylan.dubois0@student.eschool.com | 5-7 |
| CE1 | antoine.martin0@student.eschool.com | 5-7 |
| CE2 | marc.robert0@student.eschool.com | 5-7 |
| CM1 | ryan.durand0@student.eschool.com | 5-7 |
| CM2 | sacha.moreau0@student.eschool.com | 5-7 |
| 6ème | liam.laurent0@student.eschool.com | 5-7 |
| 5ème | leo.roux0@student.eschool.com | 5-7 |
| 4ème | david.fournier0@student.eschool.com | 5-7 |
| 3ème | arthur.bonnet0@student.eschool.com | 5-7 |
| 2nde | sacha.rousseau0@student.eschool.com | 5-7 |
| 1ère | tom.muller0@student.eschool.com | 5-7 |
| Tle | adam.mercier0@student.eschool.com | 5-7 |

**Note :** Les élèves sont liés à leurs parents (maximum 3 enfants par couple).

## 🌐 Accès à l'Application

- **Application :** http://127.0.0.1:8000/
- **Interface Admin Django :** http://127.0.0.1:8000/admin/

## 📊 Statistiques des Données de Test

- **Années scolaires :** 1 (2024-2025)
- **Niveaux :** 12 (CP → Tle)
- **Matières :** 12
- **Classes :** 12 (1 par niveau)
- **Enseignants :** 10
- **Parents :** 60 (30 couples)
- **Élèves :** 74
- **Sessions de cours :** ~800
- **Notes :** ~4000
- **Factures :** 74
- **Paiements :** ~140

## 🔄 Régénération des Données

Pour régénérer toutes les données de test :

```bash
cd /home/jeshurun-nasser/dev/py/django-app/eschool
uv run python scripts/reset_and_populate.py
```

⚠️ **Attention :** Cette commande supprime TOUTES les données existantes (sauf le superuser) !

## 🐛 Problèmes Connus Résolus

### ✅ Problème de connexion des parents (Résolu)
**Symptôme :** Impossible de se connecter avec les comptes parents

**Cause :** Les emails contenaient des caractères accentués (é, è, à, ç, etc.) qui causaient des problèmes d'authentification.

**Solution :** 
- Ajout de la fonction `remove_accents()` utilisant `unicodedata`
- Tous les emails sont maintenant créés sans accents
- Les noms affichés gardent les accents (Véronique, François, etc.)
- Seuls les emails sont modifiés (veronique.durand@gmail.com)

**Emails corrigés (exemples) :**
- ❌ `véronique.durand@gmail.com` → ✅ `veronique.durand@gmail.com`
- ❌ `françois.petit@gmail.com` → ✅ `francois.petit@gmail.com`
- ❌ `élisabeth.bonnet@gmail.com` → ✅ `elisabeth.bonnet@gmail.com`
- ❌ `éric.mercier@gmail.com` → ✅ `eric.mercier@gmail.com`

## 📝 Notes

1. Tous les utilisateurs utilisent le même mot de passe : `password123`
2. Les élèves sont répartis équitablement (5-7 par classe)
3. Chaque couple de parents a entre 1 et 3 enfants
4. Les présences sont générées pour les 30 derniers jours
5. Les notes sont générées aléatoirement (entre 8 et 20)
6. Les factures sont en statut PAID ou PARTIAL

---

**Dernière mise à jour :** 5 octobre 2025
**Version du script :** 2.0 (avec suppression des accents)
