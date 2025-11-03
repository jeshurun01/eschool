# 🚀 Render Deployment - Quick Start

Your Django eSchool application is now ready to deploy on Render!

## ✅ What's Been Prepared

1. **requirements.txt** - Python dependencies for production
2. **build.sh** - Automated build script (installs deps, builds Tailwind, collects static files, runs migrations)
3. **core/settings.py** - Updated with:
   - DATABASE_URL support for PostgreSQL
   - RENDER_EXTERNAL_HOSTNAME for dynamic allowed hosts
   - WhiteNoise for static files in production
4. **docs/RENDER_DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
5. **.env.render.example** - Template for environment variables

All files have been committed and pushed to GitHub ✅

## 🎯 Next Steps (Simple Overview)

### 1. Create Render Account
Go to https://render.com and sign up (free tier available)

### 2. Create PostgreSQL Database
- Click "New +" → "PostgreSQL"
- Name: `eschool-db`
- Select **Free** tier
- Wait ~2 minutes for creation
- Copy the **Internal Database URL**

### 3. Create Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repo: `jeshurun01/eschool`
- Configure:
  - **Build Command:** `./build.sh`
  - **Start Command:** `gunicorn core.wsgi:application`
  - **Environment:** Python 3

### 4. Set Environment Variables
In the Web Service environment tab, add:

```
SECRET_KEY=<generate-strong-key>
DEBUG=False
DATABASE_URL=<paste-from-postgresql>
RENDER_EXTERNAL_HOSTNAME=<your-app>.onrender.com
PYTHON_VERSION=3.12.9
```

Generate SECRET_KEY with:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Deploy!
Click "Create Web Service" and wait 5-10 minutes for the first deployment.

### 6. Create Admin User
Once deployed, use Render Shell:
```bash
python manage.py createsuperuser
```

### 7. Access Your App
Visit: `https://<your-app>.onrender.com`

## 📖 Full Documentation

See **docs/RENDER_DEPLOYMENT_GUIDE.md** for:
- Detailed step-by-step instructions
- Troubleshooting guide
- Environment variables reference
- Security best practices
- Custom domain setup
- Monitoring and logs

## 🎓 Render Plans

- **Free:** 512MB RAM, sleeps after 15 min inactivity (good for testing)
- **Starter:** $7/month, always on (recommended for production)
- **Standard:** $25/month, 2GB RAM (for higher traffic)

## 🆘 Need Help?

1. Check the logs in Render dashboard
2. Read **docs/RENDER_DEPLOYMENT_GUIDE.md**
3. Render documentation: https://render.com/docs
4. GitHub issues: https://github.com/jeshurun01/eschool/issues

---

**Ready to deploy?** Follow the steps above or read the full guide in `docs/RENDER_DEPLOYMENT_GUIDE.md` 🚀
