#!/usr/bin/env python3
"""
Script pour créer des données de test pour le module Forum
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from academic.models import ClassRoom, Subject
from communication.models import ForumTopic, ForumPost

User = get_user_model()

# Sujets de discussion variés pour différentes matières
FORUM_TOPICS = {
    'Mathématiques': [
        {
            'title': 'Question sur les équations du second degré',
            'content': 'Bonjour tout le monde ! J\'ai quelques difficultés avec la résolution des équations du second degré. Pourriez-vous m\'expliquer la méthode du discriminant avec un exemple concret ? Par exemple, comment résoudre 2x² - 7x + 3 = 0 ?'
        },
        {
            'title': 'Partage d\'exercices sur les fonctions',
            'content': 'Salut ! J\'ai trouvé quelques exercices intéressants sur les fonctions linéaires et affines. Est-ce que quelqu\'un souhaiterait qu\'on les travaille ensemble ? On pourrait s\'entraider pour les résoudre.'
        },
        {
            'title': 'Révisions pour le contrôle de géométrie',
            'content': 'Le contrôle de géométrie approche et j\'aimerais bien réviser avec vous. Quelqu\'un a-t-il des points particuliers à travailler ? On pourrait faire une session de révision collaborative.'
        }
    ],
    'Français': [
        {
            'title': 'Analyse du poème "Demain dès l\'aube"',
            'content': 'Nous étudions le poème de Victor Hugo "Demain dès l\'aube". J\'ai du mal à comprendre toutes les figures de style utilisées. Pourriez-vous m\'aider à identifier les métaphores et les symbolismes présents dans ce texte ?'
        },
        {
            'title': 'Conseils pour la rédaction',
            'content': 'Bonjour ! J\'ai souvent des difficultés pour structurer mes dissertations. Auriez-vous des conseils pratiques pour bien organiser mes idées et rendre mes textes plus fluides ?'
        },
        {
            'title': 'Discussion sur "Le Petit Prince"',
            'content': 'Que pensez-vous du message principal du livre "Le Petit Prince" de Saint-Exupéry ? J\'aimerais connaître vos interprétations personnelles de cette œuvre.'
        }
    ],
    'Histoire': [
        {
            'title': 'La Révolution française - causes et conséquences',
            'content': 'Nous travaillons sur la Révolution française. Quelqu\'un pourrait-il m\'expliquer clairement les principales causes qui ont mené à cet événement historique majeur ? Et quelles ont été ses conséquences les plus importantes ?'
        },
        {
            'title': 'Ressources documentaires sur la Seconde Guerre mondiale',
            'content': 'J\'ai trouvé des documentaires très intéressants sur la Seconde Guerre mondiale. Est-ce que cela vous intéresse que je partage les liens ? Cela pourrait enrichir nos cours.'
        }
    ],
    'Sciences': [
        {
            'title': 'Expérience de chimie sur les réactions acide-base',
            'content': 'Nous avons fait une expérience sur les réactions acide-base aujourd\'hui. J\'aimerais approfondir le sujet. Quelqu\'un a-t-il des idées d\'expériences simples qu\'on pourrait réaliser chez nous ?'
        },
        {
            'title': 'Questions sur la photosynthèse',
            'content': 'Le processus de photosynthèse me pose quelques questions. Comment exactement la chlorophylle capture-t-elle la lumière ? Et comment l\'énergie lumineuse est-elle transformée en énergie chimique ?'
        }
    ],
    'Anglais': [
        {
            'title': 'Practice with irregular verbs',
            'content': 'Hi everyone! I\'m struggling with irregular verbs. Does anyone have tips to memorize them more easily? What methods work best for you?'
        },
        {
            'title': 'Discussion about our favorite books',
            'content': 'Let\'s share our favorite English books! I just finished reading "To Kill a Mockingbird" and I loved it. What about you? What would you recommend?'
        }
    ]
}

# Réponses types pour les posts
FORUM_REPLIES = [
    "Excellente question ! Voici mon point de vue : ",
    "Je pense pouvoir t'aider avec ça. ",
    "J'ai eu la même difficulté ! Ce qui m'a aidé c'est ",
    "Très intéressant comme sujet ! ",
    "Merci pour cette question, ça me permet de réviser aussi. ",
    "J'ai une autre approche pour résoudre ce problème : ",
    "Super idée ! On pourrait aussi ",
    "Je ne suis pas sûr(e) mais je crois que ",
    "D'accord avec toi ! En plus, ",
    "Petite correction : "
]

FORUM_RESPONSES = [
    "La méthode que tu proposes est effectivement très efficace. J'ajouterais juste que...",
    "Merci pour cette explication claire ! Cela m'aide beaucoup à comprendre.",
    "J'utilise une technique similaire mais avec une petite variante : ",
    "Excellente ressource ! Je vais certainement la consulter.",
    "Très bonne initiative ! Organiser des sessions de révision en groupe est toujours profitable.",
    "Je pense qu'il y a aussi cet aspect à considérer : ",
    "Parfait ! Cela complète bien ce qu'on a vu en cours.",
    "J'ai une question complémentaire sur ce sujet : ",
    "Merci de partager ton expérience, c'est très enrichissant !",
    "Je vais essayer ta méthode et je vous dirai si ça marche pour moi."
]

def create_forum_test_data():
    print("🚀 Création des données de test pour le Forum...")
    
    # Récupérer tous les utilisateurs par rôle
    teachers = User.objects.filter(role='TEACHER')
    students = User.objects.filter(role='STUDENT')
    parents = User.objects.filter(role='PARENT')
    
    print(f"📊 Utilisateurs disponibles : {teachers.count()} enseignants, {students.count()} élèves, {parents.count()} parents")
    
    if not teachers.exists() or not students.exists():
        print("❌ Pas assez d'utilisateurs. Assurez-vous d'avoir des enseignants et des élèves.")
        return
    
    # Récupérer toutes les classes
    classrooms = ClassRoom.objects.all()
    
    if not classrooms.exists():
        print("❌ Aucune classe trouvée. Créez d'abord des classes.")
        return
    
    print(f"🏫 Classes disponibles : {classrooms.count()}")
    
    topics_created = 0
    posts_created = 0
    
    # Créer des sujets pour chaque classe
    for classroom in classrooms:
        # Prendre la première matière assignée à cette classe
        from academic.models import TeacherAssignment
        first_assignment = TeacherAssignment.objects.filter(classroom=classroom).first()
        if first_assignment:
            subject_name = first_assignment.subject.name
        else:
            subject_name = "Général"
        
        # Choisir des sujets appropriés selon la matière
        if subject_name in FORUM_TOPICS:
            topic_templates = FORUM_TOPICS[subject_name]
        else:
            # Sujets génériques si la matière n'est pas dans notre liste
            topic_templates = [
                {
                    'title': f'Question générale sur {subject_name}',
                    'content': f'J\'ai une question concernant le cours de {subject_name}. Quelqu\'un pourrait-il m\'aider ?'
                },
                {
                    'title': f'Partage de ressources - {subject_name}',
                    'content': f'J\'ai trouvé des ressources intéressantes pour le cours de {subject_name}. Qui est intéressé ?'
                }
            ]
        
        # Créer 2-3 sujets par classe
        num_topics = random.randint(2, min(3, len(topic_templates)))
        selected_topics = random.sample(topic_templates, num_topics)
        
        for i, topic_template in enumerate(selected_topics):
            # Choisir l'auteur (principalement élèves, parfois enseignants)
            if random.random() < 0.3:  # 30% de chance que ce soit un enseignant
                # Trouver les enseignants assignés à cette classe
                from academic.models import TeacherAssignment
                teacher_assignments = TeacherAssignment.objects.filter(classroom=classroom)
                if teacher_assignments.exists():
                    # Prendre un enseignant au hasard parmi ceux assignés à cette classe
                    random_assignment = random.choice(teacher_assignments)
                    author = random_assignment.teacher.user
                else:
                    # Si pas d'enseignant assigné, prendre un élève
                    from academic.models import Enrollment
                    enrollments = Enrollment.objects.filter(classroom=classroom)
                    if enrollments.exists():
                        random_enrollment = random.choice(enrollments)
                        author = random_enrollment.student.user
                    else:
                        continue
            else:
                # Prendre un élève inscrit dans cette classe
                from academic.models import Enrollment
                enrollments = Enrollment.objects.filter(classroom=classroom)
                if enrollments.exists():
                    random_enrollment = random.choice(enrollments)
                    author = random_enrollment.student.user
                else:
                    continue
            
            # Créer le sujet
            created_date = timezone.now() - timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            topic = ForumTopic.objects.create(
                title=topic_template['title'],
                content=topic_template['content'],
                author=author,
                classroom=classroom,
                created_at=created_date,
                updated_at=created_date,
                is_pinned=(i == 0 and random.random() < 0.3),  # Premier sujet parfois épinglé
                views_count=random.randint(5, 50)
            )
            
            topics_created += 1
            print(f"  ✅ Sujet créé : '{topic.title}' dans {classroom.name}")
            
            # Créer des réponses pour ce sujet
            num_posts = random.randint(2, 8)
            
            for post_num in range(num_posts):
                # Choisir l'auteur de la réponse
                from academic.models import TeacherAssignment, Enrollment
                
                possible_authors = []
                
                # Ajouter les élèves inscrits dans cette classe
                enrollments = Enrollment.objects.filter(classroom=classroom)
                for enrollment in enrollments:
                    possible_authors.append(enrollment.student.user)
                
                # Ajouter les enseignants assignés à cette classe
                teacher_assignments = TeacherAssignment.objects.filter(classroom=classroom)
                for assignment in teacher_assignments:
                    possible_authors.append(assignment.teacher.user)
                
                # Ajouter parfois des parents si l'auteur original est un élève
                if author.role == 'STUDENT' and random.random() < 0.2:
                    # Trouver les parents des élèves de cette classe
                    for enrollment in enrollments:
                        # Récupérer l'objet Student à partir de l'enrollment
                        student = enrollment.student
                        # Trouver les parents de cet élève
                        student_parents = student.parents.all()
                        for parent in student_parents:
                            possible_authors.append(parent.user)
                
                if not possible_authors:
                    continue
                
                post_author = random.choice(possible_authors)
                
                # Éviter que l'auteur original réponde immédiatement
                if post_num == 0 and post_author == author and len(possible_authors) > 1:
                    other_authors = [a for a in possible_authors if a != author]
                    post_author = random.choice(other_authors)
                
                # Générer le contenu de la réponse
                reply_start = random.choice(FORUM_REPLIES)
                reply_content = random.choice(FORUM_RESPONSES)
                
                post_content = reply_start + reply_content
                
                # Ajouter du contexte selon le rôle
                if post_author.role == 'TEACHER':
                    post_content += f" En tant qu'enseignant, je peux ajouter que cette approche est effectivement recommandée dans le programme officiel."
                elif post_author.role == 'PARENT':
                    post_content += f" En tant que parent, je trouve que ces échanges sont très enrichissants pour nos enfants."
                
                # Date de création (après le sujet)
                post_date = created_date + timedelta(
                    days=random.randint(0, 5),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                # Éviter les dates futures
                if post_date > timezone.now():
                    post_date = timezone.now() - timedelta(minutes=random.randint(1, 60))
                
                ForumPost.objects.create(
                    content=post_content,
                    author=post_author,
                    topic=topic,
                    created_at=post_date
                )
                
                posts_created += 1
            
            # Mettre à jour la date de dernière activité du sujet
            last_post = topic.forum_posts.order_by('-created_at').first()
            if last_post:
                topic.updated_at = last_post.created_at
                topic.save()
    
    print(f"\n🎉 Données de test créées avec succès !")
    print(f"📝 {topics_created} sujets créés")
    print(f"💬 {posts_created} réponses créées")
    print(f"🏫 Répartition sur {classrooms.count()} classes")
    
    # Statistiques par classe
    print(f"\n📊 Répartition par classe :")
    for classroom in classrooms:
        topic_count = ForumTopic.objects.filter(classroom=classroom).count()
        post_count = ForumPost.objects.filter(topic__classroom=classroom).count()
        
        # Récupérer le nom de la matière
        from academic.models import TeacherAssignment
        first_assignment = TeacherAssignment.objects.filter(classroom=classroom).first()
        subject_name = first_assignment.subject.name if first_assignment else "Général"
        
        print(f"  {classroom.name} ({subject_name}) : {topic_count} sujets, {post_count} réponses")

if __name__ == "__main__":
    create_forum_test_data()
