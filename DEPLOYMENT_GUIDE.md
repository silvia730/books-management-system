# PesaPal IPN System Deployment Guide

This guide will help you deploy your Flask backend with PesaPal IPN integration to production.

## 🚀 Quick Deployment Options

### Option 1: Render (Recommended for beginners)

1. **Sign up for Render** at https://render.com
2. **Connect your GitHub repository**
3. **Create a new Web Service**
4. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Environment:** Python 3.11

5. **Add Environment Variables:**
   ```
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_NAME=your_db_name
   PESAPAL_CONSUMER_KEY=your_pesapal_consumer_key
   PESAPAL_CONSUMER_SECRET=your_pesapal_consumer_secret
   PESAPAL_IPN_SECRET=your_secure_ipn_secret_key
   SECRET_KEY=your_very_secure_secret_key_here
   ```

6. **Deploy!** Your app will be available at `https://your-app-name.onrender.com`

### Option 2: Railway

1. **Sign up for Railway** at https://railway.app
2. **Connect your GitHub repository**
3. **Railway will auto-detect Python and deploy**
4. **Add environment variables in the Railway dashboard**
5. **Your app will be available at `https://your-app-name.railway.app`**

### Option 3: Heroku

1. **Install Heroku CLI**
2. **Login to Heroku:** `heroku login`
3. **Create app:** `heroku create your-app-name`
4. **Add PostgreSQL:** `heroku addons:create heroku-postgresql:mini`
5. **Set environment variables:**
   ```bash
   heroku config:set PESAPAL_CONSUMER_KEY=your_key
   heroku config:set PESAPAL_CONSUMER_SECRET=your_secret
   heroku config:set PESAPAL_IPN_SECRET=your_ipn_secret
   heroku config:set SECRET_KEY=your_secret_key
   ```
6. **Deploy:** `git push heroku main`

## 🗄️ Database Setup

### Option 1: Render PostgreSQL (Free tier available)
1. Create a PostgreSQL service in Render
2. Use the provided connection string
3. Update your environment variables

### Option 2: Railway PostgreSQL
1. Add PostgreSQL service in Railway
2. Railway automatically provides connection details

### Option 3: PlanetScale (MySQL)
1. Sign up at https://planetscale.com
2. Create a new database
3. Use the connection string provided

## 🔧 Environment Variables

Copy `env.example` to `.env` and fill in your values:

```bash
# Database Configuration
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_NAME=your_db_name

# PesaPal Configuration
PESAPAL_CONSUMER_KEY=your_pesapal_consumer_key
PESAPAL_CONSUMER_SECRET=your_pesapal_consumer_secret
PESAPAL_IPN_SECRET=your_secure_ipn_secret_key
PESAPAL_BASE_URL=https://pay.pesapal.com/v3/api

# Flask Configuration
SECRET_KEY=your_very_secure_secret_key_here
FLASK_ENV=production

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log

# Security Configuration
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## 🔐 PesaPal IPN Configuration

### 1. Get Your PesaPal Credentials
1. Log into your PesaPal merchant dashboard
2. Go to **Settings > API Credentials**
3. Copy your Consumer Key and Consumer Secret

### 2. Configure IPN URL in PesaPal Dashboard
1. In your PesaPal merchant dashboard, go to **Settings > IPN Configuration**
2. Set your IPN URL to: `https://your-domain.com/api/pesapal/ipn`
3. Save the configuration

### 3. Test IPN (Sandbox)
1. Use PesaPal's sandbox environment first
2. Make a test payment
3. Check your logs to ensure IPN is received
4. Verify payment status updates in your database

## 📊 Monitoring and Logs

### View Logs
- **Render:** Dashboard > Your Service > Logs
- **Railway:** Dashboard > Your Service > Logs
- **Heroku:** `heroku logs --tail`

### Monitor Payments
Your app includes these endpoints for monitoring:

- `GET /api/payments` - View all payments (admin)
- `GET /api/payment/<order_tracking_id>` - Check specific payment status

## 🔒 Security Best Practices

1. **Use HTTPS only** - All deployment platforms provide this
2. **Secure your SECRET_KEY** - Use a strong, random key
3. **Validate IPN requests** - The system validates with PesaPal API
4. **Rate limiting** - Enabled by default
5. **Host validation** - Configure ALLOWED_HOSTS for your domain

## 🧪 Testing Your IPN

### 1. Local Testing (ngrok)
```bash
# Install ngrok
npm install -g ngrok

# Start your Flask app
python app.py

# In another terminal, expose your local server
ngrok http 5000

# Use the ngrok URL as your IPN URL for testing
# Example: https://abc123.ngrok.io/api/pesapal/ipn
```

### 2. Test Payment Flow
1. Make a test payment through your frontend
2. Check the payment record is created in your database
3. Complete the payment on PesaPal
4. Verify IPN is received and payment status is updated
5. Test resource download with completed payment

## 🚨 Troubleshooting

### Common Issues

1. **IPN not received:**
   - Check your IPN URL is correct in PesaPal dashboard
   - Verify your server is accessible from the internet
   - Check server logs for errors

2. **Payment status not updating:**
   - Verify PesaPal credentials are correct
   - Check if IPN endpoint is responding with 200 status
   - Review logs for API errors

3. **Database connection issues:**
   - Verify database credentials
   - Check if database is accessible from your deployment platform
   - Run database migrations: `flask db upgrade`

### Debug Mode
For debugging, temporarily set:
```
LOG_LEVEL=DEBUG
FLASK_ENV=development
```

## 📈 Production Checklist

- [ ] Deployed to production platform
- [ ] Database configured and migrated
- [ ] Environment variables set
- [ ] PesaPal credentials configured
- [ ] IPN URL registered in PesaPal dashboard
- [ ] HTTPS enabled
- [ ] Logs monitoring set up
- [ ] Test payment completed successfully
- [ ] IPN received and processed
- [ ] Resource download working
- [ ] Security headers configured
- [ ] Backup strategy in place

## 🆘 Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables are set
3. Test with PesaPal sandbox first
4. Contact PesaPal support for payment-specific issues

Your IPN system is now ready for production! 🎉 