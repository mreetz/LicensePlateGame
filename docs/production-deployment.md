# Production Deployment

This guide documents running LicensePlateGame in production using Gunicorn and systemd.

## Production Architecture

    Cloudflare Tunnel
        ↓
    http://localhost:5000
        ↓
    Gunicorn
        ↓
    Flask Application

## Install Gunicorn

Activate the virtual environment:

    cd /home/mreetz/LicensePlateGame
    source venv/bin/activate

Install Gunicorn:

    pip install gunicorn

## Manual Gunicorn Test

Run:

    gunicorn --bind 127.0.0.1:5000 app:app

Test:

    curl http://127.0.0.1:5000

Stop with Ctrl+C.

## systemd Service

Create service file:

    sudo vi /etc/systemd/system/licenseplate.service

Example service:

    [Unit]
    Description=License Plate Game Flask App
    After=network.target

    [Service]
    User=mreetz
    Group=mreetz
    WorkingDirectory=/home/mreetz/LicensePlateGame
    Environment="PATH=/home/mreetz/LicensePlateGame/venv/bin"
    ExecStart=/home/mreetz/LicensePlateGame/venv/bin/gunicorn \
        --workers 3 \
        --bind 127.0.0.1:5000 \
        app:app

    Restart=always

    [Install]
    WantedBy=multi-user.target

Reload systemd:

    sudo systemctl daemon-reload

Enable service:

    sudo systemctl enable licenseplate

Start service:

    sudo systemctl start licenseplate

Check status:

    sudo systemctl status licenseplate

View logs:

    journalctl -u licenseplate -f

## Restart After Code Changes

After pulling new code:

    sudo systemctl restart licenseplate

## Common Issues

### App Will Not Start

Check logs:

    journalctl -u licenseplate -f

### Port Already In Use

    sudo lsof -i :5000

### Wrong Python Environment

Verify service uses:

    /home/mreetz/LicensePlateGame/venv/bin/gunicorn

