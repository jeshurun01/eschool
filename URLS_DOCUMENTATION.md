# 📚 Documentation des URLs - eSchool

Cette documentation liste toutes les URLs disponibles dans l'application eSchool.

## 🏠 URLs Principales (core/urls.py)

| URL | Nom | Description |
|-----|-----|-------------|
| `/` | `home` | Page d'accueil |
| `/admin/` | - | Interface d'administration Django |
| `/accounts/` | - | Module de gestion des comptes |
| `/academic/` | - | Module académique |
| `/finance/` | - | Module financier |
| `/communication/` | - | Module de communication |
| `/api/` | - | API REST |

---

## 👥 Module Accounts (accounts/urls.py)

### 🔐 Authentification
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/register/` | `accounts:register` | Inscription d'un nouvel utilisateur |
| `/accounts/login/` | `accounts:login` | Connexion |
| `/accounts/logout/` | `accounts:logout` | Déconnexion |
| `/accounts/change-password/` | `accounts:change_password` | Changement de mot de passe |

### 📊 Dashboards
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/` | `accounts:dashboard` | Dashboard principal |
| `/accounts/admin-dashboard/` | `accounts:admin_dashboard` | Dashboard administrateur |
| `/accounts/teacher-dashboard/` | `accounts:teacher_dashboard` | Dashboard enseignant |
| `/accounts/parent-dashboard/` | `accounts:parent_dashboard` | Dashboard parent |

### 👤 Profil Utilisateur
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/profile/` | `accounts:profile` | Profil utilisateur |
| `/accounts/profile/edit/` | `accounts:profile_edit` | Modification du profil |

### 👥 Gestion des Utilisateurs (Admin)
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/users/` | `accounts:user_list` | Liste des utilisateurs |
| `/accounts/users/create/` | `accounts:user_create` | Créer un utilisateur |
| `/accounts/users/<user_id>/` | `accounts:user_detail` | Détails d'un utilisateur |
| `/accounts/users/<user_id>/edit/` | `accounts:user_edit` | Modifier un utilisateur |
| `/accounts/users/<user_id>/toggle-active/` | `accounts:user_toggle_active` | Activer/désactiver un utilisateur |

### 🎓 Gestion des Élèves
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/students/` | `accounts:student_list` | Liste des élèves |
| `/accounts/students/create/` | `accounts:student_create` | Créer un élève |
| `/accounts/students/<student_id>/` | `accounts:student_detail` | Détails d'un élève |
| `/accounts/students/<student_id>/edit/` | `accounts:student_edit` | Modifier un élève |

### 👨‍👩‍👧‍👦 Gestion des Parents
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/parents/` | `accounts:parent_list` | Liste des parents |
| `/accounts/parents/create/` | `accounts:parent_create` | Créer un parent |
| `/accounts/parents/bulk-import/` | `accounts:parent_bulk_import` | Import en masse des parents |
| `/accounts/parents/export-csv/` | `accounts:parent_export_csv` | Export CSV des parents |
| `/accounts/parents/<parent_id>/` | `accounts:parent_detail` | Détails d'un parent |
| `/accounts/parents/<parent_id>/edit/` | `accounts:parent_edit` | Modifier un parent |
| `/accounts/parents/<parent_id>/delete/` | `accounts:parent_delete` | Supprimer un parent |
| `/accounts/parents/<parent_id>/assign-children/` | `accounts:parent_assign_children` | Assigner des enfants |
| `/accounts/parents/<parent_id>/toggle-active/` | `accounts:parent_toggle_active` | Activer/désactiver un parent |

