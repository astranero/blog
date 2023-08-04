import sqlite3
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers check_password, make_password

class CustomUserManager(BaseUserManager):
    def get_by_natural_key(self, username):
        return self.get(username=username)

    def create_superuser(self, username, password=None,  **kwargs):
        # Create a new user with the given email and password
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(username, password, **kwargs)

    def create_user(self, username, password, **kwargs):
        if not username:
            raise ValueError("The Username field must be set.")
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        hashed_password = make_password(password)
        try:
            cursor.execute("""INSERT INTO app_customuser (username, password, is_staff, is_superuser) VALUES (?, ?, ?, ?);""",
            (username, hashed_password, kwargs.get("is_staff", False), kwargs.get("is_superuser", False)))
            conn.commit()
            id = cursor.execute("""SELECT id FROM app_customuser WHERE username = ?""", (username,)).fetchone()[0]
            user = self.model(id=id, username=username, password=password, is_staff=kwargs.get("is_staff", False), is_superuser=kwargs.get("is_superuser", False))
        except Exception as exc:
            user = None
        conn.close()
        return user

class CustomUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def check_password(self, raw_password):
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("""SELECT password FROM app_customuser WHERE username = ?""",
                    (self.username,))
        password = cursor.fetchone()
        conn.close()
        if password is not None:
            password = password[0]
            return check_password(raw_password, password)
        return False

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app):
        return True

class Post(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
