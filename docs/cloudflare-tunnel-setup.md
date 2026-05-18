# Cloudflare Tunnel Setup

This guide documents how LicensePlateGame can be exposed publicly using Cloudflare Tunnel without opening inbound firewall ports.

## Architecture

    Internet
        ↓
    Cloudflare
        ↓
    Cloudflare Tunnel
        ↓
    Raspberry Pi localhost service
        ↓
    Gunicorn / Flask

## Install cloudflared

Follow Cloudflare's current installation instructions for Raspberry Pi OS.

Verify installation:

    cloudflared --version

## Authenticate

Login to Cloudflare:

    cloudflared tunnel login

This opens a browser-based login flow.

## Create Tunnel

Create a tunnel:

    cloudflared tunnel create licenseplate

List tunnels:

    cloudflared tunnel list

## Configure Tunnel

Example config location:

    /home/mreetz/.cloudflared/config.yml

Example config:

    tunnel: YOUR_TUNNEL_ID
    credentials-file: /home/mreetz/.cloudflared/YOUR_TUNNEL_ID.json

    ingress:
      - hostname: licenseplate.example.com
        service: http://localhost:5000
      - service: http_status:404

## DNS Route

Create DNS route:

    cloudflared tunnel route dns licenseplate licenseplate.example.com

## Run Tunnel Manually

    cloudflared tunnel run licenseplate

## Install as a Service

Install service:

    sudo cloudflared service install

Enable and start:

    sudo systemctl enable cloudflared
    sudo systemctl start cloudflared

Check status:

    sudo systemctl status cloudflared

View logs:

    journalctl -u cloudflared -f

## Troubleshooting

### Tunnel Has No Active Connection

Check service status:

    sudo systemctl status cloudflared

Restart service:

    sudo systemctl restart cloudflared

### Error 1033

This usually means Cloudflare cannot reach the tunnel.

Check:

- cloudflared service is running
- config.yml points to the correct tunnel
- hostname route exists
- Flask/Gunicorn is listening on localhost:5000

