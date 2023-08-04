import sqlite3
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, PostForm
from .models import CustomUser, Post

@login_required()
def home_view(request):
    """This is a view that leads to home template

    Returns:
        render: login.html 
        redirect: home.html
    """
    posts = Post.objects.all()
    return render(request, "home.html", {"posts": posts})

@csrf_exempt
def login_view(request):
    """This leads to login template, for user authentication

    Returns:
        render: login.html if there's error of somekind then a message
        redirect: If login successful then redirection to home.html
    """
    if request.method == "GET":
        form = UserLoginForm(request.GET)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Form is not valid. Please check the fields and try again.")
    form = UserLoginForm()
    return render(request, "login.html", {"form": form})

@csrf_exempt
def logout_view(request):
    logout(request)
    return render(request, "logout.html")

@csrf_exempt
def create_view(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("home")
    else:
        form = PostForm()
    return render(request, "create.html", {"form": form})

@csrf_exempt
@login_required()
def delete_view(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden()
    else:
        post.delete()
    return redirect("home")

@csrf_exempt
@login_required()
def edit_view(request, post_id): 
    post = Post.objects.get(id=post_id)
    if request.user != post.user:
       return HttpResponseForbidden()
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = PostForm(instance=post)
    return render(request, "edit.html", {"form":form})

def search_view(request):
    query = request.GET.get("query", "")
    print(f"{query}")
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM app_post WHERE title LIKE '%{query}%'")
    posts = cursor.fetchall()
    conn.close()
    columns = [column[0] for column in cursor.description]
    posts = [dict(zip(columns, row)) for row in posts]
    posts = [Post(**post_dict) for post_dict in posts]
    return render(request, 'home.html', {'posts': posts})

@csrf_exempt
def register_view(request):
    # In registration saving password as plain text is bad practice.
    if request.method == "GET":
        form = UserRegisterForm(request.GET)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            try:
                CustomUser.objects.create_user(username, password)
                return redirect("login")
            except ValueError as error:
                form.add_error(None, f"{error}")
        else:
            form.add_error(None, "Form is invalid!")
            form = UserRegisterForm()
    print(form.errors)
    return render(request, "register.html", {"form": form})
