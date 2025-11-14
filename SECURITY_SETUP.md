# Security Setup Guide

This guide explains how to secure your webhook relay system so only authorized sources can send webhooks.

## Current Security Status

🔴 **INSECURE**: Your webhook endpoint is currently **open to anyone**

Any person who knows your URL (`https://web-production-3d53a.up.railway.app/webhook`) can send webhooks to your system.

---

## Security Measures

### 1. GitHub Webhook Signature Verification (REQUIRED for Production)

**What it does:** Cryptographically verifies that webhooks actually come from GitHub using HMAC-SHA256.

**Status:** ✅ Code implemented, ⚠️ Not enabled

#### Step-by-Step Setup

**Step 1: Generate a Secure Secret**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `SScoyCYKRtMSxoKtRGlB89esA_yzASl-6wuvEfwNYW4`

**Step 2: Set Secret in Railway**

1. Go to Railway dashboard: https://railway.app/project/[your-project]
2. Click on your **web** service
3. Click the **Variables** tab
4. Click **+ New Variable**
5. Add:
   - **Variable:** `GITHUB_WEBHOOK_SECRET`
   - **Value:** `[paste your generated secret]`
6. Click **Add** - Railway will automatically redeploy

**Step 3: Update GitHub Webhook Settings**

1. Go to: https://github.com/tim-gameplan/ai-webhook/settings/hooks
2. Click **Edit** on your existing webhook
3. Scroll to **Secret** field
4. Paste the **same secret** you used in Railway
5. Click **Update webhook**

**Step 4: Test It**

```bash
# This should now FAIL (no signature)
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "unauthorized"}'

# Response: {"error": "Invalid webhook signature"}
```

✅ **Your webhook is now secure!** Only GitHub can send valid webhooks.

---

### 2. API Key for Custom Webhooks (OPTIONAL)

**What it does:** Allows you to send custom webhooks (non-GitHub) securely using an API key.

**When to use:** If you want to send webhooks from your own applications, AI systems, or other services.

#### Setup

**Step 1: Generate an API Key**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `9K7mPxQnVzL4cRtB3wYpH8dGfN6jKlMa5sXvC2eA1qW`

**Step 2: Set API Key in Railway**

1. Railway dashboard → Variables tab
2. Add new variable:
   - **Variable:** `API_KEY`
   - **Value:** `[paste your generated API key]`

**Step 3: Use API Key in Your Applications**

**Option A: Using Authorization Header**
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 9K7mPxQnVzL4cRtB3wYpH8dGfN6jKlMa5sXvC2eA1qW" \
  -d '{
    "event": "custom_event",
    "data": {"key": "value"}
  }'
```

**Option B: Using X-API-Key Header**
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 9K7mPxQnVzL4cRtB3wYpH8dGfN6jKlMa5sXvC2eA1qW" \
  -d '{
    "event": "custom_event",
    "data": {"key": "value"}
  }'
```

**From Python:**
```python
import requests

webhook_url = "https://web-production-3d53a.up.railway.app/webhook"
api_key = "9K7mPxQnVzL4cRtB3wYpH8dGfN6jKlMa5sXvC2eA1qW"

response = requests.post(
    webhook_url,
    json={"event": "my_event", "data": {"key": "value"}},
    headers={"Authorization": f"Bearer {api_key}"}
)
print(response.status_code)  # Should be 200
```

---

## How It Works

### GitHub Webhooks (HMAC-SHA256 Signature)

1. **You create a secret** and give it to both GitHub and your server
2. **GitHub creates a signature** by hashing the webhook payload with your secret
3. **GitHub sends the webhook** with the signature in the `X-Hub-Signature-256` header
4. **Your server recalculates** the expected signature using the same secret
5. **Comparison:** If signatures match → webhook is authentic ✅
6. **If signatures don't match** → webhook is rejected ❌

```
┌─────────┐                                    ┌──────────────┐
│ GitHub  │──── Webhook + Signature ──────────>│ Your Server  │
└─────────┘     (signed with secret)           └──────────────┘
                                                       │
                                                       ├─> Verify signature
                                                       │   using same secret
                                                       │
                                                       ├─> Match? ✅ Accept
                                                       └─> No match? ❌ Reject
```

### Custom Webhooks (API Key)

1. **You generate an API key** and store it in Railway
2. **Your application includes the API key** in the request header
3. **Your server checks** if the provided key matches the stored key
4. **Match?** → Accept ✅ | **No match?** → Reject ❌

---

## Security Best Practices

### ✅ DO
- ✅ Always set `GITHUB_WEBHOOK_SECRET` in production
- ✅ Use long, random secrets (32+ characters)
- ✅ Keep secrets in environment variables, never in code
- ✅ Use different secrets for development and production
- ✅ Rotate secrets periodically (every 90 days)
- ✅ Use HTTPS for all webhook endpoints (Railway provides this)
- ✅ Monitor webhook logs for suspicious activity

### ❌ DON'T
- ❌ Commit secrets to Git
- ❌ Share secrets in Slack, email, or other insecure channels
- ❌ Use the same secret across multiple projects
- ❌ Use predictable secrets like "password123"
- ❌ Disable signature verification in production

---

## Verification Status

**Check Current Status:**

Visit: https://web-production-3d53a.up.railway.app/

The response includes server information. Check the Railway logs (Dashboard → Deployments → View logs) for security warnings:

- ⚠️ `WARNING: GITHUB_WEBHOOK_SECRET not set` → Signature verification **DISABLED**
- ✅ No warning → Signature verification **ENABLED**

---

## Troubleshooting

### "Invalid webhook signature" error

**GitHub webhooks failing:**
1. Check that the secret in Railway **exactly matches** the secret in GitHub
2. Verify no extra spaces or characters
3. Check Railway logs for the actual error message

**Custom webhooks failing:**
1. Check that `X-Hub-Signature-256` header is NOT set (this triggers GitHub validation)
2. Ensure API key is in `Authorization: Bearer [key]` or `X-API-Key: [key]` header
3. Verify the API key matches the one in Railway environment variables

### Webhooks still work without signature

This means `GITHUB_WEBHOOK_SECRET` is not set in Railway. Follow Step 2 above to set it.

---

## Testing Security

### Test 1: Unauthorized Request (Should Fail)
```bash
# No API key, no signature - should be REJECTED
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "unauthorized"}'

# Expected: 401 or 403 error
```

### Test 2: With Valid API Key (Should Succeed)
```bash
# With API key - should be ACCEPTED
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: [your-api-key]" \
  -d '{"event": "test", "data": "authorized"}'

# Expected: 200 OK
```

### Test 3: GitHub Webhook from Dashboard (Should Succeed)
1. Go to GitHub webhook settings
2. Click "Recent Deliveries"
3. Click "Redeliver" on any webhook
4. Should succeed with 200 OK

---

## Additional Security Layers (Future)

These are not yet implemented but planned:

- **Rate limiting** - Prevent webhook spam
- **IP allowlisting** - Only accept from GitHub's IP ranges
- **WebSocket authentication** - Require token for client connections
- **Webhook payload validation** - Validate structure and content
- **Audit logging** - Log all webhook attempts for security review

See `FUTURE_TASKS.md` for the full roadmap.

---

## Questions?

- Check server logs in Railway dashboard for detailed error messages
- Review `app.py:36-83` for verification code
- Test with `curl` commands above

**Remember:** Security is not optional for production systems!

---

*Last updated: 2025-11-14*
