"""
Catálogo de permisos agrupado por App → Modelo → acción, para la pantalla
de roles y permisos.

Incluye automáticamente las apps del proyecto (las que viven dentro de
BASE_DIR) más las indicadas en EXTRA_APPS, así que las apps nuevas aparecen
solas. Excluye los modelos históricos de django-simple-history.
"""

from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Permission

EXTRA_APPS = ('auth',)
# Nombres en español para apps de Django (USE_I18N = False)
APP_NAMES = {'auth': 'Autenticación y autorización'}
ACTIONS = (
    ('view', 'Ver'),
    ('add', 'Crear'),
    ('change', 'Editar'),
    ('delete', 'Eliminar'),
)


def _is_project_app(app_config):
    base_dir = Path(settings.BASE_DIR).resolve()
    return Path(app_config.path).resolve().is_relative_to(base_dir)


def _is_historical(model):
    return hasattr(model, 'instance_type') and \
        model.__name__.startswith('Historical')


def get_catalog():
    """
    Returns:
        list[dict]: [{'label', 'name', 'models': [{'name', 'cells': [perm|None x4],
                      'extra': [perm, ...]}]}]
    """
    app_configs = [
        app for app in apps.get_app_configs()
        if _is_project_app(app) or app.label in EXTRA_APPS
    ]
    permissions = Permission.objects.select_related('content_type').filter(
        content_type__app_label__in=[app.label for app in app_configs]
    )
    by_model = {}
    for perm in permissions:
        key = (perm.content_type.app_label, perm.content_type.model)
        by_model.setdefault(key, {})[perm.codename] = perm

    catalog = []
    for app in sorted(app_configs, key=lambda a: str(a.verbose_name)):
        models = []
        for model in app.get_models():
            if _is_historical(model):
                continue
            perms = by_model.get((app.label, model._meta.model_name), {})
            if not perms:
                continue
            model_name = model._meta.model_name
            default_codes = {f'{action}_{model_name}' for action, _ in ACTIONS}
            models.append({
                'name': str(model._meta.verbose_name_plural).capitalize(),
                'cells': [perms.get(f'{action}_{model_name}')
                          for action, _ in ACTIONS],
                'extra': sorted(
                    (p for code, p in perms.items() if code not in default_codes),
                    key=lambda p: p.name
                ),
            })
        if models:
            catalog.append({
                'label': app.label,
                'name': APP_NAMES.get(app.label,
                                      str(app.verbose_name).capitalize()),
                'models': sorted(models, key=lambda m: m['name']),
            })
    return catalog


def get_catalog_ids(catalog):
    ids = set()
    for app in catalog:
        for model in app['models']:
            ids.update(p.id for p in model['cells'] if p)
            ids.update(p.id for p in model['extra'])
    return ids


def apply_permissions(current_ids, posted_ids, catalog):
    """
    Calcula el nuevo conjunto de permisos: reemplaza solo los del catálogo
    y conserva los que estén fuera de él.
    """
    catalog_ids = get_catalog_ids(catalog)
    return (set(current_ids) - catalog_ids) | (set(posted_ids) & catalog_ids)


def parse_ids(values):
    ids = set()
    for value in values:
        if str(value).isdigit():
            ids.add(int(value))
    return ids
