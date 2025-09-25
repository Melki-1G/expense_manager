# 🚀 Guide de Déploiement - Mon Gestionnaire de Dépenses

Ce guide explique comment déployer l'application en production sur différentes plateformes.

## 🌐 Options de Déploiement

### 1. Déploiement sur Heroku (Recommandé pour débuter)

#### Backend Django

```bash
# Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Se connecter à Heroku
heroku login

# Créer l'application
heroku create votre-app-backend

# Ajouter les variables d'environnement
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=votre-clé-secrète-très-longue
heroku config:set ALLOWED_HOSTS=votre-app-backend.herokuapp.com

# Créer le fichier Procfile dans backend/
echo "web: gunicorn expense_manager_backend.wsgi:application --log-file -" > Procfile

# Ajouter gunicorn aux requirements
echo "gunicorn==21.2.0" >> requirements.txt

# Déployer
git subtree push --prefix=backend heroku main
```

#### Frontend React

```bash
# Build de production
cd frontend/expense-manager-frontend
pnpm run build

# Déployer sur Netlify, Vercel, ou GitHub Pages
# Voir sections spécifiques ci-dessous
```

### 2. Déploiement sur DigitalOcean/VPS

#### Prérequis Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib nodejs npm -y

# Installation de pnpm
sudo npm install -g pnpm
```

#### Configuration Backend

```bash
# Cloner le projet
git clone https://github.com/votre-username/expense-manager.git
cd expense-manager/backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Configuration PostgreSQL
sudo -u postgres createdb expense_manager
sudo -u postgres createuser --interactive

# Variables d'environnement
cat > .env << EOF
DEBUG=False
SECRET_KEY=votre-clé-secrète-très-longue-et-sécurisée
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
DATABASE_URL=postgresql://user:password@localhost/expense_manager
EOF

# Migrations et collecte des fichiers statiques
python manage.py migrate
python manage.py collectstatic --noinput

# Service systemd pour Gunicorn
sudo tee /etc/systemd/system/expense-manager.service << EOF
[Unit]
Description=Expense Manager Django App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/expense-manager/backend
Environment="PATH=/home/ubuntu/expense-manager/backend/venv/bin"
ExecStart=/home/ubuntu/expense-manager/backend/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/expense-manager/backend/expense_manager.sock expense_manager_backend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Démarrer le service
sudo systemctl daemon-reload
sudo systemctl start expense-manager
sudo systemctl enable expense-manager
```

#### Configuration Nginx

```bash
# Configuration Nginx
sudo tee /etc/nginx/sites-available/expense-manager << EOF
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    # Backend API
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/expense-manager/backend/expense_manager.sock;
    }

    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/expense-manager/backend/expense_manager.sock;
    }

    # Fichiers statiques Django
    location /static/ {
        alias /home/ubuntu/expense-manager/backend/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/expense-manager/backend/media/;
    }

    # Frontend React
    location / {
        root /home/ubuntu/expense-manager/frontend/expense-manager-frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/expense-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Configuration Frontend

```bash
# Build du frontend
cd /home/ubuntu/expense-manager/frontend/expense-manager-frontend

# Modifier l'URL de l'API pour la production
# Dans src/lib/api.js, changer :
# const API_BASE_URL = 'https://votre-domaine.com';

pnpm install
pnpm run build
```

### 3. Déploiement Frontend sur Netlify

```bash
# Dans frontend/expense-manager-frontend/
pnpm run build

# Créer le fichier _redirects pour le routing React
echo "/*    /index.html   200" > dist/_redirects

# Déployer via Netlify CLI
npm install -g netlify-cli
netlify login
netlify deploy --prod --dir=dist
```

### 4. Déploiement Frontend sur Vercel

```bash
# Installer Vercel CLI
npm install -g vercel

# Dans frontend/expense-manager-frontend/
vercel --prod
```

### 5. Déploiement avec Docker

#### Dockerfile Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "expense_manager_backend.wsgi:application"]
```

#### Dockerfile Frontend

```dockerfile
# frontend/expense-manager-frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: expense_manager
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://postgres:password@db:5432/expense_manager
    depends_on:
      - db
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  frontend:
    build: ./frontend/expense-manager-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/static
      - media_volume:/media
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

## 🔒 Configuration HTTPS avec Let's Encrypt

```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtenir le certificat SSL
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique
sudo crontab -e
# Ajouter : 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring et Logs

### Logs Backend

```bash
# Logs Gunicorn
sudo journalctl -u expense-manager -f

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Monitoring avec Sentry (Optionnel)

```bash
# Installation
pip install sentry-sdk[django]

# Configuration dans settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="VOTRE_DSN_SENTRY",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

## 🔧 Variables d'Environnement Production

### Backend (.env)

```env
DEBUG=False
SECRET_KEY=votre-clé-secrète-très-longue-et-sécurisée-pour-production
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
DATABASE_URL=postgresql://user:password@localhost/expense_manager

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Sentry (optionnel)
SENTRY_DSN=https://votre-dsn@sentry.io/projet

# AWS S3 (pour les fichiers media - optionnel)
AWS_ACCESS_KEY_ID=votre-access-key
AWS_SECRET_ACCESS_KEY=votre-secret-key
AWS_STORAGE_BUCKET_NAME=votre-bucket
AWS_S3_REGION_NAME=eu-west-1
```

### Frontend (.env.production)

```env
VITE_API_BASE_URL=https://votre-domaine.com
VITE_SENTRY_DSN=https://votre-dsn@sentry.io/projet
```

## 🚀 Automatisation du Déploiement

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd /home/ubuntu/expense-manager
          git pull origin main
          cd backend
          source venv/bin/activate
          pip install -r requirements.txt
          python manage.py migrate
          python manage.py collectstatic --noinput
          sudo systemctl restart expense-manager
          cd ../frontend/expense-manager-frontend
          pnpm install
          pnpm run build
          sudo systemctl reload nginx
```

## 📋 Checklist de Déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données migrée
- [ ] Fichiers statiques collectés
- [ ] HTTPS configuré
- [ ] Monitoring en place
- [ ] Sauvegardes automatiques configurées
- [ ] Tests de charge effectués
- [ ] Documentation mise à jour

## 🆘 Dépannage Production

### Problèmes Courants

**500 Internal Server Error** : Vérifiez les logs Gunicorn et Django
**502 Bad Gateway** : Vérifiez que Gunicorn fonctionne et que Nginx peut s'y connecter
**CORS Errors** : Vérifiez la configuration CORS dans Django
**Static Files 404** : Vérifiez la configuration Nginx pour les fichiers statiques

### Commandes Utiles

```bash
# Redémarrer les services
sudo systemctl restart expense-manager
sudo systemctl restart nginx

# Vérifier les statuts
sudo systemctl status expense-manager
sudo systemctl status nginx

# Tester la configuration Nginx
sudo nginx -t

# Voir les processus
ps aux | grep gunicorn
```

## 🎉 Félicitations !

Votre application est maintenant déployée en production ! N'oubliez pas de :

- Configurer des sauvegardes régulières
- Mettre en place un monitoring
- Tester régulièrement vos sauvegardes
- Maintenir vos dépendances à jour

Bon déploiement ! 🚀