### 👨‍🏫 Gestion des Enseignants
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/teachers/` | `accounts:teacher_list` | Liste des enseignants |
| `/accounts/teachers/create/` | `accounts:teacher_create` | Créer un enseignant |
| `/accounts/teachers/<teacher_id>/` | `accounts:teacher_detail` | Détails d'un enseignant |
| `/accounts/teachers/<teacher_id>/edit/` | `accounts:teacher_edit` | Modifier un enseignant |

### 📋 Vues Spécialisées
| URL | Nom | Description |
|-----|-----|-------------|
| `/accounts/children-overview/` | `accounts:admin_children_overview` | Vue d'ensemble des enfants (Admin) |
| `/accounts/student/grades/` | `accounts:student_grades_detail` | Notes de l'élève |
| `/accounts/student/attendance/` | `accounts:student_attendance_detail` | Présences de l'élève |
| `/accounts/student/finance/` | `accounts:student_finance_detail` | Finances de l'élève |
| `/accounts/student/calendar/` | `accounts:student_academic_calendar` | Calendrier académique |
| `/accounts/parent/children/` | `accounts:parent_children_overview` | Vue d'ensemble des enfants (Parent) |
| `/accounts/parent/child/<child_id>/` | `accounts:parent_child_detail` | Détails d'un enfant |
| `/accounts/parent/communication/` | `accounts:parent_communication_center` | Centre de communication parent |

---

## 🎓 Module Académique (academic/urls.py)

### 📅 Années Scolaires
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/academic-years/` | `academic:academic_year_list` | Liste des années scolaires |
| `/academic/academic-years/create/` | `academic:academic_year_create` | Créer une année scolaire |

### 🎚️ Niveaux
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/levels/` | `academic:level_list` | Liste des niveaux |
| `/academic/levels/create/` | `academic:level_create` | Créer un niveau |

### 📚 Matières
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/subjects/` | `academic:subject_list` | Liste des matières |
| `/academic/subjects/create/` | `academic:subject_create` | Créer une matière |

### 🏫 Classes
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/classes/` | `academic:classroom_list` | Liste des classes |
| `/academic/classes/create/` | `academic:classroom_create` | Créer une classe |
| `/academic/classes/<classroom_id>/` | `academic:classroom_detail` | Détails d'une classe |
| `/academic/classes/<classroom_id>/edit/` | `academic:classroom_edit` | Modifier une classe |
| `/academic/classes/<classroom_id>/enrollments/` | `academic:enrollment_manage` | Gérer les inscriptions |
| `/academic/classes/<classroom_id>/students/` | `academic:classroom_students` | Élèves de la classe |
| `/academic/classes/<classroom_id>/timetable/` | `academic:classroom_timetable` | Emploi du temps |

### 📖 Cours
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/courses/<assignment_id>/` | `academic:course_detail` | Détails d'un cours |

### 🕐 Emplois du Temps
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/timetables/` | `academic:timetable_list` | Liste des emplois du temps |
| `/academic/timetables/create/` | `academic:timetable_create` | Créer un emploi du temps |

### ✅ Présences
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/attendance/` | `academic:attendance_list` | Liste des présences |
| `/academic/attendance/take/` | `academic:attendance_take` | Prendre les présences |
| `/academic/attendance/class/<classroom_id>/` | `academic:attendance_class` | Présences d'une classe |
| `/academic/api/classroom/<classroom_id>/students/` | `academic:get_classroom_students` | API - Élèves d'une classe |

### 📊 Notes
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/grades/` | `academic:grade_list` | Liste des notes |
| `/academic/grades/add/` | `academic:grade_add` | Ajouter une note |
| `/academic/grades/student/<student_id>/` | `academic:student_grades` | Notes d'un élève |
| `/academic/grades/class/<classroom_id>/` | `academic:class_grades` | Notes d'une classe |

### 📄 Documents
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/documents/` | `academic:document_list` | Liste des documents |
| `/academic/documents/add/` | `academic:document_add` | Ajouter un document |
| `/academic/documents/<document_id>/` | `academic:document_detail` | Détails d'un document |
| `/academic/documents/<document_id>/edit/` | `academic:document_edit` | Modifier un document |
| `/academic/documents/<document_id>/delete/` | `academic:document_delete` | Supprimer un document |
| `/academic/documents/<document_id>/view/` | `academic:document_view` | Voir un document |
| `/academic/documents/subject/<subject_id>/` | `academic:document_subject_list` | Documents d'une matière |

