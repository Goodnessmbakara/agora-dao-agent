#!/bin/bash
# Setup script for permanent Cloudflare Tunnel
# Run this after getting tunnel token from Cloudflare

echo "🌐 Agora Permanent Tunnel Setup"
echo "================================"
echo ""

# Check if token provided
if [ -z "$1" ]; then
    echo "❌ ERROR: No tunnel token provided!"
    echo ""
    echo "Usage: ./setup-permanent-tunnel.sh <CLOUDFLARE_TUNNEL_TOKEN>"
    echo ""
    echo "Get your token from:"
    echo "1. Go to https://dash.cloudflare.com"
    echo "2. Zero Trust > Networks > Tunnels"
    echo "3. Create tunnel > Copy the token"
    exit 1
fi

TUNNEL_TOKEN="$1"

echo "✅ Token received"
echo ""

# Stop temporary tunnel
echo "🛑 Stopping temporary tunnel..."
pkill -f "cloudflared.*--url" || echo "   No temporary tunnel running"

# Stop old permanent tunnel (if any)
pkill -f "cloudflared.*run" || echo "   No old permanent tunnel"

sleep 2

# Start permanent tunnel as service
echo "🚀 Starting permanent tunnel..."
nohup cloudflared tunnel run --token "$TUNNEL_TOKEN" > /tmp/cloudflare-tunnel.log 2>&1 &

sleep 3

# Check if running
if pgrep -f "cloudflared.*run" > /dev/null; then
    echo "✅ Permanent tunnel is LIVE!"
    echo ""
    echo "📊 Status:"
    ps aux | grep cloudflared | grep -v grep
    echo ""
    echo "📋 Logs: tail -f /tmp/cloudflare-tunnel.log"
    echo ""
    echo "🌐 Your site is now permanently accessible!"
    echo "   Check Cloudflare dashboard for your URL"
else
    echo "❌ Failed to start tunnel"
    echo "Check logs: cat /tmp/cloudflare-tunnel.log"
    exit 1
fi

# Make it auto-start on reboot
echo ""
echo "💡 To make tunnel start on boot:"
echo "   1. sudo nano /etc/systemd/system/cloudflare-tunnel.service"
echo "   2. Paste this:"
cat << EOF

[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=$(whoami)
ExecStart=/usr/local/bin/cloudflared tunnel run --token $TUNNEL_TOKEN
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "   3. sudo systemctl enable cloudflare-tunnel"
echo "   4. sudo systemctl start cloudflare-tunnel"
