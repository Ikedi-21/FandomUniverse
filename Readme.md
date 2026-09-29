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


# Major Steps
-- Create a virtual environment (We use this store project requiremenst specifically for this project, so we only have packages required foe this project installed)

-- step --
py -m venv .venv 

-- Activate virtual environment (This activates our virtual environment for the current project)

-- step --
- powershell
.venv/Scripts/activate

- command prompt
.venv\Scripts\activate

- git bash
source .venv/Scripts/activate

-- Install Django (We need the open source django framework to work on this project)

-- step --
py -m pip install django

-- Create Django Project --
- We created a django project named FandomUniverse, since we are using django for our project

-- step --
project-name = FandomUniverse
django-admin startproject ${project-name} .

-- Create Django Applications -- 
- We use applications to seperate core features of our project and grouping them neatly

-- step --
python manage.py startapp ${app-name}

-- register app in settings.py --
-- create urls in the app and then include it in the project urls

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

---

## Development Progress & Audit Log

### Phase 1: Templates Audit & Fix
- [x] Create unified master `templates/base.html` with clean layout blocks, responsive sidebar, top navbar, theme initialization, global chatbot drawer, trailer stream modal, and Django message alerts
- [x] Configure `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']` in `FandomUniverse/settings.py`
- [x] Add logout view & URL route (`logout`) to `core` app
- [x] Add route aliases (`dashboard`, `admin-overview`, `admin-submissions-queue`, etc.) in `dashboard/urls.py` and `bookmark-list` in `engagements/urls.py`
- [x] Audit and refactor `core/templates/index.html` to extend `base.html`:
  - Replaced hardcoded `/static/...` assets with `{% static %}` tags
  - Replaced broken URLs (`articles` -> `content-detail`, `characters-list` -> `character-detail`, `merch-details` -> `merch-detail`)
  - Validated clean closure for all loops (`{% for %}` ... `{% empty %}` ... `{% endfor %}`)
- [x] Refactor Catalog app templates (`explore.html`, `content-detail.html`, `submit-content.html`):
  - Extracted shared frame into master `base.html`
  - Replaced hardcoded routes (`/characters/`, `href="/"`, etc.) with `{% url %}` tags
  - Fixed unclosed script in `content-detail.html` and integrated dynamic star rating & bookmark handlers
  - Configured sticky filter sidebar in `explore.html` with clean responsive layout
- [ ] Refactor Characters app templates (`character-list.html`, `character-detail.html`) and clean up prototype collisions
- [ ] Refactor Merch app templates (`merch-list.html`, `merch-detail.html`)
- [ ] Refactor Events app templates (`event-list.html`, `event-detail.html`)
- [ ] Refactor Dashboard app templates (`dashboard.html`, `admin-overview.html`, etc.)
- [ ] Refactor Engagements app templates (`feedback.html`, `bookmark-list.html`)
- [ ] Refactor Accounts & Core Auth templates (`login.html`, `register.html`, email verification)
- [ ] Refactor Article app templates

**Status**: In Progress - Next inspecting & refactoring Characters app templates.


