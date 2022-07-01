from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, LogoutView)
from .modules.forms import LoginForm
from . import sparql
import os

class Login(LoginView):
    """ログインページ"""

    form_class = LoginForm
    template_name = os.getcwd() + '/templates/accounts/accounts.html'

class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = os.getcwd()+'/templates/accounts/accounts.html'

class Logout1(TemplateView):
    template_name = os.getcwd()+'/templates/accounts/logout.html'

class TopView(LoginRequiredMixin, TemplateView):
    # return render(request, os.getcwd()+'/templates/accounts/hello.html')
    #return render(request, os.getcwd()+'/templates/accounts/hello.html')
    template_name = os.getcwd()+'/templates/accounts/hello.html'
    login_url = '/login'


# Create your views here.
