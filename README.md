# School Management System with PesaPal IPN Integration

A comprehensive school management system with secure PesaPal payment integration and Instant Payment Notification (IPN) handling.

## 🚀 Features

- **Resource Management**: Upload and manage books, papers, and setbooks
- **Secure Payments**: PesaPal integration with IPN handling
- **User Management**: Registration, login, and password management
- **Payment Tracking**: Complete payment history and status tracking
- **Resource Downloads**: Secure file downloads after payment verification
- **Admin Dashboard**: Monitor payments and manage resources

## 🔐 PesaPal IPN System

This system includes a production-ready IPN (Instant Payment Notification) endpoint that:

- ✅ Receives payment status updates from PesaPal
- ✅ Validates payments with PesaPal API
- ✅ Updates payment records in real-time
- ✅ Logs all transactions for monitoring
- ✅ Handles errors gracefully
- ✅ Includes security measures (rate limiting, host validation)

## 📁 Project Structure

```
school management system/
├── backend/                 # Flask backend with IPN system
│   ├── app.py              # Main application with IPN endpoints
│   ├── models.py           # Database models including Payment
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── wsgi.py            # Production WSGI entry point
│   ├── Procfile           # Heroku deployment config
│   ├── runtime.txt        # Python version specification
│   └── env.example        # Environment variables template
├── admin/                  # Admin frontend
├── user/                   # User frontend
├── migrations/             # Database migrations
└── DEPLOYMENT_GUIDE.md    # Complete deployment guide
```

## 🛠️ Quick Start

### 1. Setup Backend

```bash
cd backend
pip install -r requirements.txt
python init_db.py
python app.py
```

### 2. Configure Environment Variables

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

# Flask Configuration
SECRET_KEY=your_very_secure_secret_key_here
```

### 3. Configure PesaPal IPN

1. Log into your PesaPal merchant dashboard
2. Go to **Settings > IPN Configuration**
3. Set IPN URL to: `https://your-domain.com/api/pesapal/ipn`
4. Save the configuration

## 🔌 API Endpoints

### Payment Endpoints

- `POST /api/pay` - Initiate payment
- `GET /api/pesapal/ipn` - PesaPal IPN endpoint
- `GET /api/payments` - Get all payments (admin)
- `GET /api/payment/<order_tracking_id>` - Get specific payment status

### Resource Endpoints

- `POST /api/upload` - Upload resource
- `GET /api/resources` - Get all resources
- `DELETE /api/resource/<id>` - Delete resource
- `GET /api/download/<resource_id>` - Download resource (requires payment)

### User Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/change_password` - Change password
- `GET /api/users` - Get user count

## 🔒 IPN Security Features

### 1. Request Validation
- Validates all required IPN parameters
- Checks payment existence in database
- Verifies payment status with PesaPal API

### 2. Security Measures
- Rate limiting on IPN endpoint
- Host validation
- Comprehensive logging
- Error handling and recovery

### 3. Payment Verification
```python
# IPN endpoint validates payments with PesaPal API
status_url = f"{PESAPAL_BASE_URL}/Transactions/GetTransactionStatus?orderTrackingId={merchant_reference}"
status_resp = requests.get(status_url, headers={'Authorization': f'Bearer {access_token}'})
```

## 📊 Payment Flow

1. **Payment Initiation**
   - User selects resource to download
   - System creates PesaPal order
   - Payment record stored in database

2. **IPN Processing**
   - PesaPal sends IPN to `/api/pesapal/ipn`
   - System validates payment with PesaPal API
   - Payment status updated in database

3. **Resource Access**
   - User can download resource after payment completion
   - System verifies payment status before allowing download

## 🚀 Deployment

### Quick Deploy to Render

1. **Sign up for Render** at https://render.com
2. **Connect your GitHub repository**
3. **Create a new Web Service**
4. **Configure:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
5. **Add environment variables**
6. **Deploy!**

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🧪 Testing

### Local Testing with ngrok

```bash
# Install ngrok
npm install -g ngrok

# Start your Flask app
python app.py

# Expose local server
ngrok http 5000

# Use ngrok URL as IPN URL for testing
# Example: https://abc123.ngrok.io/api/pesapal/ipn
```

### Test Payment Flow

1. Make a test payment through your frontend
2. Check payment record is created in database
3. Complete payment on PesaPal
4. Verify IPN is received and status updated
5. Test resource download with completed payment

## 📈 Monitoring

### View Logs
- All IPN requests are logged with full details
- Payment status changes are tracked
- Error conditions are logged for debugging

### Payment Monitoring
- `GET /api/payments` - View all payments
- `GET /api/payment/<order_tracking_id>` - Check specific payment

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PESAPAL_CONSUMER_KEY` | Your PesaPal consumer key | Yes |
| `PESAPAL_CONSUMER_SECRET` | Your PesaPal consumer secret | Yes |
| `PESAPAL_IPN_SECRET` | Secret key for IPN validation | Yes |
| `DB_USER` | Database username | Yes |
| `DB_PASSWORD` | Database password | Yes |
| `DB_HOST` | Database host | Yes |
| `DB_NAME` | Database name | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | No |

## 🚨 Troubleshooting

### Common Issues

1. **IPN not received**
   - Check IPN URL is correct in PesaPal dashboard
   - Verify server is accessible from internet
   - Check server logs for errors

2. **Payment status not updating**
   - Verify PesaPal credentials are correct
   - Check IPN endpoint responds with 200 status
   - Review logs for API errors

3. **Database connection issues**
   - Verify database credentials
   - Check database accessibility
   - Run `python init_db.py` to create tables

## 📞 Support

For issues related to:
- **PesaPal integration**: Contact PesaPal support
- **Deployment**: Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Code issues**: Check logs and environment variables

## 📄 License

This project is for educational purposes. Please ensure compliance with PesaPal's terms of service.

---

**Your PesaPal IPN system is now ready for production! 🎉** 