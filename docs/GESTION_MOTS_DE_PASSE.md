# Système de Gestion des Mots de Passe

## Vue d'ensemble

Le système eSchool utilise un processus de génération automatique de mots de passe pour améliorer la sécurité et simplifier la création de comptes utilisateurs.

## Fonctionnement

### 1. Création d'un nouvel utilisateur

Lorsqu'un administrateur crée un nouveau compte utilisateur :

1. **Formulaire simplifié** : L'administrateur remplit uniquement les informations personnelles (nom, prénom, email, rôle, etc.) sans avoir à définir de mot de passe.

2. **Génération automatique** : Le système génère automatiquement un mot de passe sécurisé de 12 caractères contenant :
   - Au moins une lettre minuscule
   - Au moins une lettre majuscule
   - Au moins un chiffre
   - Au moins un caractère spécial (@#$%&*!)

3. **Envoi par email** : Le mot de passe généré est envoyé automatiquement à l'adresse email de l'utilisateur avec :
   - Ses identifiants de connexion
   - Le mot de passe temporaire
   - Instructions pour le changer à la première connexion
   - Lien vers le portail

4. **Notification à l'admin** : L'administrateur reçoit une confirmation :
   - Si l'email est envoyé avec succès : message de confirmation
   - Si l'email échoue : affichage du mot de passe temporaire à communiquer manuellement

### 2. Première connexion de l'utilisateur

Lors de la première connexion, l'utilisateur :

1. Se connecte avec les identifiants reçus par email
2. Est invité à changer son mot de passe temporaire
3. Définit un nouveau mot de passe personnel et sécurisé

## Sécurité

### Génération de mot de passe

- **Algorithme** : Utilisation du module `secrets` de Python (cryptographiquement sûr)
- **Complexité** : 12 caractères minimum avec diversité de caractères
- **Aléatoire** : Génération vraiment aléatoire, pas pseudo-aléatoire

### Stockage

- Les mots de passe sont **hashés** avec l'algorithme PBKDF2 par défaut de Django
- Aucun mot de passe n'est stocké en clair dans la base de données
- Les mots de passe ne sont jamais loggés

### Transmission

- Email envoyé de manière sécurisée via le serveur SMTP configuré
- En cas d'échec d'envoi, le mot de passe est affiché une seule fois à l'admin
- L'utilisateur doit changer le mot de passe à la première connexion

## Configuration

### Variables d'environnement

Ajoutez dans votre fichier `.env` :

```env
# Nom du site (utilisé dans les emails)
SITE_NAME=eSchool

# URL du site (lien dans les emails)
SITE_URL=https://votre-ecole.com

# Configuration email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=noreply@votre-ecole.com
```

### Configuration SMTP

#### Gmail

1. Activer l'authentification à deux facteurs
2. Générer un mot de passe d'application
3. Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

#### SendGrid, Mailgun, etc.

Consultez la documentation de votre fournisseur pour obtenir les paramètres SMTP.

#### Mode développement

En développement, utilisez le backend console :

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Les emails seront affichés dans la console au lieu d'être envoyés.

## Utilisation

### Pour les administrateurs

#### Créer un utilisateur

1. Accédez à **Gestion > Utilisateurs > Créer un utilisateur**
2. Remplissez le formulaire :
   - Informations personnelles (nom, prénom, email)
   - Téléphone (optionnel)
   - Rôle (STUDENT, TEACHER, PARENT, ADMIN, etc.)
   - Statut du compte (actif/inactif)
3. Cliquez sur **Créer**
4. Le système :
   - Génère un mot de passe
   - Crée le compte
   - Envoie l'email
   - Affiche une confirmation

#### Si l'email échoue

Si l'envoi de l'email échoue, le système affichera :

```
⚠️ Utilisateur Jean Dupont créé avec succès.
IMPORTANT : Mot de passe temporaire : Abc123@xyz
(L'email n'a pas pu être envoyé. Veuillez noter ce mot de passe 
et le communiquer à l'utilisateur.)
```

**Action requise** : Communiquez manuellement le mot de passe à l'utilisateur de manière sécurisée.

### Pour les utilisateurs

#### Première connexion

1. Ouvrez l'email de bienvenue
2. Notez vos identifiants :
   - Email : votre-email@example.com
   - Mot de passe temporaire : (affiché dans l'email)
3. Cliquez sur le lien du portail
4. Connectez-vous avec ces identifiants
5. **Changez immédiatement votre mot de passe**

#### Changer le mot de passe

1. Connectez-vous au portail
2. Accédez à **Mon Profil > Changer le mot de passe**
3. Entrez :
   - Mot de passe actuel
   - Nouveau mot de passe
   - Confirmation du nouveau mot de passe
4. Cliquez sur **Enregistrer**

## Template d'email

Le système envoie un email au format suivant :

```
Objet : Bienvenue sur eSchool - Vos identifiants de connexion

Bonjour Jean Dupont,

Votre compte a été créé avec succès sur eSchool.

Voici vos identifiants de connexion :
- Email : jean.dupont@example.com
- Mot de passe temporaire : Abc123@xyz

⚠️ IMPORTANT : Pour des raisons de sécurité, veuillez changer ce mot 
de passe lors de votre première connexion.

Pour vous connecter, rendez-vous sur : https://votre-ecole.com

Cordialement,
L'équipe eSchool
```

## Bonnes pratiques

### Pour les administrateurs

1. **Vérifiez l'email** : Assurez-vous que l'adresse email est correcte avant de créer le compte
2. **Communiquez** : Prévenez l'utilisateur qu'il va recevoir un email
3. **Vérifiez les spams** : Demandez à l'utilisateur de vérifier ses spams
4. **Conservez** : Si l'email échoue, notez le mot de passe temporaire de manière sécurisée
5. **Suivez** : Vérifiez que l'utilisateur change bien son mot de passe

### Pour les utilisateurs

1. **Changez rapidement** : Changez votre mot de passe dès la première connexion
2. **Mot de passe fort** : Utilisez un mot de passe complexe et unique
3. **Ne partagez pas** : Ne partagez jamais votre mot de passe
4. **Sécurisez** : Ne notez pas votre mot de passe en clair
5. **Méfiez-vous** : L'administration ne vous demandera jamais votre mot de passe

## Dépannage

### L'email n'est pas reçu

1. **Vérifier les spams** : L'email peut être dans les spams
2. **Vérifier l'adresse** : L'adresse email est-elle correcte ?
3. **Vérifier les logs** : Consultez les logs Django pour voir les erreurs
4. **Tester la config SMTP** : Utilisez le shell Django pour tester :

```python
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test',
    'Message de test',
    'noreply@eschool.com',
    ['destinataire@example.com'],
    fail_silently=False,
)
```

### L'utilisateur ne peut pas se connecter

1. **Vérifier le statut** : Le compte est-il actif ?
2. **Vérifier l'email** : L'adresse est-elle correcte ?
3. **Réinitialiser** : Utilisez la fonction "Mot de passe oublié"
4. **Vérifier les rôles** : L'utilisateur a-t-il les permissions nécessaires ?

### Erreur lors de la création

1. **Email dupliqué** : Un compte avec cet email existe déjà
2. **Champs requis** : Tous les champs obligatoires sont remplis ?
3. **Permissions** : Vous avez les droits d'administration ?

## Code source

### Fonction de génération

```python
# accounts/views.py

def generate_secure_password(length=12):
    """Génère un mot de passe sécurisé aléatoire"""
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = '@#$%&*!'
    
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    
    all_chars = lowercase + uppercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)
```

### Fonction d'envoi d'email

```python
# accounts/views.py

def send_password_email(user, password):
    """Envoie le mot de passe initial à l'utilisateur par email"""
    subject = f'Bienvenue sur {settings.SITE_NAME} - Vos identifiants'
    message = f"""
Bonjour {user.get_full_name()},

Votre compte a été créé avec succès sur {settings.SITE_NAME}.

Voici vos identifiants de connexion :
- Email : {user.email}
- Mot de passe temporaire : {password}

⚠️ IMPORTANT : Veuillez changer ce mot de passe lors de votre première connexion.

Pour vous connecter, rendez-vous sur : {settings.SITE_URL}

Cordialement,
L'équipe {settings.SITE_NAME}
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        return False
```

## Support

Pour toute question ou problème :

1. Consultez cette documentation
2. Vérifiez les logs système
3. Contactez l'administrateur système
4. Créez un ticket de support

---

**Version** : 1.0  
**Dernière mise à jour** : Octobre 2025  
**Auteur** : Équipe eSchool
