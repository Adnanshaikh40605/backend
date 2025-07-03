# PostgreSQL Setup Guide

This guide will help you set up PostgreSQL for local development.

## Prerequisites

1. Install PostgreSQL on your system:
   - [Download PostgreSQL](https://www.postgresql.org/download/)
   - During installation, note down the password you set for the 'postgres' user

## Setup Options

### Option 1: Automatic Setup (Recommended)

Run the provided setup script:

```bash
python setup_postgres.py
```

This script will:
1. Check if PostgreSQL is installed
2. Create the 'railway' database if it doesn't exist
3. Update your .env file to use the local PostgreSQL instance

### Option 2: Manual Setup

1. Create a database named 'railway':

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside the PostgreSQL prompt, create the database
CREATE DATABASE railway;

# Exit PostgreSQL
\q
```

2. Update your .env file:
   - Comment out the remote DATABASE_URL line
   - Uncomment the local DATABASE_URL line

```
# Remote PostgreSQL connection
# DATABASE_URL=postgresql://postgres:tjivRKybjCRWGgWiVAxNpASgEmhzASyi@switchyard.proxy.rlwy.net:57528/railway
# Local PostgreSQL connection
DATABASE_URL=postgresql://postgres:tjivRKybjCRWGgWiVAxNpASgEmhzASyi@localhost:5432/railway
```

## Apply Migrations

After setting up the database, run migrations to create the database schema:

```bash
python manage.py migrate
```

## Create a Superuser

Create an admin user to access the Django admin interface:

```bash
python manage.py createsuperuser
```

## Run the Server

Start the development server:

```bash
python manage.py runserver
```

## Switching Between Remote and Local Database

To switch between remote and local database:

1. Edit your .env file
2. Comment/uncomment the appropriate DATABASE_URL line
3. Restart your Django server

## Connection Details

### Local PostgreSQL
- Host: localhost
- Port: 5432
- Database: railway
- Username: postgres
- Password: tjivRKybjCRWGgWiVAxNpASgEmhzASyi

### Remote PostgreSQL
- Host: switchyard.proxy.rlwy.net
- Port: 57528
- Database: railway
- Username: postgres
- Password: tjivRKybjCRWGgWiVAxNpASgEmhzASyi 