# Troubleshooting

Common operational issues for LicensePlateGame.

## Service Status

Check application service:

    sudo systemctl status licenseplate

Follow logs:

    journalctl -u licenseplate -f

## Cloudflare Tunnel Status

Check tunnel service:

    sudo systemctl status cloudflared

Follow logs:

    journalctl -u cloudflared -f

Restart tunnel:

    sudo systemctl restart cloudflared

## App Not Loading Publicly

Check local app first:

    curl http://127.0.0.1:5000

If local app works, check Cloudflare Tunnel.

If local app does not work, check Gunicorn/systemd logs.

## Port Conflict

Check port 5000:

    sudo lsof -i :5000

## Environment Variables

Confirm `.env` exists:

    ls -la .env

Verify required values:

- SECRET_KEY
- DATABASE_URL
- MAIL_USERNAME
- MAIL_PASSWORD

Do not print secrets into shared logs or screenshots.

## Email Problems

For Gmail SMTP:

- Use an App Password
- Do not use the normal Gmail password
- Confirm MAIL_USERNAME is correct
- Confirm MAIL_PASSWORD has no spaces
- Confirm TLS and port 587 are configured

## Database Problems

If using SQLite, confirm the app can write to the database file.

If using MariaDB, confirm network connectivity and credentials.

## Git Branch Confusion

Show current branch:

    git branch --show-current

Show status:

    git status

Show remotes:

    git branch -r

Set upstream for a branch:

    git push -u origin branch-name