### 📋 Bulletins et Rapports
| URL | Nom | Description |
|-----|-----|-------------|
| `/academic/reports/bulletin/<student_id>/` | `academic:student_bulletin` | Bulletin d'un élève |
| `/academic/reports/class/<classroom_id>/` | `academic:class_report` | Rapport de classe |

---

## 💰 Module Finance (finance/urls.py)

### 💸 Types de Frais
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/fee-types/` | `finance:fee_type_list` | Liste des types de frais |
| `/finance/fee-types/create/` | `finance:fee_type_create` | Créer un type de frais |
| `/finance/fee-structures/` | `finance:fee_structure_list` | Structure des frais |
| `/finance/fee-structures/create/` | `finance:fee_structure_create` | Créer une structure de frais |
| `/finance/fee-structures/create/<fee_type_id>/` | `finance:fee_structure_create_for_type` | Créer pour un type |

### 🧾 Factures
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/invoices/` | `finance:invoice_list` | Liste des factures |
| `/finance/invoices/create/` | `finance:invoice_create` | Créer une facture |
| `/finance/invoices/<invoice_id>/` | `finance:invoice_detail` | Détails d'une facture |
| `/finance/invoices/<invoice_id>/edit/` | `finance:invoice_edit` | Modifier une facture |
| `/finance/invoices/<invoice_id>/pdf/` | `finance:invoice_pdf` | PDF de la facture |
| `/finance/invoices/generate/` | `finance:invoice_generate` | Générer des factures |

### 💳 Paiements
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/payments/` | `finance:payment_list` | Liste des paiements |
| `/finance/payments/create/` | `finance:payment_create` | Créer un paiement |
| `/finance/payments/<payment_id>/` | `finance:payment_detail` | Détails d'un paiement |

### 🎓 Bourses
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/scholarships/` | `finance:scholarship_list` | Liste des bourses |
| `/finance/scholarships/create/` | `finance:scholarship_create` | Créer une bourse |
| `/finance/scholarships/applications/` | `finance:scholarship_application_list` | Demandes de bourse |

### 💼 Dépenses
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/expenses/` | `finance:expense_list` | Liste des dépenses |
| `/finance/expenses/create/` | `finance:expense_create` | Créer une dépense |
| `/finance/expenses/<expense_id>/` | `finance:expense_detail` | Détails d'une dépense |

### 💰 Paie
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/payroll/` | `finance:payroll_list` | Liste de la paie |
| `/finance/payroll/create/` | `finance:payroll_create` | Créer une paie |
| `/finance/payroll/<payroll_id>/` | `finance:payroll_detail` | Détails de la paie |

### 📈 Rapports Financiers
| URL | Nom | Description |
|-----|-----|-------------|
| `/finance/reports/` | `finance:financial_reports` | Rapports financiers |
| `/finance/reports/revenue/` | `finance:revenue_report` | Rapport des revenus |
| `/finance/reports/expenses/` | `finance:expense_report` | Rapport des dépenses |
| `/finance/reports/list/` | `finance:report_list` | Liste des rapports |

---

## 💬 Module Communication (communication/urls.py)

### 📢 Annonces
| URL | Nom | Description |
|-----|-----|-------------|
| `/communication/announcements/` | `communication:announcement_list` | Liste des annonces |
| `/communication/announcements/create/` | `communication:announcement_create` | Créer une annonce |
| `/communication/announcements/<announcement_id>/` | `communication:announcement_detail` | Détails d'une annonce |
| `/communication/announcements/<announcement_id>/mark-read/` | `communication:announcement_mark_read` | Marquer comme lu |

### 📧 Messagerie
| URL | Nom | Description |
|-----|-----|-------------|
| `/communication/messages/` | `communication:message_list` | Liste des messages |
| `/communication/messages/compose/` | `communication:message_compose` | Composer un message |
| `/communication/messages/<message_id>/` | `communication:message_detail` | Détails d'un message |
| `/communication/messages/<message_id>/reply/` | `communication:message_reply` | Répondre au message |

