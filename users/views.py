from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import auth


def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Я Тут")
            
            user = form.save()
            login(request, user)
            return redirect("social_networks:index")
    else:
        form = UserCreationForm()
    content = {"form": form}
    return render(request, 'users/sign_up.html', content)


def sign_in(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print("Я тут тут")
                login(request, user)
                return redirect("social_networks:index")

    else:
        form = AuthenticationForm()
    content = {"form": form}
    return render(request, "users/sign_in.html", content)


def sign_out(request):
    auth.logout(request)
    return redirect("social_networks:index")
