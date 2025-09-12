#!/usr/bin/env python
"""
Script pour créer des données de test pour le module de communication
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from communication.models import Announcement, AnnouncementRead, Message, Notification
from accounts.models import User


def create_test_announcements():
    """Créer des annonces de test"""
    print("=== Création des annonces de test ===")
    
    # Récupérer des utilisateurs
    admin_users = User.objects.filter(role='ADMIN')
    teacher_users = User.objects.filter(role='TEACHER')
    
    if not admin_users.exists():
        print("❌ Aucun utilisateur admin trouvé")
        return
    
    admin = admin_users.first()
    teacher = teacher_users.first() if teacher_users.exists() else admin
    
    # Supprimer les anciennes annonces de test
    Announcement.objects.all().delete()
    
    announcements_data = [
        {
            'title': 'Réunion de rentrée 2025',
            'content': '''Chers parents et élèves,
            
Nous avons le plaisir de vous inviter à la réunion de rentrée qui se déroulera le mercredi 10 septembre 2025 à 18h30 dans la salle polyvalente.

Programme de la soirée :
- 18h30 : Accueil et présentation de l'équipe pédagogique
- 19h00 : Présentation du projet éducatif 2025-2026
- 19h30 : Questions/réponses
- 20h00 : Pot de l'amitié

Votre présence est vivement souhaitée.

Cordialement,
L'équipe de direction''',
            'type': 'EVENT',
            'audience': 'ALL',
            'priority': 2,
            'is_pinned': True,
            'author': admin
        },
        {
            'title': 'Nouvelle procédure de cantine',
            'content': '''À partir du lundi 15 septembre 2025, une nouvelle procédure de réservation des repas sera mise en place.

Principales nouveautés :
- Réservation obligatoire via l'application mobile ou le site web
- Possibilité d'annuler jusqu'à 9h le matin même
- Menu végétarien disponible tous les jours
- Nouveau système de paiement par carte

Pour plus d'informations, consultez le guide complet sur notre site web ou contactez le service de restauration.''',
            'type': 'ADMINISTRATIVE',
            'audience': 'PARENTS',
            'priority': 1,
            'is_pinned': False,
            'author': admin
        },
        {
            'title': 'Formation pédagogique obligatoire',
            'content': '''Chers collègues enseignants,

Une formation pédagogique obligatoire sur les nouvelles technologies éducatives aura lieu :

📅 Date : Mercredi 12 septembre 2025
🕐 Heure : 14h00 - 17h00
📍 Lieu : Salle informatique

Thèmes abordés :
- Utilisation des tableaux interactifs
- Plateformes d'apprentissage en ligne
- Outils d'évaluation numériques

Merci de confirmer votre présence avant le 8 septembre.''',
            'type': 'ACADEMIC',
            'audience': 'TEACHERS',
            'priority': 2,
            'is_pinned': False,
            'author': teacher
        },
        {
            'title': 'Nouveau règlement intérieur',
            'content': '''Le nouveau règlement intérieur de l'établissement entre en vigueur dès maintenant.

Principales modifications :
- Horaires d'ouverture étendus (7h30 - 18h30)
- Nouvelle politique sur l'utilisation des téléphones portables
- Procédures d'absences modifiées
- Règles de vie scolaire actualisées

Le document complet est disponible sur l'espace numérique de travail. Tous les élèves et parents sont invités à en prendre connaissance.''',
            'type': 'ADMINISTRATIVE',
            'audience': 'ALL',
            'priority': 1,
            'is_pinned': True,
            'author': admin
        },
        {
            'title': 'Concours de mathématiques 2025',
            'content': '''🏆 Grand concours de mathématiques ouvert à tous les élèves !

Dates importantes :
- Inscriptions : jusqu'au 20 septembre
- Épreuve écrite : 5 octobre 2025
- Résultats : 15 octobre 2025

Catégories :
- 6ème - 5ème
- 4ème - 3ème  
- Lycée

Prix à gagner : calculatrices scientifiques, livres, bons d'achat...

Inscription auprès de votre professeur de mathématiques.''',
            'type': 'EVENT',
            'audience': 'STUDENTS',
            'priority': 1,
            'is_pinned': False,
            'author': teacher
        },
        {
            'title': 'Maintenance informatique programmée',
            'content': '''⚠️ MAINTENANCE PROGRAMMÉE

Une maintenance des serveurs informatiques aura lieu ce week-end :

📅 Samedi 7 septembre - 22h00 à Dimanche 8 septembre - 6h00

Services indisponibles :
- Espace numérique de travail
- Messagerie électronique
- Plateforme de cours en ligne

Les services seront rétablis dès la fin de la maintenance.

Nous nous excusons pour la gêne occasionnée.''',
            'type': 'URGENT',
            'audience': 'ALL',
            'priority': 3,
            'is_pinned': True,
            'author': admin
        }
    ]
    
    created_announcements = []
    for data in announcements_data:
        announcement = Announcement.objects.create(
            title=data['title'],
            content=data['content'],
            type=data['type'],
            audience=data['audience'],
            priority=data['priority'],
            is_pinned=data['is_pinned'],
            author=data['author'],
            is_published=True,
            publish_date=timezone.now() - timedelta(days=random.randint(0, 5))
        )
        created_announcements.append(announcement)
        print(f"✅ Annonce créée : {announcement.title}")
    
    # Marquer quelques annonces comme lues pour certains utilisateurs
    users = User.objects.all()[:10]
    for user in users:
        # Marquer aléatoirement 60% des annonces comme lues
        for announcement in created_announcements:
            if random.random() < 0.6:
                AnnouncementRead.objects.get_or_create(
                    announcement=announcement,
                    user=user
                )
    
    print(f"✅ {len(created_announcements)} annonces créées avec succès")
    return created_announcements


def create_test_messages():
    """Créer des messages de test"""
    print("\n=== Création des messages de test ===")
    
    # Récupérer des utilisateurs de différents rôles
    students = list(User.objects.filter(role='STUDENT')[:5])
    teachers = list(User.objects.filter(role='TEACHER')[:3])
    parents = list(User.objects.filter(role='PARENT')[:3])
    admins = list(User.objects.filter(role='ADMIN')[:2])
    
    all_users = students + teachers + parents + admins
    
    if len(all_users) < 2:
        print("❌ Pas assez d'utilisateurs pour créer des messages")
        return
    
    # Supprimer les anciens messages de test
    Message.objects.all().delete()
    
    messages_data = [
        {
            'subject': 'Question sur les devoirs de mathématiques',
            'content': '''Bonjour,

J'ai une question concernant l'exercice 12 page 45 du manuel de mathématiques. Pourriez-vous m'expliquer la méthode pour résoudre ce type d'équation ?

Merci d'avance pour votre aide.

Cordialement''',
            'sender_role': 'STUDENT',
            'recipient_role': 'TEACHER'
        },
        {
            'subject': 'Absence de mon enfant',
            'content': '''Madame, Monsieur,

Je vous informe que mon enfant sera absent demain matin en raison d'un rendez-vous médical.

Il sera présent en cours à partir de 14h.

Merci de votre compréhension.

Cordialement''',
            'sender_role': 'PARENT',
            'recipient_role': 'TEACHER'
        },
        {
            'subject': 'Réunion équipe pédagogique',
            'content': '''Chers collègues,

Je vous propose d'organiser une réunion de l'équipe pédagogique la semaine prochaine pour faire le point sur le premier trimestre.

Pouvez-vous me dire vos disponibilités pour mercredi ou jeudi après 16h ?

Merci''',
            'sender_role': 'TEACHER',
            'recipient_role': 'TEACHER'
        },
        {
            'subject': 'Demande de rendez-vous',
            'content': '''Bonjour,

Je souhaiterais prendre rendez-vous avec vous pour discuter des résultats de mon enfant et voir comment l'aider à progresser.

Seriez-vous disponible cette semaine ou la semaine prochaine ?

Merci et bonne journée''',
            'sender_role': 'PARENT',
            'recipient_role': 'TEACHER'
        },
        {
            'subject': 'Information importante',
            'content': '''Bonjour,

Suite à notre conversation de ce matin, voici les informations complémentaires que vous m'aviez demandées concernant le projet de classe.

N'hésitez pas si vous avez d'autres questions.

Cordialement''',
            'sender_role': 'TEACHER',
            'recipient_role': 'ADMIN'
        }
    ]
    
    created_messages = []
    
    for i, data in enumerate(messages_data):
        # Sélectionner sender et recipient selon les rôles
        senders = [u for u in all_users if getattr(u, 'role', None) == data['sender_role']]
        recipients = [u for u in all_users if getattr(u, 'role', None) == data['recipient_role']]
        
        if senders and recipients:
            sender = random.choice(senders)
            recipient = random.choice([r for r in recipients if r != sender])
            
            message = Message.objects.create(
                sender=sender,
                recipient=recipient,
                subject=data['subject'],
                content=data['content'],
                sent_date=timezone.now() - timedelta(days=random.randint(0, 7)),
                is_read=random.choice([True, False])
            )
            created_messages.append(message)
            print(f"✅ Message créé : {message.subject}")
    
    # Créer quelques réponses
    for message in created_messages[:3]:
        if random.random() < 0.5:  # 50% de chance d'avoir une réponse
            reply = Message.objects.create(
                sender=message.recipient,
                recipient=message.sender,
                subject=f"Re: {message.subject}",
                content=f"Merci pour votre message. Je reviens vers vous rapidement.\n\nCordialement",
                sent_date=message.sent_date + timedelta(hours=random.randint(1, 24)),
                is_read=random.choice([True, False]),
                parent_message=message
            )
            print(f"✅ Réponse créée pour : {message.subject}")
    
    print(f"✅ {len(created_messages)} messages créés avec succès")
    return created_messages


def create_test_notifications():
    """Créer des notifications de test"""
    print("\n=== Création des notifications de test ===")
    
    users = User.objects.all()[:10]
    
    if not users:
        print("❌ Aucun utilisateur trouvé")
        return
    
    # Supprimer les anciennes notifications
    Notification.objects.all().delete()
    
    notifications_data = [
        {
            'title': 'Nouveau message reçu',
            'message': 'Vous avez reçu un nouveau message de votre professeur.',
            'type': 'MESSAGE',
            'link_url': '/communication/messages/'
        },
        {
            'title': 'Nouvelle annonce publiée',
            'message': 'Une nouvelle annonce importante a été publiée.',
            'type': 'ANNOUNCEMENT',
            'link_url': '/communication/announcements/'
        },
        {
            'title': 'Note ajoutée',
            'message': 'Une nouvelle note a été ajoutée à votre bulletin.',
            'type': 'ACADEMIC',
            'link_url': '/academic/grades/'
        },
        {
            'title': 'Paiement en attente',
            'message': 'Un paiement de frais de scolarité est en attente.',
            'type': 'FINANCE',
            'link_url': '/finance/payments/'
        },
        {
            'title': 'Mise à jour système',
            'message': 'Le système a été mis à jour avec de nouvelles fonctionnalités.',
            'type': 'SYSTEM',
            'link_url': ''
        }
    ]
    
    created_notifications = []
    
    for user in users:
        # Créer 2-4 notifications par utilisateur
        user_notifications = random.sample(notifications_data, random.randint(2, 4))
        
        for data in user_notifications:
            notification = Notification.objects.create(
                user=user,
                title=data['title'],
                message=data['message'],
                type=data['type'],
                link_url=data['link_url'] or '',
                created_at=timezone.now() - timedelta(days=random.randint(0, 10)),
                is_read=random.choice([True, False])
            )
            created_notifications.append(notification)
    
    print(f"✅ {len(created_notifications)} notifications créées avec succès")
    return created_notifications


def main():
    """Fonction principale"""
    print("🚀 Création des données de test pour le module de communication")
    print("=" * 60)
    
    try:
        # Créer les annonces
        announcements = create_test_announcements()
        
        # Créer les messages
        messages = create_test_messages()
        
        # Créer les notifications
        notifications = create_test_notifications()
        
        print("\n" + "=" * 60)
        print("🎉 RÉSUMÉ DE LA CRÉATION")
        print(f"📢 Annonces créées : {len(announcements) if announcements else 0}")
        print(f"💬 Messages créés : {len(messages) if messages else 0}")
        print(f"🔔 Notifications créées : {len(notifications) if notifications else 0}")
        print("\n✅ Toutes les données de test ont été créées avec succès !")
        print("\nVous pouvez maintenant tester le module de communication :")
        print("- http://127.0.0.1:8000/communication/announcements/")
        print("- http://127.0.0.1:8000/communication/messages/")
        print("- http://127.0.0.1:8000/communication/notifications/")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
