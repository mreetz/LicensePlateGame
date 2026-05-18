# Deployment Workflow

This document describes the normal development and deployment workflow for LicensePlateGame.

## Source of Truth

The active deployed repository is on the Raspberry Pi:

    /home/mreetz/LicensePlateGame

Development can be done remotely using VS Code connected to the Raspberry Pi.

## Branching

Create feature branches from main:

    git checkout main
    git pull
    git checkout -b feature/my-feature

## Commit Changes

Check changes:

    git status

Stage files:

    git add .

Commit:

    git commit -m "Describe the change"

Push branch:

    git push -u origin feature/my-feature

## Pull Request

Open a pull request in GitHub.

Recommended checks before merging:

- App starts locally
- Login works
- Signup works
- Admin approval works
- User plate save works
- Leaderboard loads
- Mobile browser view is usable
- GitHub Actions pass

## Deploy After Merge

On the Raspberry Pi:

    cd /home/mreetz/LicensePlateGame
    git checkout main
    git pull
    source venv/bin/activate
    pip install -r requirements.txt
    sudo systemctl restart licenseplate

Check service:

    sudo systemctl status licenseplate

Check logs:

    journalctl -u licenseplate -f

