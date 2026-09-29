## PROJECT DOCUMENTATION
# Introduction


# Project Specifications
-- Frontend
- HTML5 / CSS3 / Vanilla JS
- reason: For simplicity we use HTML for our frontend

-- Backend
- Django Monolith
- reason: Django comes with a lot out of the box, reducing our work significantly, when using HTML for the frontend djanogo provides a lot of security against attacks like Cross-Site Request Forgery (CSRF), Cross-Site Scripting (XSS), Sql Injections (Most effective when using Django forms).

-- Database
- MySQL - Django's default database for development is db.sqlite and it's not recommendedd for production, and accourding to the SRS, we have an option to use MySQL for database, so we are going with MySQL for our database, our MySQL database provider is AIVEN (https://aiven.io), they have a 1 GB storage, 1 GB RAM, single node with backups included, free hosted MySQL so we didn't have to install locally (https://aiven.io/mysql), 


# Local setup

Run these commands in PowerShell from the project root:

    py -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    Copy-Item .env.example .env

The supplied .env.example uses SQLite for local setup. For MySQL, install the dependencies from requirements.txt, set DB_ENGINE=mysql and the DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, and DB_SSL_CA variables in .env. DB_SSL_CA must point to the provider CA certificate file; keep both .env and the certificate private. The current Aiven connection could not be verified because the configured CA chain was rejected, so SQLite is the verified local configuration.

After setting .env, initialize and run the project:

    python manage.py migrate
    python manage.py seed_demo
    python manage.py runserver
    python manage.py test
    python scripts/smoke.py

The seed command prints the demo account passwords. Email verification and password-reset messages use Django's console email backend unless SMTP credentials are configured in .env.

# Core Applications
---
Application 1 
---
- name: core
- features: 

- Landing pages
- Login page
- Authentication Page

- description: this is the landing app or the starting point of our web flow, from here users can sign in or register and also have an overview of FandomUniverse

---
Application 2
---
- name: aricle
- description: User and admin articles are handled here

---
Application 3
---
- name: chatbot
- description: This contains all of the views and functions we used for our chatbot faq

---
Application 4
---
- name: characters
- decription: This handles everything related to characters feature including the views and the models

---
Application 5
---
- name: dashboard
- description: This is where our dashboard logic goes

---
Application 6
---
- name: engagements

---
Application 7
---
- name: media_centre

---
Application 8
---
- name: merch

---
Application 9
---
- name: events

---
Application 10
---
- name: accounts
- description: Our core Accounts logic is handled here

---
Application 11
---
- name: catalog