# 🔐 Plan d'Implémentation - Contrôle d'Accès par Rôle (RBAC)

## 📋 Vue d'ensemble

Ce document définit l'architecture et le plan d'implémentation pour le système de contrôle d'accès basé sur les rôles dans l'application Django eSchool.

---

## 🔒 Règles d'accès par rôle

### 1. 👨‍🏫 Enseignant

**Accès autorisé :**
- ✅ Ses propres cours uniquement
- ✅ Les classes dans lesquelles il enseigne
- ✅ Les élèves appartenant à ces classes
- ✅ Les présences concernant ses élèves et ses sessions
- ✅ Les notes liées à ses propres cours
- ✅ Les communications avec ses élèves/parents

**Accès refusé :**
- ❌ Cours, classes, élèves ou notes d'autres enseignants
- ❌ Données financières globales
- ❌ Administration système

---

### 2. 👨‍🎓 Élève

**Accès autorisé :**
- ✅ Ses propres informations personnelles
- ✅ Ses propres parents/tuteurs
- ✅ Ses propres notes dans les cours auxquels il est inscrit
- ✅ Les classes dans lesquelles il est inscrit
- ✅ Les annonces qui lui sont destinées
- ✅ Son historique de présences

**Accès refusé :**
- ❌ Données d'autres élèves
- ❌ Notes d'autres élèves
- ❌ Informations financières détaillées
- ❌ Administration

---

### 3. 👨‍👩‍👧‍👦 Parent / Tuteur

**Accès autorisé :**
- ✅ Les activités, notes et informations scolaires de ses propres enfants
- ✅ Les communications concernant ses enfants
- ✅ Les factures et paiements de ses enfants
- ✅ Les présences de ses enfants

**Accès refusé :**
- ❌ Données des autres enfants
- ❌ Informations sur les autres familles
- ❌ Administration système

---

### 4. 👥 Staff (selon permissions définies par le Superuser)

**Accès configurable :**
- 🔧 Données dans le périmètre assigné par le Superuser
- 🔧 Exemple : staff responsable du niveau "Secondaire" → accès uniquement aux données de ce niveau
- 🔧 Peut inclure : gestion des inscriptions, communications, rapports limités

**Accès refusé :**
- ❌ Données en dehors de son périmètre
- ❌ Administration complète du système

---

### 5. 🔑 Superuser

**Accès total :**
- ✅ Intégralité de l'application, sans restriction
- ✅ Gestion des utilisateurs et leurs rôles
- ✅ Configuration des groupes et permissions
- ✅ Toutes les données sans exception
- ✅ Administration complète du système

---

## 📝 Plan d'implémentation

### Phase 1 : Architecture de base
- [ ] **Middleware de contrôle d'accès**
  - Créer un middleware custom pour vérifier les permissions
  - Intégrer avec le système d'authentification Django
  
- [ ] **Decorators de permission**
  - `@teacher_required`
  - `@student_required` 
  - `@parent_required`
  - `@staff_required`
  - `@superuser_required`

- [ ] **Mixins pour les vues basées sur les classes**
  - `TeacherAccessMixin`
  - `StudentAccessMixin`
  - `ParentAccessMixin`
  - `StaffAccessMixin`

### Phase 2 : Filtrage des données
- [ ] **QuerySet personnalisés**
  - Filtres automatiques basés sur le rôle utilisateur
  - Méthodes pour chaque modèle (`filter_for_teacher()`, `filter_for_student()`, etc.)

- [ ] **Managers personnalisés**
  - `TeacherManager` pour les cours et classes
  - `StudentManager` pour les notes et présences
  - `ParentManager` pour les enfants associés

### Phase 3 : Sécurisation des vues
- [ ] **Module Academic**
  - Sécuriser `grade_list`, `grade_add`, `student_grades`
  - Filtrer les classes selon l'enseignant
  - Restreindre l'accès aux présences

- [ ] **Module Finance**
  - Limiter l'accès aux paiements selon le rôle
  - Filtrer les factures par élève/parent
  - Masquer les données sensibles

- [ ] **Module Communication**
  - Filtrer les annonces par destinataire
  - Limiter l'accès aux forums
  - Contrôler l'envoi de messages

### Phase 4 : Interface utilisateur adaptative
- [ ] **Templates conditionnels**
  - Affichage des menus selon le rôle
  - Masquage des fonctionnalités non autorisées
  - Messages d'erreur personnalisés

- [ ] **Dashboards spécialisés**
  - Interface enseignant optimisée
  - Vue élève simplifiée
  - Dashboard parent focalisé sur les enfants

### Phase 5 : Tests et validation
- [ ] **Tests unitaires**
  - Tests de permissions pour chaque rôle
  - Vérification des filtres de données
  - Tests d'accès non autorisé

- [ ] **Tests d'intégration**
  - Scénarios complets par rôle
  - Navigation entre modules
  - Gestion des erreurs

---

## 🛠️ Implémentation technique

### Structure des fichiers à créer/modifier :

```
eschool/
├── core/
│   ├── middleware/
│   │   └── rbac_middleware.py
│   ├── decorators/
│   │   └── permissions.py
│   └── mixins/
│       └── access_mixins.py
├── accounts/
│   ├── managers.py (à modifier)
│   └── permissions.py (nouveau)
├── academic/
│   ├── managers.py (nouveau)
│   └── views.py (à modifier)
├── finance/
│   ├── managers.py (nouveau)
│   └── views.py (à modifier)
└── communication/
    ├── managers.py (nouveau)
    └── views.py (à modifier)
```

### Technologies utilisées :
- **Django Groups & Permissions** : Base du système de rôles
- **Custom Middleware** : Contrôle d'accès automatique
- **QuerySet Filtering** : Filtrage transparent des données
- **Template Tags** : Affichage conditionnel dans les templates

---

## 🎯 Objectifs de sécurité

1. **Isolation complète des données** entre les rôles
2. **Principe du moindre privilège** : accès minimal nécessaire
3. **Traçabilité** des accès et modifications
4. **Facilité de maintenance** et d'extension
5. **Performance optimisée** malgré les contrôles

---

## 📊 Métriques de succès

- [ ] **0 fuite de données** entre rôles différents
- [ ] **Tests de couverture** > 95% pour les permissions
- [ ] **Performance** : < 10ms overhead par requête
- [ ] **Facilité d'usage** : navigation intuitive par rôle
- [ ] **Maintenance** : ajout de nouveaux rôles en < 1 jour

---

## 🚀 Prochaines étapes

1. **Analyser l'architecture actuelle** des modèles et vues
2. **Créer les groupes Django** pour chaque rôle
3. **Implémenter le middleware RBAC** de base
4. **Sécuriser les vues critiques** (notes, finances)
5. **Tester avec des utilisateurs réels** de chaque rôle

---

*Document créé le : 8 septembre 2025*  
*Version : 1.0*  
*Auteur : Équipe de développement eSchool*
