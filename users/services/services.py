from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate


def register_user_and_redirect(request, form):

    user = form.save()
    login(request, user)
    return redirect("social_networks:index")


def authenticate_user_and_redirect(request, form):

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("social_networks:index")
    else:
        return render(request, "users/sign_in.html", {'form': form})