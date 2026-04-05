import os

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.db.models import Model
from django.db.models import Q
from django.db.models import QuerySet
from django.urls import path
from django.urls import reverse
from functools import reduce
from typing import Any

from igs_app_base.templatetags.crud_helpers import action_label
from igs_app_base.templatetags.crud_helpers import action_smart_button
from igs_app_base.templatetags.crud_helpers import crud_label
from igs_app_base.templatetags.crud_helpers import crud_smart_button

from ..menu.models import MenuOpc
from .permission import model_perms_4_user


def get_model_attr(instance: Any, attr: str) -> Any:
    for field in attr.split('__'):
        if instance is None:
            break
        instance = getattr(instance, field)
    return instance


def get_next_prev_object(
        instance, prev: bool = False, qs: QuerySet = None, loop: bool = False
        ) -> Any | None:
    if not qs:
        qs = instance._meta.model.objects.all()
    if prev:
        qs = qs.reverse()
        lookup = 'lt'
    else:
        lookup = 'gt'
    q_list = []
    prev_fields = []
    if qs.query.extra_order_by:
        ordering = qs.query.extra_order_by
    elif qs.query.order_by:
        ordering = qs.query.order_by
    elif qs.query.get_meta().ordering:
        ordering = qs.query.get_meta().ordering
    else:
        ordering = []
    ordering = list(ordering)
    if 'pk' not in ordering and '-pk' not in ordering:
        ordering.append('pk')
        qs = qs.order_by(*ordering)
    for field in ordering:
        if field[0] == '-':
            this_lookup = (lookup == 'gt' and 'lt' or 'gt')
            field = field[1:]
        else:
            this_lookup = lookup
        q_kwargs = dict([(f, get_model_attr(instance, f))
                         for f in prev_fields if get_model_attr(
                instance, f) is not None])
        key = "%s__%s" % (field, this_lookup)
        q_kwargs[key] = get_model_attr(instance, field)
        if q_kwargs[key] is None:
            del q_kwargs[key]
        q_list.append(Q(**q_kwargs))
        prev_fields.append(field)
    try:
        obj = qs.filter(reduce(Q.__or__, q_list))[0]
        return obj if instance.pk != obj.pk else None
    except IndexError:
        length = qs.count()
        if loop and length > 1:
            obj = qs[0]
            return obj if instance.pk != obj.pk else None
    return None


def create_crud_toolbar_dict(
        user: User, model: Model, pk: int,
        label_and_icon: bool = False, blinder_model: str = None
        ) -> tuple[dict, dict]:
    perms = model_perms_4_user(model, user, blinder_model)
    base_name = blinder_model if blinder_model else model.__name__.lower()
    toolbar = dict()
    if perms['list']:
        toolbar['list'] = {
            'type': 'link',
            'view': f'{base_name}_list',
            'label': crud_smart_button('list', label_and_icon),
            'title': crud_label('list')}
    if perms['create']:
        toolbar['create'] = {
            'type': 'link',
            'view': f'{base_name}_create',
            'label': crud_smart_button('create', label_and_icon),
            'title': crud_label('create')}
    if perms['read']:
        toolbar['read'] = {
            'type': 'link_pk',
            'view': f'{base_name}_read',
            'pk': pk,
            'label': crud_smart_button('read', label_and_icon),
            'title': crud_label('read')}
    if perms['update']:
        toolbar['update'] = {
            'type': 'link_pk',
            'view': f'{base_name}_update',
            'pk': pk,
            'label': crud_smart_button('update', label_and_icon),
            'title': crud_label('update')}
        toolbar['update_many'] = {
            'type': 'button',
            'label': crud_smart_button('update', label_and_icon),
            'title': crud_label('update'),
            'onclick': 'update_many_records()', }
    if perms['delete']:
        toolbar['delete'] = {
            'type': 'link_pk_del',
            'view': f'{base_name}_delete',
            'pk': pk,
            'label': crud_smart_button('delete', label_and_icon),
            'title': crud_label('delete')}
        toolbar['delete_many'] = {
            'type': 'button',
            'label': crud_smart_button('delete', label_and_icon),
            'title': crud_label('delete'),
            'onclick': 'delete_many_records()', }
    return perms, toolbar


def crud_toolbar(
        user: User, object, label_and_icon: bool = False,
        blinder_model: str = None, qs: Any = None) -> list:
    perms, buttons = create_crud_toolbar_dict(
        user, object._meta.model, object.pk, label_and_icon, blinder_model)
    base_name = blinder_model if blinder_model \
        else object._meta.model.__name__.lower()
    toolbar = []
    if perms['list']:
        toolbar.append(buttons['list'])
    if perms['update']:
        toolbar.append(buttons['update'])
    if perms['delete']:
        toolbar.append(buttons['delete'])
    next = get_next_prev_object(object, qs=qs)
    prev = get_next_prev_object(object, True, qs)
    if prev:
        toolbar.append({
            'type': 'link_pk',
            'label': action_smart_button('prev_item', label_and_icon),
            'title': action_label('prev_item'),
            'view': f'{base_name}_read',
            'pk': prev.pk})
    if next:
        toolbar.append({
            'type': 'link_pk',
            'label': action_smart_button('next_item', label_and_icon),
            'title': action_label('next_item'),
            'view': f'{base_name}_read',
            'pk': next.pk})
    return toolbar


