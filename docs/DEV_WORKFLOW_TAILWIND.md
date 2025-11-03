# Guide de développement - Tailwind CSS

## 🚀 Démarrage rapide

### Installation initiale (après clone)
```bash
# 1. Installer les dépendances Python
uv sync

# 2. Installer les dépendances Node.js
npm install

# 3. Compiler Tailwind CSS
npm run build
```

## 💻 Workflow de développement

### Mode développement avec watch
Le mode watch recompile automatiquement le CSS à chaque modification :

```bash
npm run dev
```

Laissez cette commande tourner dans un terminal pendant que vous développez. Elle détecte automatiquement :
- Modifications des templates (`.html`)
- Modifications des fichiers Python (`.py`)
- Modifications des fichiers JavaScript (`.js`)

### Lancer le serveur Django
Dans un autre terminal :

```bash
python manage.py runserver
```

### Workflow recommandé
1. **Terminal 1** : `npm run dev` (watch Tailwind)
2. **Terminal 2** : `python manage.py runserver` (serveur Django)
3. **Navigateur** : `http://localhost:8000`

## 📝 Ajouter des classes Tailwind

### Dans un template
```html
<div class="bg-blue-600 text-white p-4 rounded-lg">
  Hello eSchool!
</div>
```

### Classes custom disponibles
Utilisez les composants définis dans `static/src/input.css` :

```html
<!-- Boutons -->
<button class="btn-primary">Enregistrer</button>
<button class="btn-secondary">Annuler</button>

<!-- Cartes -->
<div class="card">
  <h2>Titre</h2>
  <p>Contenu</p>
</div>

<!-- Badges -->
<span class="badge badge-student">Élève</span>
<span class="badge badge-parent">Parent</span>
<span class="badge badge-teacher">Enseignant</span>
<span class="badge badge-finance">Finance</span>
<span class="badge badge-admin">Admin</span>
```

## 🎨 Couleurs des rôles

Couleurs définies dans `tailwind.config.js` :

```javascript
student: { 600: '#2563eb', 700: '#1d4ed8' }  // Bleu
parent: { 600: '#16a34a', 700: '#15803d' }   // Vert
teacher: { 600: '#9333ea', 700: '#7e22ce' }  // Violet
finance: { 600: '#0d9488', 700: '#0f766e' }  // Teal
```

Usage dans les templates :
```html
<div class="bg-student-600 text-white">...</div>
<div class="bg-parent-600 text-white">...</div>
<div class="bg-teacher-600 text-white">...</div>
<div class="bg-finance-600 text-white">...</div>
```

## 🔧 Commandes npm

| Commande | Description |
|----------|-------------|
| `npm run dev` | Mode développement avec watch |
| `npm run build` | Build production (minifié) |
| `npm install` | Installer/réinstaller les dépendances |

## 📦 Build pour production

Avant de déployer :

```bash
# 1. Build CSS minifié
npm run build

# 2. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 3. Vérifier que le CSS existe
ls -lh static/css/output.css
```

## 🐛 Dépannage

### CSS non chargé / Classes non appliquées

1. **Vérifier que le fichier CSS existe**
```bash
ls -lh static/css/output.css
```

2. **Recompiler le CSS**
```bash
npm run build
```

3. **Vider le cache du navigateur**
- Chrome/Edge : `Ctrl + Shift + R`
- Firefox : `Ctrl + F5`

4. **Vérifier les chemins dans tailwind.config.js**
```javascript
content: [
  "./templates/**/*.html",
  "./static/**/*.js",
  "./*/templates/**/*.html",  // Templates dans les apps
  "./**/*.py"
]
```

### Classes custom non appliquées

Si vos classes `.btn-primary`, `.card`, etc. ne fonctionnent pas :

1. **Vérifier que `static/src/input.css` contient les directives**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

2. **Recompiler**
```bash
npm run build
```

### Erreur "tailwindcss not found"

```bash
# Réinstaller les dépendances
rm -rf node_modules package-lock.json
npm install
```

### Le watch ne détecte pas les modifications

1. **Arrêter le watch** : `Ctrl + C`
2. **Relancer** : `npm run dev`

Si le problème persiste, vérifiez les chemins dans `tailwind.config.js`.

## 📁 Structure des fichiers

```
eschool/
├── static/
│   ├── src/
│   │   └── input.css          # Source avec directives Tailwind
│   └── css/
│       └── output.css         # Fichier compilé (généré)
├── templates/
│   ├── base.html              # Template principal
│   └── ...
├── tailwind.config.js         # Configuration Tailwind
├── package.json               # Dépendances Node.js
└── node_modules/              # Packages Node.js (ignoré par Git)
```

## 🔄 Git workflow

Le fichier `static/css/output.css` est ignoré par Git (dans `.gitignore`).

Après un `git pull` :
```bash
npm install  # Si package.json a changé
npm run build  # Recompiler le CSS
```

## 📚 Ressources

- [Documentation Tailwind CSS](https://tailwindcss.com/docs)
- [Tailwind Cheat Sheet](https://nerdcave.com/tailwind-cheat-sheet)
- [Tailwind Play (playground)](https://play.tailwindcss.com/)

## ✅ Checklist développeur

Avant de commencer à coder :
- [ ] `npm install` (première fois uniquement)
- [ ] `npm run dev` (terminal 1)
- [ ] `python manage.py runserver` (terminal 2)
- [ ] Navigateur ouvert sur `http://localhost:8000`

Avant de commit :
- [ ] `npm run build` (build production)
- [ ] Tester les pages modifiées
- [ ] Vider le cache navigateur
- [ ] Vérifier que `static/css/output.css` existe (si vous l'avez en local)

---

**Pro tip** : Ajoutez ces alias dans votre `.bashrc` ou `.zshrc` :

```bash
alias tw-dev="cd /path/to/eschool && npm run dev"
alias tw-build="cd /path/to/eschool && npm run build"
alias dj-run="cd /path/to/eschool && python manage.py runserver"
```
