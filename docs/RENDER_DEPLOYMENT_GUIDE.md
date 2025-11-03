# Guide de Déploiement sur Render.com

Ce guide explique comment déployer votre application Django eSchool sur Render.com.

## 📋 Prérequis

- Un compte GitHub avec le dépôt eschool
- Un compte Render.com (gratuit pour commencer)
- Node.js et npm installés localement (déjà fait ✅)

## 🔧 Fichiers de Configuration Créés

Les fichiers suivants ont été créés pour le déploiement :

1. **`requirements.txt`** - Liste des dépendances Python
2. **`build.sh`** - Script de build automatique pour Render
3. **`core/settings.py`** - Mis à jour avec support pour DATABASE_URL et RENDER_EXTERNAL_HOSTNAME

## 📝 Étapes de Déploiement

### 1️⃣ Pousser les Changements vers GitHub

Les fichiers de déploiement sont prêts. Commitez et poussez-les :

```bash
git add requirements.txt build.sh core/settings.py
git commit -m "Add Render deployment configuration"
git push origin master
```

### 2️⃣ Créer un Nouveau Web Service sur Render

1. Connectez-vous à [Render.com](https://render.com/)
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre dépôt GitHub `jeshurun01/eschool`
4. Donnez un nom à votre service : `eschool` ou `eschool-app`

### 3️⃣ Configurer le Web Service

Dans la page de configuration, utilisez ces paramètres :

**Build & Deploy:**
- **Environment:** `Python 3`
- **Region:** Choisissez la région la plus proche (ex: Frankfurt pour l'Europe)
- **Branch:** `master`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn core.wsgi:application`

**Instance Type:**
- Pour commencer : **Free** (0$/mois, avec limitations)
- Pour production : **Starter** (7$/mois) ou **Standard** (25$/mois)

### 4️⃣ Ajouter une Base de Données PostgreSQL

1. Dans le dashboard Render, cliquez sur **"New +"** → **"PostgreSQL"**
2. Donnez un nom : `eschool-db`
3. Choisissez le même datacenter que votre web service
4. Sélectionnez le plan **Free** pour commencer
5. Cliquez sur **"Create Database"**

**⏳ Attendez** que la base soit créée (~2 minutes)

### 5️⃣ Configurer les Variables d'Environnement

Dans votre Web Service, allez dans **"Environment"** et ajoutez ces variables :

#### Variables Obligatoires :

```env
# Django Core
SECRET_KEY=<générez-une-clé-secrète-forte>
DEBUG=False

# Database (copier depuis votre PostgreSQL Render)
DATABASE_URL=<URL-de-votre-base-PostgreSQL-Render>

# Hostname Render
RENDER_EXTERNAL_HOSTNAME=<votre-app>.onrender.com

# Python
PYTHON_VERSION=3.12.9
```

#### Variables Optionnelles :

```env
# Langues et Timezone
LANGUAGE_CODE=fr
TIME_ZONE=Africa/Lubumbashi

# Email (si vous configurez l'envoi d'emails)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=noreply@eschool.cd

# Site
SITE_NAME=eSchool
SITE_URL=https://<votre-app>.onrender.com
```

#### 🔐 Générer une SECRET_KEY

Vous pouvez générer une clé secrète sécurisée avec :

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 📋 Obtenir DATABASE_URL

1. Allez dans votre base de données PostgreSQL sur Render
2. Copiez l'**"Internal Database URL"** (commence par `postgresql://`)
3. Collez-la dans la variable `DATABASE_URL`

### 6️⃣ Déployer l'Application

1. Cliquez sur **"Create Web Service"**
2. Render va automatiquement :
   - Cloner votre dépôt
   - Installer les dépendances Python (`requirements.txt`)
   - Installer Node.js et construire Tailwind CSS
   - Collecter les fichiers statiques
   - Exécuter les migrations
   - Démarrer Gunicorn

**⏳ Le premier déploiement peut prendre 5-10 minutes**

### 7️⃣ Créer un Super Utilisateur

Une fois déployé, vous devez créer un compte admin :

1. Dans votre Web Service Render, allez dans l'onglet **"Shell"**
2. Exécutez :

```bash
python manage.py createsuperuser
```

3. Entrez email et mot de passe pour le compte admin

**Alternative :** Exécuter votre script de population

```bash
python scripts/reset_and_populate.py
```

⚠️ **Attention :** Cela va supprimer toutes les données existantes !

### 8️⃣ Vérifier le Déploiement

Visitez votre application : `https://<votre-app>.onrender.com`

**Pages à tester :**
- Page d'accueil : `/`
- Admin Django : `/admin/`
- Login : `/accounts/login/`
- Dashboard : `/accounts/`

## 🎨 Gestion des Fichiers Statiques

WhiteNoise est configuré pour servir automatiquement les fichiers statiques (CSS, JS, images) en production.

Les fichiers sont collectés pendant le build avec :
```bash
python manage.py collectstatic --no-input
```

## 🔄 Déploiements Futurs

Render redéploie automatiquement à chaque `git push` sur la branche `master`.

**Déploiement manuel :**
1. Allez dans votre Web Service
2. Cliquez sur **"Manual Deploy"** → **"Deploy latest commit"**

## 📊 Monitoring et Logs

**Voir les logs en temps réel :**
1. Dans votre Web Service, onglet **"Logs"**
2. Les logs Python et Gunicorn s'affichent ici

**Métriques :**
- L'onglet **"Metrics"** montre CPU, mémoire, requêtes HTTP

## 🛠️ Dépannage

### Build Échoue

**Erreur : `npm: command not found`**
- Render devrait installer Node.js automatiquement
- Vérifiez que `package.json` est bien dans le repo

**Erreur : `Module not found`**
- Vérifiez que toutes les dépendances sont dans `requirements.txt`
- Essayez un déploiement manuel

### Application Ne Démarre Pas

**Erreur 500 Internal Server Error**
- Vérifiez les logs dans l'onglet **"Logs"**
- Assurez-vous que `DEBUG=False` en production
- Vérifiez que `RENDER_EXTERNAL_HOSTNAME` est correct

**Database connection errors**
- Vérifiez que `DATABASE_URL` est correctement configurée
- Assurez-vous que la base PostgreSQL est dans le même datacenter

### Fichiers Statiques Ne Chargent Pas

- Vérifiez que `build.sh` a bien exécuté `collectstatic`
- Vérifiez les logs du build
- WhiteNoise devrait servir automatiquement les fichiers

## 💾 Sauvegardes de Base de Données

**Faire une sauvegarde :**
1. Dans votre PostgreSQL Render, allez à **"Backups"**
2. Les plans payants ont des sauvegardes automatiques
3. Plan gratuit : pas de sauvegardes automatiques

**Exporter manuellement :**
```bash
# Depuis le Shell Render
python manage.py dumpdata > backup.json
```

## 🔒 Sécurité en Production

✅ **Déjà configuré :**
- `DEBUG=False` en production
- `SECRET_KEY` depuis variable d'environnement
- WhiteNoise pour servir les fichiers statiques
- HTTPS automatique avec Render
- Sécurité Django (HSTS, XSS protection) activée si `DEBUG=False`

**⚠️ À faire :**
- Utilisez des mots de passe forts pour les comptes admin
- Changez `SECRET_KEY` si elle a été exposée
- Configurez les CORS selon vos besoins
- Activez Redis pour le cache en production (optionnel)

## 📈 Mise à l'Échelle

**Plans Render :**
- **Free** : 512 MB RAM, se met en veille après 15 min d'inactivité
- **Starter** : 512 MB RAM, toujours actif, 7$/mois
- **Standard** : 2 GB RAM, 25$/mois
- **Pro** : 4 GB RAM, mise à l'échelle automatique, 85$/mois

**Quand passer au plan payant :**
- Plus de 100 utilisateurs actifs
- Besoin de disponibilité 24/7
- Temps de réponse < 1 seconde requis

## 🌍 Domaine Personnalisé

Pour utiliser votre propre domaine (`www.eschool.cd`) :

1. Dans votre Web Service, onglet **"Settings"**
2. Section **"Custom Domain"**
3. Ajoutez votre domaine
4. Configurez les DNS selon les instructions Render
5. Render génère automatiquement un certificat SSL

## 📞 Support

- Documentation Render : https://render.com/docs
- Support Render : support@render.com
- Issues GitHub : https://github.com/jeshurun01/eschool/issues

## ✅ Checklist de Déploiement

- [ ] Code poussé sur GitHub
- [ ] Web Service créé sur Render
- [ ] Base PostgreSQL créée et connectée
- [ ] Variables d'environnement configurées
- [ ] Build réussi (vérifier les logs)
- [ ] Migrations exécutées
- [ ] Super utilisateur créé
- [ ] Page d'accueil accessible
- [ ] Admin Django accessible
- [ ] Login fonctionne
- [ ] Fichiers statiques chargent correctement
- [ ] Tests basiques réussis

---

**🎉 Félicitations !** Votre application Django est maintenant déployée sur Render !

Pour toute question ou problème, consultez les logs et la documentation Render.
