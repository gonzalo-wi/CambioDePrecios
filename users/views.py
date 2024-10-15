from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import LoginForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from AppCambioPrecios.views import inicio
from users.forms import *


def login_request(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inicio')  
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form, 'msg_login': ''})

"""def login_request(request):
    msg_login = ""
    if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                usuario = form.cleaned_data.get('username')
                contrasenia = form.cleaned_data.get('password')
                user = authenticate(username=usuario, password = contrasenia)

                if user is not None:
                    login(request, user)
                    return render(request, "AppCambioPrecios/inicio.html")
            msg_login = "Usuario o contrasenia incorrectos"
    form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form, "msg_login": msg_login})"""