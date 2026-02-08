# Permanent Cloudflare Tunnel Setup Guide

## Step 1: Create Cloudflare Account
1. Go to https://dash.cloudflare.com/sign-up
2. Sign up (free)
3. Verify email

## Step 2: Create a Tunnel
1. In Cloudflare dashboard, go to "Zero Trust"
2. Navigate to "Networks" > "Tunnels"
3. Click "Create a tunnel"
4. Name it: "agora-dao-agent"
5. Click "Save tunnel"

## Step 3: Get Your Tunnel Token
After creating, you'll see a command like:
```
cloudflared tunnel run --token <YOUR-TOKEN-HERE>
```

**COPY THAT TOKEN!** It looks like:
`eyJhIjoiMTIzNC...` (long string)

## Step 4: Configure the Tunnel
In Cloudflare dashboard:
1. Go to "Public Hostname"
2. Click "Add a public hostname"
3. Configure:
   - Subdomain: `agora` (or whatever you want)
   - Domain: Choose from dropdown (Cloudflare gives you a free one like `xyz.trycloudflare.com` OR use your own domain)
   - Type: `HTTP`
   - URL: `localhost:80`
4. Save

## Step 5: Give Me the Token
Send me the tunnel token and I'll:
1. Stop the temporary tunnel
2. Start the permanent one
3. Your site will have a stable URL forever!

---

## Alternative: Use Your Own Domain

If you buy a domain (e.g., `agora-dao.com`):
1. Add domain to Cloudflare (free)
2. Update nameservers at your domain registrar
3. Use tunnel with your custom domain
4. Result: `https://agora-dao.com` or `https://app.agora-dao.com`

---

**RECOMMENDED:** Option 1 (permanent tunnel with free Cloudflare domain)
- Takes 5 minutes
- Completely free
- Professional URL
- Auto SSL/HTTPS
- No domain purchase needed
