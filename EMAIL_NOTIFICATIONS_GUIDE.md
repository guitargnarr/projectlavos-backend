# Email Notifications System - Setup & Testing Guide

## Overview

SendGrid-powered email notification system with:
- **HTML email templates** with responsive design
- **Automatic retry logic** (3 attempts with exponential backoff)
- **Three notification types**: contact form, alerts, custom
- **Error handling** with graceful degradation

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `sendgrid==6.11.0` - SendGrid Python SDK
- `tenacity==8.2.3` - Retry logic library

### 2. Get SendGrid API Key

1. Go to [SendGrid](https://app.sendgrid.com/)
2. Sign up or log in
3. Navigate to: Settings → API Keys
4. Create new API key with "Mail Send" permissions
5. Copy the key (you'll only see it once!)

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Required
SENDGRID_API_KEY=SG.your_actual_api_key_here
SENDGRID_FROM_EMAIL=noreply@projectlavos.com
NOTIFICATION_RECIPIENTS=matthewdscott7@gmail.com

# Optional (defaults shown)
SENDGRID_FROM_NAME=Project Lavos Notifications
EMAIL_MAX_RETRIES=3
EMAIL_RETRY_DELAY=2
```

**Important**:
- `SENDGRID_FROM_EMAIL` must be verified in SendGrid (Settings → Sender Authentication)
- For production, use a verified domain (not gmail/yahoo/etc.)
- `NOTIFICATION_RECIPIENTS` can be comma-separated for multiple recipients

### 4. Verify SendGrid Sender

Before sending emails, verify your sender email in SendGrid:

1. Go to: Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Fill in your email (matthewdscott7@gmail.com)
4. Check your inbox for verification email
5. Click verification link

---

## Testing

### Run Unit Tests

```bash
pytest test_email_notifications.py -v
```

Expected output:
```
test_email_notifications.py::TestEmailTemplates::test_contact_form_template PASSED
test_email_notifications.py::TestEmailTemplates::test_alert_template_info PASSED
test_email_notifications.py::TestEmailService::test_send_contact_form_notification PASSED
test_email_notifications.py::TestNotificationEndpoints::test_notify_contact_form PASSED
...
===================== 20 passed in 2.34s ======================
```

### Start the Server

```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

### Check Health Status

```bash
curl http://localhost:8000/health
```

Response should show:
```json
{
  "status": "healthy",
  "version": "1.5.0",
  "features": {
    "email_notifications": "enabled"
  }
}
```

If email_notifications shows "disabled (no API key)", check your `.env` file.

---

## API Usage Examples

### 1. Contact Form Notification

Send when someone submits a contact form:

```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "contact_form",
    "name": "John Doe",
    "email": "john@example.com",
    "business_type": "Healthcare",
    "challenge": "We need an AI solution for patient triage and prioritization"
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Contact form notification sent successfully",
  "details": {
    "status_code": 202
  }
}
```

**Email Template**: Professional HTML email with:
- Gradient header with Project Lavos branding
- Contact details in formatted boxes
- Action required notice
- Branded footer with links

### 2. Alert Notification

Send system alerts (high lead scores, security events, etc.):

**Info Alert**:
```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "alert",
    "alert_type": "System Update",
    "message": "Platform updated to v1.5.0 with email notifications feature",
    "severity": "info"
  }'
```

**Warning Alert** (High Lead Score):
```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "alert",
    "alert_type": "High Priority Lead",
    "message": "New lead scored 95/100. Contact details: John Doe (john@fortune500.com). Budget: $100K. Timeline: ASAP. Action required within 24 hours.",
    "severity": "warning"
  }'
```

**Error Alert** (Phishing Detected):
```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "alert",
    "alert_type": "Phishing Email Detected",
    "message": "High-risk phishing email detected. Sender: suspicious@fake-bank.com. Subject: Urgent - Account Suspended. Risk score: 95/100. Email has been quarantined.",
    "severity": "error"
  }'
```

**Success Alert**:
```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "alert",
    "alert_type": "Deployment Successful",
    "message": "Backend v1.5.0 deployed successfully to production. All health checks passing. Email notifications enabled.",
    "severity": "success"
  }'
```

**Severity Colors**:
- `info` - Blue background
- `warning` - Yellow background
- `error` - Red background
- `success` - Green background

### 3. Custom Notification

Send custom formatted notifications:

```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "custom",
    "subject": "Weekly Platform Report",
    "title": "Platform Usage Summary - Week of Nov 14",
    "body": "<h3>Key Metrics</h3><ul><li>Total API Calls: 1,247</li><li>New Leads Scored: 34</li><li>Phishing Emails Blocked: 12</li><li>Cache Hit Rate: 78%</li></ul><p><strong>Top Performing Demo:</strong> Restaurant Analyzer (456 requests)</p>"
  }'
```

**With Custom Recipients**:
```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "custom",
    "subject": "Client Report",
    "title": "Monthly Analysis Complete",
    "body": "<p>Your monthly sentiment analysis report is ready.</p>",
    "recipients": ["client@example.com", "manager@example.com"]
  }'
```

---

## Error Handling

### Missing Required Fields

```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "contact_form",
    "name": "John Doe"
  }'
```

Response (400 Bad Request):
```json
{
  "detail": "contact_form type requires: name, email, business_type, challenge"
}
```

### Invalid Notification Type

```bash
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "invalid_type"
  }'
```

Response (400 Bad Request):
```json
{
  "detail": "Invalid notification_type: invalid_type. Use: contact_form, alert, or custom"
}
```

### SendGrid Not Configured

If `SENDGRID_API_KEY` is not set or invalid:

Response (500 Internal Server Error):
```json
{
  "detail": "Email notification failed: SendGrid not configured. Set SENDGRID_API_KEY environment variable."
}
```

### SendGrid API Error

If SendGrid API fails, automatic retry logic kicks in:
- **Attempt 1**: Immediate
- **Attempt 2**: 2 seconds later
- **Attempt 3**: 4 seconds later
- **Final Failure**: Returns error after 3 attempts

---

## Integration Examples

### Trigger Email from Lead Scoring

After scoring a high-value lead, send immediate notification:

```bash
# 1. Score the lead
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah Johnson",
    "email": "sarah@bigcorp.com",
    "company": "Fortune 500 Healthcare",
    "budget": "100k+",
    "timeline": "urgent"
  }'

# Response: {"score": 95, "priority": "High", ...}

# 2. Send alert notification
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "alert",
    "alert_type": "High Priority Lead - 95/100",
    "message": "Name: Sarah Johnson\nEmail: sarah@bigcorp.com\nCompany: Fortune 500 Healthcare\nBudget: 100k+\nTimeline: urgent\n\nAction: Contact within 24 hours",
    "severity": "warning"
  }'
```

### Trigger Email from Phishing Detection

After detecting dangerous phishing:

```bash
# 1. Detect phishing
curl -X POST http://localhost:8000/api/phishing \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "urgent@paypal-verify.tk",
    "subject": "Urgent: Account Suspended - Verify Now",
    "body": "Click here to verify your account immediately or it will be deleted: http://bit.ly/suspiciouslink"
  }'

# Response: {"is_phishing": true, "risk_level": "Dangerous", ...}

# 2. Send alert
curl -X POST http://localhost:8000/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "notification_type": "alert",
    "alert_type": "Dangerous Phishing Email Detected",
    "message": "Sender: urgent@paypal-verify.tk\nSubject: Urgent: Account Suspended\nRisk: Dangerous (95% confidence)\nIndicators: Suspicious domain, urgent language, link shortener\n\nAction: Email quarantined automatically",
    "severity": "error"
  }'
```

---

## Testing Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Get SendGrid API key from dashboard
- [ ] Verify sender email in SendGrid
- [ ] Configure `.env` file with credentials
- [ ] Run unit tests: `pytest test_email_notifications.py -v`
- [ ] Start server: `python main.py`
- [ ] Check health: `curl http://localhost:8000/health`
- [ ] Test contact form notification (curl command above)
- [ ] Test alert notification with all severities
- [ ] Test custom notification
- [ ] Verify emails arrive in inbox
- [ ] Check email formatting (HTML rendering)
- [ ] Test error handling (missing fields, invalid type)
- [ ] Test retry logic (temporarily use invalid API key)

---

## Production Deployment (Render.com)

### Set Environment Variables

In Render dashboard:

1. Go to your service → Environment
2. Add these variables:
   - `SENDGRID_API_KEY`: Your SendGrid API key
   - `SENDGRID_FROM_EMAIL`: noreply@projectlavos.com
   - `SENDGRID_FROM_NAME`: Project Lavos
   - `NOTIFICATION_RECIPIENTS`: matthewdscott7@gmail.com

3. Save and redeploy

### Verify Production

```bash
curl https://projectlavos-backend.onrender.com/health
```

Should show:
```json
{
  "features": {
    "email_notifications": "enabled"
  }
}
```

### Monitor Logs

Watch for email send confirmations:
```
INFO: Email sent successfully: 202
INFO: Contact form notification email sent successfully
```

Or errors:
```
WARNING: Email notification failed: SendGrid not configured
ERROR: SendGrid API error: Unauthorized
```

---

## Files Created

- `email_templates.py` - HTML email templates (contact form, alerts, custom)
- `email_service.py` - SendGrid integration with retry logic
- `test_email_notifications.py` - Comprehensive test suite (20+ tests)
- `EMAIL_NOTIFICATIONS_GUIDE.md` - This file (setup & usage docs)
- `.env.example` - Updated with email configuration

---

## Architecture

```
FastAPI Endpoint (/api/notify)
        ↓
  Email Service (email_service.py)
        ↓
  Email Templates (email_templates.py)
        ↓
  SendGrid API (with retry logic)
        ↓
  Recipient Inbox
```

**Features**:
- **Retry Logic**: 3 attempts with exponential backoff (tenacity library)
- **Error Handling**: Graceful degradation (contact form still works if email fails)
- **Template System**: Reusable HTML templates with inline CSS
- **Multiple Notification Types**: Contact forms, alerts (4 severities), custom
- **Recipient Override**: Default recipients or custom per request
- **Health Monitoring**: `/health` endpoint shows email service status

---

## Troubleshooting

### Emails not sending

1. Check API key is set: `echo $SENDGRID_API_KEY`
2. Verify sender email in SendGrid dashboard
3. Check logs for errors: Look for "SendGrid API error"
4. Test API key with curl:
   ```bash
   curl -X POST https://api.sendgrid.com/v3/mail/send \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"personalizations":[{"to":[{"email":"test@example.com"}]}],"from":{"email":"noreply@projectlavos.com"},"subject":"Test","content":[{"type":"text/plain","value":"test"}]}'
   ```

### Emails in spam folder

- Verify domain with SPF/DKIM records in SendGrid
- Use SendGrid's domain authentication (not single sender verification)
- Avoid spam trigger words in subject/body

### Rate limiting

- SendGrid free tier: 100 emails/day
- If you hit limits, upgrade plan or reduce notification frequency

---

## Next Steps

1. **Webhook Integration**: Add SendGrid webhooks to track delivery/opens/clicks
2. **Email Queue**: Implement queue for high-volume notifications (Celery + Redis)
3. **Template Customization**: Add more templates (weekly reports, performance alerts)
4. **A/B Testing**: Test different subject lines and content for engagement
5. **Unsubscribe Management**: Add preference center for email types

---

**Feature Status**: ✅ Production Ready (v1.5.0)

For questions: matthewdscott7@gmail.com
