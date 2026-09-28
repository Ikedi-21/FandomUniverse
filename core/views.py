import re

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from accounts.models import User, Profile, Avatar
from media_centre.models import Rating
from catalog.models import Content, Category
from characters.models import CharacterProfile
from merch.models import Merch
from article.models import FanSubmission, EventHighlight
from django.contrib.auth import authenticate, login as auth_login
from django.db.models import Avg



def register(request):
    categories = Category.objects.all()
    avatars = Avatar.objects.all()


    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        cPassword = request.POST.get("cpassword", "")

        # ==========================================
        # 1. USERNAME FORMAT
        # ==========================================

        if not username:
            messages.error(request, "Username is required.")
            return redirect("register")

        # Username: letters, numbers, underscores only
        if not re.match(r"^[A-Za-z0-9_]+$", username):
            messages.error(
                request,
                "Username can only contain letters, numbers, and underscores."
            )
            return redirect("register")

        # Username length
        if len(username) < 3:
            messages.error(
                request,
                "Username must be at least 3 characters long."
            )
            return redirect("register")

        if len(username) > 20:
            messages.error(
                request,
                "Username cannot be more than 20 characters long."
            )
            return redirect("register")

        # ==========================================
        # 2. USERNAME UNIQUENESS
        # ==========================================

        if User.objects.filter(username__iexact=username).exists():
            messages.error(
                request,
                "That username is already taken. Please choose another."
            )
            return redirect("register")

        # ==========================================
        # 3. EMAIL FORMAT
        # ==========================================

        if not email:
            messages.error(request, "Email address is required.")
            return redirect("register")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(
                request,
                "Please enter a valid email address."
            )
            return redirect("register")

        # ==========================================
        # 4. EMAIL UNIQUENESS
        # ==========================================

        if User.objects.filter(email__iexact=email).exists():
            messages.error(
                request,
                "That email address is already registered."
            )
            return redirect("register")

        # ==========================================
        # 5. PASSWORD CONFIRMATION
        # ==========================================

        if not password:
            messages.error(
                request,
                "Password is required."
            )
            return redirect("register")

        if password != cPassword:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("register")

        # ==========================================
        # 6. PASSWORD STRENGTH
        # ==========================================

        try:
            validate_password(password)
        except ValidationError as error:
            messages.error(
                request,
                "Password is too weak: " + " ".join(error.messages)
            )
            return redirect("register")

        # ==========================================
        # 7. TERMS
        # ==========================================

        terms = request.POST.get("terms")

        if not terms:
            messages.error(
                request,
                "You must agree to the Terms of Service."
            )
            return redirect("register")

        # ==========================================
        # CREATE USER
        # ==========================================

        newUser = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Profile Info

        bio = request.POST.get("bio", "").strip()
        avatar = request.POST.get("avatar", "")
        theme = request.POST.get("theme", "dark")


        profile = Profile.objects.create(
            user=newUser,
            avatar=avatar,
            bio=bio,
            theme=theme,
            font_size="medium"
        )


        # Favorite Fandoms

        fandoms = request.POST.getlist("fandomChoice")

        for fandom in fandoms:

            category = Category.objects.filter(
                name=fandom
            ).first()

            if category:
                profile.favorite_categories.add(category)

        profile.save()


        messages.success(
            request,
            "Registration successful! Welcome to Fan Hub+."
        )

        return redirect("login")

    return render(request, "register.html", {
            "categories": categories,
            "avatars": avatars,
        })

def login(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(
                request,
                "Please enter your username/email and password."
            )
            return render(request, "login.html")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            return redirect("home")

        else:

            messages.error(
                request,
                "Invalid username/email or password."
            )

            return render(request, "login.html")

    return render(request, "login.html")

def home(request):
    contents = Content.objects.all().order_by("-created_at")[:3]
    contentsTwo = Content.objects.all().order_by("-created_at")[:4]
    contentsLdb = Content.objects.all().order_by("view_count")[:3]
    categories = Category.objects.all().order_by("-created_at")[:4]
    characters = CharacterProfile.objects.all().order_by("name")[:4]
    merchs = Merch.objects.all().order_by("name")[:4]
    articles = FanSubmission.objects.all().order_by("title")[:3]
    events = EventHighlight.objects.all().order_by("event_date")[:3]


    context = {
        "categories": categories,
        "contents": contents,
        "contentsTwo": contentsTwo,
        "characters": characters,
        "merchs": merchs,
        "articles": articles,
        "events": events,
        "contentsLdb": contentsLdb,

    }

    return render(request, "index.html", context)
