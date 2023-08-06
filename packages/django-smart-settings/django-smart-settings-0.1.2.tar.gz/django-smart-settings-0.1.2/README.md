django-smart-settings
=====================

How to install

pip install django-smart-settings

How to use

Create your Django project
Create directory settings next to settings.py file
Move settings.py to settings/ and rename it to default.py
Create settings/__init__.py
Add in this file:
import django_smart_settings

django_smart_settings.configure(locals())