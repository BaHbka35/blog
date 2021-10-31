from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, \
    AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import auth

from .services.services import register_user_and_redirect, \
    authenticate_user_and_redirect


def sign_up(request):
    """
    View for users registration
    """

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():

            return register_user_and_redirect(request, form)
    else:
        form = UserCreationForm()
    content = {"form": form}
    return render(request, 'users/sign_up.html', content)


def sign_in(request):
    """
    View for user authorization
    """

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():

            return authenticate_user_and_redirect(request, form)

    else:
        form = AuthenticationForm()

    content = {"form": form}
    return render(request, "users/sign_in.html", content)


def sign_out(request):
    """
    View for user log out
    """

    auth.logout(request)
    return redirect("social_networks:index")
