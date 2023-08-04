import sqlite3
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class CustomAuthentication(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM app_customuser WHERE username = '{ username }' ")
        user = cursor.fetchone()
        conn.close()
        if user is not None:
            user = CustomUser(id=user[0], username=user[1], password=user[2], is_staff=user[3], is_superuser=user[4])
            if user.check_password(password):
                return user

        return None

    def get_user(self, username):
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM app_customuser WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user is not None:
            return CustomUser(id=user[0], username=user[1], password=user[2], is_staff=user[3], is_superuser=user[4])
        return None
