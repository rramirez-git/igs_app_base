from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from .forms import MainForm


class Login(TemplateView):
    form_class = MainForm
    form = None
    titulo = None
    titulo_descripcion = None
    app = None
    status = None
    template_name = 'auth/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = self.titulo_descripcion
        context["toolbar_search"] = None
        context["toolbar"] = None
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = [self.status, ] if self.status else []
        context["req_chart"] = False
        context["search_value"] = None
        context["form"] = self.form
        context["without_btn_save"] = True
        context["app"] = self.app
        return context

    def success_redirect(self):
        next_url = self.request.GET.get('next')
        return redirect(next_url or 'session_imin')

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.success_redirect()
        self.form = self.form_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = self.form_class(self.request.POST)
        if self.form.is_valid():
            user = authenticate(
                request,
                username=self.form.cleaned_data['username'],
                password=self.form.cleaned_data['password'])
            if user and user.is_active:
                login(self.request, user)
                return self.success_redirect()
        self.status = {
            'msg': f"El usuario o la contraseña no son válidos",
            'type': 'danger', 'dismissible': True
        }
        return self.get(request, *args, **kwargs)


class Logout(TemplateView):

    def get(self, request, *args, **kwargs):
        logout(self.request)
        return redirect('session_login')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class ImIn(TemplateView):
    titulo = "Aplicaciones"
    titulo_descripcion = None
    app = None
    template_name = "html/html_struct.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = self.titulo_descripcion
        context["toolbar_search"] = None
        context["toolbar"] = None
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = None
        context["without_btn_save"] = True
        context["app"] = self.app
        context["include_apps_start"] = True
        return context
