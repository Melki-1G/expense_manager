# 🔧 Guide d'Installation - Mon Gestionnaire de Dépenses

Ce guide vous accompagne pas à pas pour installer et configurer l'application sur votre machine locale.

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.11 ou supérieur** : [Télécharger Python](https://www.python.org/downloads/)
- **Node.js 18 ou supérieur** : [Télécharger Node.js](https://nodejs.org/)
- **pnpm** (recommandé) ou npm : `npm install -g pnpm`
- **Git** : [Télécharger Git](https://git-scm.com/)

## 🚀 Installation Rapide

### 1. Cloner le Projet

```bash
git clone https://github.com/votre-username/expense-manager.git
cd expense-manager
```

### 2. Configuration du Backend Django

```bash
# Naviguer vers le dossier backend
cd backend

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur macOS/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations de base de données
python manage.py migrate

# Créer des catégories par défaut
python manage.py shell
>>> from expenses.models import Category
>>> categories = [
...     {'name': 'Alimentation', 'color': '#FF6B6B', 'description': 'Courses, restaurants, etc.'},
...     {'name': 'Transport', 'color': '#4ECDC4', 'description': 'Essence, transports en commun, etc.'},
...     {'name': 'Logement', 'color': '#45B7D1', 'description': 'Loyer, charges, etc.'},
...     {'name': 'Loisirs', 'color': '#96CEB4', 'description': 'Sorties, hobbies, etc.'},
...     {'name': 'Santé', 'color': '#FFEAA7', 'description': 'Médecin, pharmacie, etc.'}
... ]
>>> for cat_data in categories:
...     Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
>>> exit()

# (Optionnel) Créer un compte administrateur
python manage.py createsuperuser

# Démarrer le serveur backend
python manage.py runserver 0.0.0.0:8000
```

Le backend sera accessible à l'adresse : http://localhost:8000

### 3. Configuration du Frontend React

Ouvrez un nouveau terminal et exécutez :

```bash
# Naviguer vers le dossier frontend
cd frontend/expense-manager-frontend

# Installer les dépendances
pnpm install

# Démarrer le serveur de développement
pnpm run dev --host
```

Le frontend sera accessible à l'adresse : http://localhost:5173

## 🎯 Première Utilisation

1. **Accédez à l'application** : Ouvrez http://localhost:5173 dans votre navigateur
2. **Créez un compte** : Cliquez sur "Créer un compte" et remplissez le formulaire
3. **Explorez le tableau de bord** : Une fois connecté, vous arriverez sur le tableau de bord
4. **Ajoutez votre première dépense** : Cliquez sur "Nouvelle dépense" pour commencer

## 🔧 Configuration Avancée

### Variables d'Environnement

Créez un fichier `.env` dans le dossier `backend/` pour personnaliser la configuration :

```env
# backend/.env
DEBUG=True
SECRET_KEY=votre-clé-secrète-très-longue-et-sécurisée
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données (optionnel - SQLite par défaut)
DATABASE_URL=sqlite:///db.sqlite3

# Email (pour les notifications - optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### Base de Données PostgreSQL (Optionnel)

Pour utiliser PostgreSQL au lieu de SQLite :

```bash
# Installer le driver PostgreSQL
pip install psycopg2-binary

# Modifier settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'expense_manager',
        'USER': 'votre_utilisateur',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🐳 Installation avec Docker (Optionnel)

Si vous préférez utiliser Docker :

```bash
# Créer le fichier docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=1
    
  frontend:
    build: ./frontend/expense-manager-frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/expense-manager-frontend:/app
    depends_on:
      - backend

# Démarrer les services
docker-compose up --build
```

## 🧪 Tests

### Tester le Backend

```bash
cd backend
python manage.py test
```

### Tester le Frontend

```bash
cd frontend/expense-manager-frontend
pnpm run test
```

## 🚀 Déploiement en Production

### Backend (avec Gunicorn)

```bash
# Installer Gunicorn
pip install gunicorn

# Collecter les fichiers statiques
python manage.py collectstatic

# Démarrer avec Gunicorn
gunicorn expense_manager_backend.wsgi:application --bind 0.0.0.0:8000
```

### Frontend (Build de Production)

```bash
cd frontend/expense-manager-frontend

# Créer le build de production
pnpm run build

# Les fichiers sont dans le dossier 'dist/'
# Servir avec Nginx, Apache, ou un CDN
```

## 🔍 Dépannage

### Problèmes Courants

**Erreur CORS** : Vérifiez que `django-cors-headers` est installé et configuré dans `settings.py`

**Port déjà utilisé** : Changez le port avec `python manage.py runserver 8001` ou `pnpm run dev --port 3000`

**Erreur de migration** : Supprimez `db.sqlite3` et relancez `python manage.py migrate`

**Modules non trouvés** : Vérifiez que l'environnement virtuel est activé et que les dépendances sont installées

### Logs et Debug

- **Backend** : Les logs Django s'affichent dans le terminal
- **Frontend** : Ouvrez les outils de développement du navigateur (F12)
- **API** : Testez les endpoints avec l'interface admin Django ou Postman

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez que tous les prérequis sont installés
2. Consultez les logs d'erreur
3. Vérifiez que les ports 8000 et 5173 sont libres
4. Assurez-vous que les deux serveurs (Django et React) sont démarrés

## 🎉 Félicitations !

Votre application Mon Gestionnaire de Dépenses est maintenant prête à l'emploi ! 

Vous pouvez commencer à :
- Créer des catégories personnalisées
- Ajouter vos dépenses et revenus
- Configurer vos factures récurrentes
- Analyser vos habitudes financières

Bon développement ! 🚀

