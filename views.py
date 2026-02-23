import importlib
import os

from datetime import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import Model
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from typing import Any
from django.shortcuts import redirect

from .templatetags.crud_helpers import crud_label
from .templatetags.crud_helpers import crud_smart_button
from .utils.utils import absolute_url
from .utils.utils import create_view_urls
from .utils.utils import crud_list_toolbar
from .utils.utils import crud_toolbar
from .utils.utils import update_permission


class GenericList(ListView):
    titulo = ""
    titulo_descripcion = ""
    app = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = self.titulo_descripcion
        context["toolbar_search"] = None
        context["toolbar"] = crud_list_toolbar(self.request.user, self.model)
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = None
        context["without_btn_save"] = True
        context["app"] = self.app
        return context


class GenericRead(DetailView):
    titulo = ""
    app = None
    form_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = str(self.object)
        context["toolbar_search"] = False
        context["toolbar"] = crud_toolbar(self.request.user, self.object)
        context["footer"] = False
        context["read_only"] = True
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = {'top': [{
            'form': self.form_class(instance=self.object)}]}
        context["without_btn_save"] = True
        context["app"] = self.app
        return context


class GenericReadSuperCatalog(GenericRead):
    form_class_opcion = None
    model_opcion = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['toolbar_opciones'] = [
            {
                'type': 'button',
                'label': crud_smart_button('create'),
                'title': crud_label('create'),
                'onclick': f'create_tipo_opcion()'},
            {
                'type': 'button',
                'label': crud_smart_button('update'),
                'title': crud_label('update'),
                'onclick': f'update_{self.model.__name__.lower()}_opcion()'},
            {
                'type': 'button',
                'label': crud_smart_button('delete'),
                'title': crud_label('delete'),
                'onclick': f'delete_tipo_opcion()'}
        ]
        context["form_opc"] = self.form_class_opcion()
        return context

    def create_opcion(self, post: Any, files: Any):
        pass

    def update_opcion(self, post: Any, files: Any):
        pass

    def delete_opcion(self, post: Any):
        extra = post.get("extra")
        if extra:
            self.model_opcion.objects.filter(pk__in=extra.split(",")).delete()

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "create":
            self.create_opcion(request.POST, request.FILES)
        elif action == "update":
            self.update_opcion(request.POST, request.FILES)
        elif action == "delete":
            self.delete_opcion(request.POST)
        return redirect(request.path)


class GenericCreate(CreateView):
    titulo = ""
    app = None
    toolbar = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = crud_label('create')
        context["toolbar_search"] = False
        context["toolbar"] = self.toolbar
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = {'top': [{'form': context['form']}]}
        context["without_btn_save"] = False
        context["app"] = self.app
        return context

    def get_success_url(self):
        try:
            return super().get_success_url()
        except ImproperlyConfigured:
            return absolute_url(self.object)


class GenericUpdate(UpdateView):
    titulo = ""
    app = None
    toolbar = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = \
            f"{self.object} ({crud_label('update')})"
        context["toolbar_search"] = False
        context["toolbar"] = self.toolbar
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = {'top': [{'form': context['form']}]}
        context["without_btn_save"] = False
        context["app"] = self.app
        return context

    def get_success_url(self):
        try:
            return super().get_success_url()
        except ImproperlyConfigured:
            return absolute_url(self.object)


class GenericDelete(DeleteView):

    def get_success_url(self):
        url = None
        try:
            url = super().get_success_url()
        except ImproperlyConfigured:
            url = reverse(self.model.__name__.lower() + "_list")
        return url


class GenericDeleteMany(TemplateView):

    def post(self, request, *args, **kwargs):
        ids = [
            int("0" + id)
            for id in self.request.POST.get('ids', '').split(',')]
        self.model.objects.filter(pk__in=ids).delete()
        return HttpResponse(",".join([str(id) for id in ids]))