def crud_list_toolbar(
        user: User, model: Model,
        label_and_icon: bool = False, blinder_model: str = None) -> list:
    perms, buttons = create_crud_toolbar_dict(
        user, model, 0, label_and_icon, blinder_model)
    toolbar = []
    if perms['create']:
        toolbar.append(buttons['create'])
    if perms['update']:
        toolbar.append(buttons['update_many'])
    if perms['delete']:
        toolbar.append(buttons['delete_many'])
    return toolbar


def absolute_url(object: Model) -> str:
    return reverse(
        type(object).__name__.lower() + "_read", kwargs={"pk": object.pk})


def update_permission():
    Group.objects.get_or_create(name="SuperAdministrador")[0].permissions.set(
        Permission.objects.all())

    Group.objects.get_or_create(name="Solo Lectura")[0].permissions.set(
        Permission.objects.filter(codename__icontains='view_'))

    prefijos = [
        ('add', 'Agregar', ),
        ('change', crud_label('update'),),
        ('delete', crud_label('delete'),),
        ('view', crud_label('read'),),
    ]
    for prefijo in prefijos:
        for p in Permission.objects.filter(
                codename__icontains=f"{prefijo[0]}_"):
            p.name = str(p.name).replace(f"Can {prefijo[0]}", prefijo[1])
            p.save()


def create_path(path: str) -> None:
    if os.path.splitext(path)[1] != "":
        path = os.path.split(path)[0]
    if not os.path.exists(path):
        path_parts = os.path.split(path)
        create_path(path_parts[0])
        if path_parts[1] != "":
            os.mkdir(os.path.join(path_parts[0], path_parts[1]))


def create_view_urls(
        app_label: str, model_name: str,
        list_view: Any, create_view: Any, update_view: Any, read_view: Any,
        delete_many_view: Any, delete_view: Any) -> list:
    return [
        path(
            '',
            permission_required(f"{app_label}.view_{model_name}", '/')(
                list_view.as_view()),
            name=f"{model_name}_list"),
        path(
            'nuevo/',
            permission_required(f"{app_label}.add_{model_name}", '/')(
                create_view.as_view()),
            name=f"{model_name}_create"),
        path(
            'actualizar/<int:pk>',
            permission_required(f"{app_label}.change_{model_name}", '/')(
                update_view.as_view()),
            name=f"{model_name}_update"),
        path(
            'eliminar/multiple/',
            permission_required(f"{app_label}.delete_{model_name}", '/')(
                delete_many_view.as_view()),
            name=f"{model_name}_delete_many"),
        path(
            'eliminar/<int:pk>',
            permission_required(f"{app_label}.delete_{model_name}", '/')(
                delete_view.as_view()),
            name=f"{model_name}_delete"),
        path(
            '<int:pk>',
            permission_required(f"{app_label}.view_{model_name}", '/')(
                read_view.as_view()),
            name=f"{model_name}_read"),
    ]


def add_or_create_menuopc(
        nombre: str, posicion: int, padre: MenuOpc, model_name: str = None,
        perms: str | list = "__base__", vista: str = None) -> MenuOpc:
    if vista is None:
        vista = f"{model_name}_list"
    mnuopc, created = MenuOpc.objects.get_or_create(
        nombre=nombre,
        vista=vista,
        posicion=posicion,
        padre=padre
    )
    if created:
        if perms == "__base__":
            mnuopc.permisos_requeridos.set([
                Permission.objects.get(codename=f'add_{model_name}'),
                Permission.objects.get(codename=f'change_{model_name}'),
                Permission.objects.get(codename=f'delete_{model_name}'),
                Permission.objects.get(codename=f'view_{model_name}'),
            ])
        elif perms == "__all__":
            mnuopc.permisos_requeridos.set(Permission.objects.filter(
                codename__icontains=f"_{model_name}"))
        elif perms and isinstance(perms, list):
            mnuopc.permisos_requeridos.set(perms)
    return mnuopc


def get_user_from_context(context: Any, user_pk: User | int) -> User | None:
    user = context.get('user')
    if user is None:
        if isinstance(user_pk, User):
            user = user_pk
        else:
            user = User.objects.filter(pk=user_pk)
            if user.exists():
                user = user[0]
    if isinstance(user, AnonymousUser):
        return None
    return user


def get_apps():
    return [
        app for app in settings.INSTALLED_APPS
        if app.find("django.contrib") == -1 and
        app.find("django_extensions") == -1 and
        app.find("crispy_") == -1]


def get_from_request(request: Any, param: str) -> str:
    return request.GET.get(param) or request.POST.get(param)
