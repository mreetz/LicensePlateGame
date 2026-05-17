# LicensePlateGame

A Raspberry Pi hosted web application for tracking license plates seen across the United States, Canada, and Mexico.

The application provides secure user authentication, administrative approval workflows, leaderboard tracking, password reset functionality, and a mobile-friendly interface optimized for travel and road-trip usage.

---

## Features

### User Features
- User registration and login
- Password reset via email
- Track seen license plates
- Separate tracking for:
  - United States
  - Canadian Provinces
  - Mexican States
- Responsive mobile-friendly interface
- Filter to display unseen plates only
- User leaderboard rankings
- Feedback submission form

### Administrative Features
- User approval workflow
- User management interface
- State/province management
- Administrative dashboard

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python / Flask |
| Database | SQLite or MariaDB |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Email | Flask-Mail |
| Frontend | Bootstrap 4 |
| Production Server | Gunicorn |
| Public Exposure | Cloudflare Tunnel |
| Hosting Platform | Raspberry Pi |

---

## Architecture

    Internet
        ↓
    Cloudflare Tunnel
        ↓
    Gunicorn
        ↓
    Flask Application
        ↓
    SQLite / MariaDB

The application is designed to run securely on a Raspberry Pi without directly exposing inbound ports to the internet.

Cloudflare Tunnel provides encrypted public access while masking the origin server IP address.

---

## Screenshots

Screenshots can be added here later.

Suggested screenshots:
- Login page
- User dashboard
- Plate tracking page
- Leaderboard
- Admin approval panel
- Mobile browser view

---

## Requirements

### Hardware
- Raspberry Pi 4 recommended
- 4GB RAM or greater recommended

### Software
- Raspberry Pi OS Bookworm or newer
- Python 3.11+
- Git
- Cloudflare account
- Gmail account with App Password enabled

---

## Installation

### Clone Repository

    git clone https://github.com/YOUR_GITHUB_USERNAME/LicensePlateGame.git
    cd LicensePlateGame

### Create Python Virtual Environment

    python3 -m venv venv
    source venv/bin/activate

### Install Dependencies

    pip install -r requirements.txt

### Configure Environment Variables

Create a .env file:

    SECRET_KEY=your_secret_key
    MAIL_USERNAME=your_email@gmail.com
    MAIL_PASSWORD=your_gmail_app_password
    DATABASE_URL=sqlite:///license_plate_game.db

---

## Database Initialization

Initialize the database:

    flask db upgrade

If migrations are not being used:

    python init_db.py

---

## Running Locally

    python app.py

Application will be available at:

    http://127.0.0.1:5000

---

## Production Deployment

## Gunicorn

Install Gunicorn:

    pip install gunicorn

Test Gunicorn manually:

    gunicorn --bind 127.0.0.1:5000 app:app

---

## systemd Service

Example service file:

    [Unit]
    Description=License Plate Game Flask App
    After=network.target

    [Service]
    User=mreetz
    Group=mreetz
    WorkingDirectory=/home/mreetz/LicensePlateGame
    Environment="PATH=/home/mreetz/LicensePlateGame/venv/bin"
    ExecStart=/home/mreetz/LicensePlateGame/venv/bin/gunicorn 
        --workers 3 
        --bind 127.0.0.1:5000 
        app:app

    Restart=always

    [Install]
    WantedBy=multi-user.target

Save as:

    /etc/systemd/system/licenseplate.service

Enable and start:

    sudo systemctl daemon-reload
    sudo systemctl enable licenseplate
    sudo systemctl start licenseplate

Check status:

    sudo systemctl status licenseplate

---

## Cloudflare Tunnel

Example ingress configuration:

    tunnel: YOUR_TUNNEL_ID
    credentials-file: /home/mreetz/.cloudflared/YOUR_TUNNEL_ID.json

    ingress:
      - hostname: licenseplate.example.com
        service: http://localhost:5000
      - service: http_status:404

Run tunnel:

    cloudflared tunnel run licenseplate

---

## Security Notes

- Never commit .env files
- Use Gmail App Passwords instead of account passwords
- Use a strong Flask SECRET_KEY
- Cloudflare Tunnel prevents direct inbound exposure
- Administrative approval is required before user access
- HTTPS is provided through Cloudflare

---

## Mobile Support

The application uses Bootstrap responsive layouts and is designed for:
- iPhone browsers
- Android browsers
- Tablet devices
- Desktop browsers

---

## Troubleshooting

### Cloudflare Tunnel Offline

Check tunnel status:

    sudo systemctl status cloudflared

Restart:

    sudo systemctl restart cloudflared

---

### Gunicorn Not Starting

Check logs:

    journalctl -u licenseplate -f

---

### Flask-Mail Authentication Failures

Verify:
- Gmail App Password
- SMTP enabled
- .env configuration

---

### Port Already In Use

Check port usage:

    sudo lsof -i :5000

---

## Development Workflow

### Create Feature Branch

    git checkout -b feature/my-feature

### Commit Changes

    git add .
    git commit -m "Describe changes"

### Push Branch

    git push -u origin feature/my-feature

---

## Future Improvements

Planned enhancements may include:
- Progressive Web App (PWA) support
- OCR license plate recognition
- GPS trip tracking
- REST API support
- Docker deployment
- User statistics dashboard
- Plate photo uploads
- Dark mode support

---

## License

This project is provided for educational and personal use.

---

## Author

Michael W. Reetz