### 👥 Messages de Groupe
| URL | Nom | Description |
|-----|-----|-------------|
| `/communication/group-messages/` | `communication:group_message_list` | Messages de groupe |
| `/communication/group-messages/compose/` | `communication:group_message_compose` | Composer un message de groupe |
| `/communication/group-messages/<message_id>/` | `communication:group_message_detail` | Détails du message de groupe |

### 📁 Ressources
| URL | Nom | Description |
|-----|-----|-------------|
| `/communication/resources/` | `communication:resource_list` | Liste des ressources |
| `/communication/resources/upload/` | `communication:resource_upload` | Uploader une ressource |
| `/communication/resources/<resource_id>/` | `communication:resource_detail` | Détails d'une ressource |
| `/communication/resources/<resource_id>/download/` | `communication:resource_download` | Télécharger une ressource |

### 🔔 Notifications
| URL | Nom | Description |
|-----|-----|-------------|
| `/communication/notifications/` | `communication:notification_list` | Liste des notifications |
| `/communication/notifications/<notification_id>/mark-read/` | `communication:notification_mark_read` | Marquer comme lu |
| `/communication/notifications/mark-all-read/` | `communication:notification_mark_all_read` | Tout marquer comme lu |

### 💬 Forum
| URL | Nom | Description |
|-----|-----|-------------|
| `/communication/forum/` | `communication:forum_index` | Index du forum |
| `/communication/forum/classroom/<classroom_id>/` | `communication:forum_classroom` | Forum d'une classe |
| `/communication/forum/topic/<topic_id>/` | `communication:forum_topic_detail` | Détails d'un sujet |
| `/communication/forum/classroom/<classroom_id>/topic/create/` | `communication:forum_topic_create` | Créer un sujet |
| `/communication/forum/topic/<topic_id>/post/` | `communication:forum_post_create` | Créer un post |

---

## 🚀 API REST (core/api_urls.py)

### 🔗 URLs API
| URL | Nom | Description |
|-----|-----|-------------|
| `/api/v1/` | - | API REST v1 (en développement) |
| `/api/auth/` | - | Authentification API |

### 📝 Notes sur l'API
- L'API REST est actuellement en développement
- Les ViewSets pour les différents modules seront ajoutés progressivement
- L'authentification API utilise Django REST Framework

---

## 🛠️ URLs de Développement

### 🐛 Debug (en mode DEBUG=True)
| URL | Nom | Description |
|-----|-----|-------------|
| `/__debug__/` | - | Django Debug Toolbar |

### 📁 Fichiers Statiques (en mode DEBUG=True)
| URL | Nom | Description |
|-----|-----|-------------|
| `/media/` | - | Fichiers médias uploadés |
| `/static/` | - | Fichiers statiques |

---

## 📊 Résumé par Module

| Module | Nombre d'URLs | Description |
|--------|---------------|-------------|
| **Accounts** | 27 | Gestion des utilisateurs, authentification, dashboards |
| **Academic** | 23 | Gestion académique (classes, notes, présences, documents) |
| **Finance** | 20 | Gestion financière (factures, paiements, bourses, rapports) |
| **Communication** | 17 | Communication (annonces, messages, forum, ressources) |
| **API** | 2 | API REST (en développement) |
| **Core** | 6 | URLs principales et configuration |

**Total : 95 URLs** définies dans l'application eSchool.

---

## 🎯 Conventions de Nommage

### Patterns d'URLs
- **Liste** : `module/items/` → `module:item_list`
- **Création** : `module/items/create/` → `module:item_create`
- **Détails** : `module/items/<id>/` → `module:item_detail`
- **Modification** : `module/items/<id>/edit/` → `module:item_edit`
- **Suppression** : `module/items/<id>/delete/` → `module:item_delete`

### Noms d'Apps
- `accounts` : Gestion des comptes et utilisateurs
- `academic` : Module académique
- `finance` : Module financier
- `communication` : Module de communication

---

*Dernière mise à jour : 15 septembre 2025*