# Raspberry Pi Setup

This guide documents the base Raspberry Pi setup for running LicensePlateGame.

## Recommended Hardware

- Raspberry Pi 4 or newer
- 4 GB RAM or greater recommended
- Reliable power supply
- MicroSD card or SSD storage
- Network connection

## Operating System

Recommended:

- Raspberry Pi OS Bookworm or newer

Check OS version:

    cat /etc/os-release

Update system packages:

    sudo apt update
    sudo apt upgrade

Install common dependencies:

    sudo apt install git python3 python3-venv python3-pip vim curl lsof

## Application Directory

Recommended location:

    /home/mreetz/LicensePlateGame

Clone the repository:

    git clone https://github.com/YOUR_GITHUB_USERNAME/LicensePlateGame.git
    cd LicensePlateGame

## Python Virtual Environment

Create virtual environment:

    python3 -m venv venv

Activate it:

    source venv/bin/activate

Install dependencies:

    pip install --upgrade pip
    pip install -r requirements.txt

## Environment Configuration

Copy the example environment file:

    cp .env.example .env

Edit the real environment file:

    vi .env

Never commit `.env` to Git.

## Local Test

Run the app locally:

    python app.py

Test locally:

    curl http://127.0.0.1:5000

