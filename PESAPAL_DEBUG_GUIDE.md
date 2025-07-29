# PesaPal Integration Debugging Guide

## Overview
This guide helps you debug PesaPal payment integration issues with detailed error handling and logging.

## Enhanced Error Handling Features

### 1. Detailed Logging
- All PesaPal API calls are now logged with request/response details
- Logs are saved to both console and `app.log` file
- Structured logging with timestamps and log levels

### 2. Comprehensive Error Messages
- Specific validation errors for missing fields
- Detailed PesaPal API error responses
- Network connectivity error handling
- JSON parsing error handling

### 3. Debug Endpoint
- Access `/api/debug/pesapal-config` to check your configuration
- Tests PesaPal connectivity automatically
- Shows configuration status without exposing secrets

## Common Error Scenarios and Solutions

### 1. "Failed to initiate payment" - No Specific Error

**Possible Causes:**
- Missing or invalid PesaPal credentials
- Network connectivity issues
- Invalid request format
- PesaPal API errors

**Debugging Steps:**
1. Check the application logs (`app.log` file)
2. Use the debug endpoint: `GET /api/debug/pesapal-config`
3. Look for specific error messages in the logs

### 2. Authentication Errors

**Common Issues:**
- Invalid consumer key/secret
- Wrong PesaPal environment (sandbox vs production)
- Expired credentials

**Solutions:**
```python
# Check your config.py file
PESAPAL_CONSUMER_KEY = "your_actual_key"
PESAPAL_CONSUMER_SECRET = "your_actual_secret"
PESAPAL_BASE_URL = "https://cybqa.pesapal.com"  # Sandbox
# or "https://www.pesapal.com" for production
```

### 3. Validation Errors

**Missing Fields:**
- `resource_id`: Must be a valid resource ID
- `email`: Must be a valid email format
- `amount`: Must be a positive number
- `name`: Customer's full name
- `phone`: Phone number (format: 254700000000)

**Example Valid Request:**
```json
{
  "resource_id": 1,
  "email": "customer@example.com",
  "amount": 100.50,
  "name": "John Doe",
  "phone": "254700000000"
}
```

### 4. PesaPal API Errors

**Common PesaPal Error Codes:**
- `INVALID_CALLBACK_URL`: Check your callback URL format
- `INVALID_AMOUNT`: Amount must be positive and in KES
- `INVALID_CURRENCY`: Must be "KES"
- `INVALID_BILLING_ADDRESS`: Check phone number format

## Debugging Tools

### 1. Test Script
Run the provided test script:
```bash
python test_pesapal.py
```

Update the configuration in the script:
```python
BASE_URL = "http://localhost:5000"  # Your server URL
PESAPAL_BASE_URL = "https://cybqa.pesapal.com"  # Your PesaPal environment
CONSUMER_KEY = "your_actual_key"
CONSUMER_SECRET = "your_actual_secret"
```

### 2. Debug Endpoint
```bash
curl http://localhost:5000/api/debug/pesapal-config
```

### 3. Log Analysis
Check the `app.log` file for detailed information:
```bash
tail -f app.log
```

## Log Examples

### Successful Payment Flow
```
2024-01-15 10:30:00 - __main__ - INFO - === PESAPAL PAYMENT REQUEST START ===
2024-01-15 10:30:00 - __main__ - INFO - Payment request data: {'resource_id': 1, 'email': 'test@example.com', ...}
2024-01-15 10:30:01 - __main__ - INFO - === PESAPAL TOKEN REQUEST START ===
2024-01-15 10:30:02 - __main__ - INFO - PesaPal token received successfully
2024-01-15 10:30:03 - __main__ - INFO - PesaPal order response status: 200
2024-01-15 10:30:03 - __main__ - INFO - Payment initiated successfully
```

### Error Examples
```
2024-01-15 10:30:00 - __main__ - ERROR - Payment validation failed: Missing required fields: email, phone
2024-01-15 10:30:01 - __main__ - ERROR - PesaPal authentication failed (Status: 401): Invalid credentials
2024-01-15 10:30:02 - __main__ - ERROR - PesaPal order request failed: {'status_code': 400, 'response_text': 'Invalid callback URL'}
```

## Configuration Checklist

### Environment Variables
- [ ] `PESAPAL_CONSUMER_KEY` is set
- [ ] `PESAPAL_CONSUMER_SECRET` is set
- [ ] `PESAPAL_BASE_URL` is correct (sandbox/production)
- [ ] `PESAPAL_NOTIFICATION_ID` is set (optional)

### Callback URL
- [ ] Callback URL is publicly accessible
- [ ] URL format: `https://yourdomain.com/api/pesapal-callback`
- [ ] HTTPS is enabled (required by PesaPal)

### Network
- [ ] Server can reach PesaPal API endpoints
- [ ] No firewall blocking outbound HTTPS requests
- [ ] DNS resolution works for PesaPal domains

## Testing Steps

1. **Test Configuration:**
   ```bash
   curl http://localhost:5000/api/debug/pesapal-config
   ```

2. **Test Authentication:**
   - Check if you can get an access token
   - Verify credentials are correct

3. **Test Payment Request:**
   ```bash
   curl -X POST http://localhost:5000/api/pay \
     -H "Content-Type: application/json" \
     -d '{"resource_id": 1, "email": "test@example.com", "amount": 100, "name": "Test User", "phone": "254700000000"}'
   ```

4. **Check Logs:**
   ```bash
   tail -f app.log
   ```

## Common Solutions

### If PesaPal credentials are not configured:
The system will automatically use test mode and return a success response.

### If you get timeout errors:
- Check your internet connection
- Verify PesaPal API endpoints are accessible
- Consider increasing timeout values

### If you get JSON parsing errors:
- PesaPal might be returning HTML error pages
- Check if the API endpoint is correct
- Verify your request format

### If callback URL is invalid:
- Ensure the URL is publicly accessible
- Use HTTPS (required by PesaPal)
- Check the URL format in your configuration

## Support

If you're still experiencing issues:
1. Check the detailed logs in `app.log`
2. Use the debug endpoint to verify configuration
3. Test with the provided test script
4. Verify your PesaPal account status and credentials 