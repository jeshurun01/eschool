# Fichier temporaire pour documenter les fonctions à refactorer

## Fonctions dans accounts/views.py à adapter :
- dashboard_view (lignes 161-163) : Remplacer Attendance par DailyAttendanceSummary
- student_dashboard (ligne 314) : Utiliser DailyAttendanceSummary pour les présences mensuelles
- teacher_dashboard (lignes 500, 568) : Adapter les statistiques de présence
- parent_dashboard (lignes 602, 698, 716) : Utiliser SessionAttendance/DailyAttendanceSummary
- parent_detail_view (lignes 1314, 1390) : Adapter les vues parents

## Fonctions dans academic/views.py à adapter :
- attendance_list (ligne 729) : Remplacer par SessionAttendance
- take_attendance (lignes 844, 907) : Adapter pour les sessions
- attendance_create (ligne 964) : Refactorer pour SessionAttendance
- student_attendance_report (ligne 1038) : Utiliser DailyAttendanceSummary

## Plan de refactoring :
1. Créer les migrations pour les nouveaux modèles
2. Créer des utilitaires de migration des données 
3. Refactorer progressivement chaque vue
4. Mettre à jour les templates
5. Supprimer l'ancien code