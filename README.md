# LicensePlateGame

Track license plates you've seen from the U.S., Canada, and Mexico with this Flask-based web application. Designed to run on a Raspberry Pi and accessible securely from anywhere via Cloudflare Tunnel.

---

## 🔧 Features

* User authentication (signup, login, password reset)
* Leaderboard for U.S. states
* Admin panel for user approval and state management
* User dashboard for marking seen plates
* Feedback system

---

## 🖥️ Local Development Setup (Mac or Raspberry Pi)

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR_USERNAME/LicensePlateGame.git
cd LicensePlateGame
```

### 2. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file (or `LicensePlateGame.env`) in the root folder:

```env
MAIL_USERNAME=<Mail User to Send Mail>
MAIL_PASSWORD=<Mail User password or app key>
MAIL_DEFAULT_SENDER=<Default Sender - often same as MAIL_USERNAME>
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///licenseplategame.db
```

Update `app.py` to load this file:

```python
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "LicensePlateGame.env"))
```

---

## 🐍 Database Setup (SQLite with SQLAlchemy)

1. Ensure `DATABASE_URL` is set to a SQLite file, e.g.:

```env
DATABASE_URL=sqlite:///licenseplategame.db
```

2. From the root directory and virtual environment activated, initialize the database using Python:

```python
from app import db

db.create_all()
```

3. This will create `licenseplategame.db` in your project directory with the necessary tables as defined in your SQLAlchemy models.

> Tip: You can wrap this in a script called `init_db.py` to make it easier:

```python
# init_db.py
from app import db

db.create_all()
print("Database initialized.")
```

Run it with:

```bash
python init_db.py
```

---

## 🐧 Raspberry Pi Setup (OS & App)

1. **Install Raspberry Pi OS Lite**
   Flash using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)

2. **Enable SSH and Wi-Fi** (create `ssh` and `wpa_supplicant.conf` in boot partition)

3. **Install required packages:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

4. **Deploy the app:**

```bash
git clone https://github.com/YOUR_USERNAME/LicensePlateGame.git
cd LicensePlateGame
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Set up `.env` file** and initialize the database as above.

---

## 🔁 Auto-Start on Reboot

Create `licenseplate.service` file:

```ini
[Unit]
Description=License Plate Game Flask App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/LicensePlateGame
Environment="FLASK_APP=app.py"
Environment="FLASK_ENV=production"
EnvironmentFile=/home/pi/LicensePlateGame/LicensePlateGame.env
ExecStart=/home/pi/LicensePlateGame/venv/bin/gunicorn -b localhost:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Install and enable:

```bash
sudo cp licenseplate.service /etc/systemd/system/
sudo systemctl enable licenseplate
sudo systemctl start licenseplate
```

---

## 🌐 Cloudflare Tunnel Setup

1. **Install `cloudflared`:**

```bash
sudo apt install cloudflared
```

2. **Authenticate:**

```bash
cloudflared tunnel login
```

3. **Create and configure tunnel:**

```bash
cloudflared tunnel create licenseplate
```

4. **Create config file at `/etc/cloudflared/config.yml`:**

```yaml
tunnel: licenseplate
credentials-file: /home/pi/.cloudflared/licenseplate.json

ingress:
  - hostname: licenseplate.mreetz.com
    service: http://localhost:8000
  - service: http_status:404
```

5. **Start and enable the tunnel:**

```bash
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

---

## ✅ Final Checklist

* [ ] Flask app runs with `.env` secrets
* [ ] SQLite database initialized with SQLAlchemy
* [ ] App auto-starts on reboot
* [ ] Publicly accessible at `https://licenseplate.mreetz.com`

---

## 📄 License

MIT License. See `LICENSE` file for details.
