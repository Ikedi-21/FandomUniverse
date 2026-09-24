## PROJECT DOCUMENTATION
# Introduction


# Project Specifications
-- Frontend
- HTML5 / CSS3 / Vanilla JS

-- Backend
- Django Monolith

-- Database
- db.sqlite3 (We are going with this for easy start up - It's bad practice to use db.sqlite for a production website, we were initially going to use Postgresql and containerize using docker, but to easily run the application without having alot of other softwares)

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
-- Application 1 --
- name: core
- features: 

- Landing pages
- Login page
- Authentication Page