class GenericViews:

    def __init__(
            self, model: Model, titulo: str, titulo_pl: str, app: str,
            frmCreate: Any, frmRead: Any, frmUpdate: Any):

        class List(GenericList):
            pass

        class Read(GenericRead):
            pass

        class Create(GenericCreate):
            pass

        class Update(GenericUpdate):
            pass

        class Delete(GenericDelete):
            pass

        class DeleteMany(GenericDeleteMany):
            pass

        self.model = model
        self.titulo = titulo
        self.titulo_pl = titulo_pl
        self.app = app
        self.frmCreate = frmCreate
        self.frmUpdate = frmUpdate
        self.frmRead = frmRead
        self.List = List
        self.Read = Read
        self.Create = Create
        self.Update = Update
        self.Delete = Delete
        self.DeleteMany = DeleteMany
        views = [
            self.List, self.Read,
            self.Create, self.Update,
            self.Delete, self.DeleteMany]
        for view in views:
            view.model = self.model
            view.titulo = self.titulo
            view.app = self.app
        self.List.titulo = self.titulo_pl
        self.Create.form_class = self.frmCreate
        self.Update.form_class = self.frmUpdate
        self.Read.form_class = self.frmRead

    def create_urls(self, app_label: str) -> list:
        return create_view_urls(
            app_label, self.model.__name__.lower(),
            self.List, self.Create, self.Update, self.Read,
            self.DeleteMany, self.Delete)


class Migrate(TemplateView):
    migr_dir = settings.DATA_MIGRATION_DIR
    app = 'configuracion'
    template_name = "utils/migracion.html"
    titulo = "Aplicacion Automática de Migraciones"
    toolbar = None

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def add_2_db(self, filename: str) -> None:
        sql = f"""
                    INSERT INTO django_migrations(app, name, applied)
                    VALUES (
                        'data_migration',
                        '{filename[:-3]}',
                        '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'
                        );
                """
        with connection.cursor() as cursor:
            cursor.execute(sql)

    def verify_db(self, filename: str) -> bool:
        sql = f"""
                    SELECT COUNT(*) AS n
                    FROM django_migrations
                    WHERE app = 'data_migration' AND name = '{filename[:-3]}';
                """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return int(rows[0][0]) == 0

    def apply(self, app: str, filename: str) -> dict:
        result = ""
        try:
            file = os.path.join(
                settings.BASE_DIR, app, self.migr_dir, filename)
            if os.path.exists(file):
                module_name = os.path.join(
                    app, self.migr_dir, filename).replace(
                        os.sep, '.')[:-3]
                module = importlib.import_module(module_name)
                module.migration()
                result = "ok"
        except Exception as e:
            result = f"{type(e).__name__}: {e}"
        finally:
            return {
                "file": app + os.sep + filename[:-3],
                "result": result,
            }

    def get_files_and_apply(self) -> list:
        migraciones = list()
        update_permission()
        for app in settings.INSTALLED_APPS:
            app_path = os.path.join(settings.BASE_DIR, app, self.migr_dir)
            if os.path.exists(app_path):
                for root, dirs, files in os.walk(app_path):
                    if root == app_path:
                        files = sorted(files)
                        for f in files:
                            if "py" == f[-2:].lower():
                                if self.verify_db(app + os.sep + f):
                                    result = self.apply(app, f)
                                    migraciones.append(result)
                                    if result['result'] == "ok":
                                        self.add_2_db(app + os.sep + f)
                                else:
                                    migraciones.append({
                                        'file': app + os.sep + f[:-3],
                                        'result': "previo",
                                    })
        return migraciones

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["migraciones"] = self.get_files_and_apply()
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = None
        context["toolbar_search"] = False
        context["toolbar"] = self.toolbar
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = None
        context["without_btn_save"] = True
        context["app"] = self.app
        return context


class GenericAppRootView(TemplateView):
    app = None
    template_name = "app/empty.html"
    titulo = None
    titulo_descripcion = None
    toolbar = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = self.titulo
        context["titulo_descripcion"] = self.titulo_descripcion
        context["toolbar_search"] = False
        context["toolbar"] = self.toolbar
        context["footer"] = False
        context["read_only"] = False
        context["alertas"] = []
        context["mensajes"] = []
        context["req_chart"] = False
        context["search_value"] = None
        context["forms"] = None
        context["without_btn_save"] = True
        context["app"] = self.app
        return context
