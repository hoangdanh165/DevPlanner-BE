import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
from random import choice

# import pytz
import uuid


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.contrib.auth import get_user_model
from user.models.role import Role
from django.db import transaction
from django.db.models import F
from faker import Faker


fake = Faker()
User = get_user_model()


def create_roles():
    roles = [
        {"name": "admin", "permissions": {}},
        {"name": "user", "permissions": {}},
    ]
    for role_data in roles:
        Role.objects.create(**role_data)


def create_users():
    emails = [
        "hoangdanh.165@gmail.com",
    ]

    emails_user = [
        "user_1@gmail.com",
    ]

    admin_role = Role.objects.filter(name="admin").first()
    user_role = Role.objects.filter(name="user").first()

    for email in emails:
        admin_user = User.objects.create_user(
            full_name="ADMINISTRATOR",
            email=email,
            password="12345678",
            is_staff=True,
            is_superuser=True,
            role=admin_role,
        )
        admin_user.save()
        print(f"Created admin user: {email}")

    for email in emails_user:
        customer_user = User.objects.create_user(
            email=email,
            full_name=fake.name(),
            phone=fake.phone_number(),
            address=fake.address(),
            avatar="https://example.com/avatar.jpg",
            password="12345678",
            is_staff=False,
            is_superuser=False,
            role=user_role,
        )
        customer_user.save()
        print(f"Created customer user: {email}")


if __name__ == "__main__":
    create_roles()
    create_users()

    print("Fake data created successfully!")
