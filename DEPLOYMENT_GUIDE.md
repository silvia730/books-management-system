# 🚀 School Management System - Deployment Guide

## 📋 Overview

This guide will help you deploy the School Management System with both the backend API and frontend dashboards.

## 🏗️ Project Structure

```
school-management-system/
├── backend/                 # Flask API backend
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── config.py           # Configuration
│   └── static/             # Static files (covers, etc.)
├── admin/                  # Admin dashboard frontend
│   ├── admin.html          # Admin dashboard
│   ├── admin.css           # Admin styles
│   ├── admin-script.js     # Admin JavaScript
│   └── assets/             # Admin images
├── user/                   # User dashboard frontend
│   ├── index.html          # User dashboard
│   ├── style.css           # User styles
│   ├── script.js           # User JavaScript
│   ├── resources.html      # Resources page
│   ├── resources.js        # Resources JavaScript
│   └── assets/             # User images
└── migrations/             # Database migrations
```

## 🔧 Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend` directory:

```env
FLASK_APP=app.py
FLASK_ENV=production
DATABASE_URL=your_database_url_here
PESAPAL_CONSUMER_KEY=your_pesapal_key
PESAPAL_CONSUMER_SECRET=your_pesapal_secret
PESAPAL_BASE_URL=https://pay.pesapal.com/v3/api
PESAPAL_NOTIFICATION_ID=your_notification_id
```

### 3. Database Setup

```bash
cd backend
flask db upgrade
```

## 🌐 Deployment Options

### Option 1: Render.com (Recommended)

1. **Create a new Web Service**
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn app:app`
   - **Root Directory:** Leave empty (or set to `backend` if needed)

4. **Environment Variables:**
   - Add all variables from your `.env` file

5. **Deploy**

### Option 2: Heroku

1. **Create a new Heroku app**
2. **Add PostgreSQL addon**
3. **Set environment variables:**
   ```bash
   heroku config:set FLASK_APP=app.py
   heroku config:set FLASK_ENV=production
   heroku config:set DATABASE_URL=your_database_url
   # ... add other variables
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Option 3: VPS/Server

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```

2. **Setup the application:**
   ```bash
   cd /var/www/school-management-system
   pip3 install -r backend/requirements.txt
   ```

3. **Configure Gunicorn:**
   ```bash
   sudo nano /etc/systemd/system/school-management.service
   ```

   ```ini
   [Unit]
   Description=School Management System
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/school-management-system/backend
   Environment="PATH=/var/www/school-management-system/backend/venv/bin"
   ExecStart=/var/www/school-management-system/backend/venv/bin/gunicorn --workers 3 --bind unix:school-management.sock -m 007 app:app

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start the service:**
   ```bash
   sudo systemctl start school-management
   sudo systemctl enable school-management
   ```

## 🔗 URL Structure

After deployment, your application will have these URLs:

- **API Base:** `https://your-domain.com/api`
- **Admin Dashboard:** `https://your-domain.com/admin`
- **User Dashboard:** `https://your-domain.com/user`
- **Resources Page:** `https://your-domain.com/user/resources.html`

## 🧪 Testing Deployment

### 1. Run the Path Test

```bash
python test_deployment_paths.py
```

This will verify all required files are present.

### 2. Test API Endpoints

```bash
# Test API health
curl https://your-domain.com/api/resources

# Test admin dashboard
curl https://your-domain.com/admin

# Test user dashboard
curl https://your-domain.com/user
```

### 3. Test Admin Login

- **URL:** `https://your-domain.com/admin`
- **Username:** `admin`
- **Password:** `admin123`

## 🔒 Security Considerations

### 1. Change Default Admin Password

After first login, change the admin password through the settings page.

### 2. Environment Variables

Never commit sensitive information like API keys to version control.

### 3. HTTPS

Always use HTTPS in production. Most deployment platforms provide this automatically.

### 4. Database Security

- Use strong database passwords
- Restrict database access to your application only
- Regular backups

## 🐛 Troubleshooting

### Common Issues

1. **"Admin dashboard not found"**
   - Check if `admin/admin.html` exists
   - Verify file permissions
   - Check the file path in Flask routes

2. **"Static files not loading"**
   - Verify CSS/JS files exist
   - Check file permissions
   - Ensure correct file paths

3. **"Database connection failed"**
   - Check DATABASE_URL environment variable
   - Verify database is running
   - Check network connectivity

4. **"PesaPal integration not working"**
   - Verify PesaPal credentials
   - Check callback URLs
   - Ensure HTTPS is enabled

### Debug Mode

For local development, you can run in debug mode:

```bash
cd backend
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## 📞 Support

If you encounter issues:

1. Check the logs in your deployment platform
2. Run the test scripts provided
3. Verify all environment variables are set
4. Check file permissions and paths

## 🎉 Success Checklist

- [ ] All files are present (run `test_deployment_paths.py`)
- [ ] Database is connected and migrated
- [ ] Environment variables are set
- [ ] Admin dashboard is accessible
- [ ] User dashboard is accessible
- [ ] API endpoints are working
- [ ] PesaPal integration is configured
- [ ] HTTPS is enabled
- [ ] Admin password is changed

---

**Happy Deploying! 🚀** 