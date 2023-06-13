import inspect
import os
import uuid
from importlib import import_module

import pytest
from django.conf import settings
from django.http import HttpRequest
from pytest_django.asserts import assertTemplateUsed


def test_csrf_failure_view():
    csrf_failure_view_setting = getattr(settings, 'CSRF_FAILURE_VIEW', '')
    module_name, function_name = csrf_failure_view_setting.rsplit('.', 1)
    csrf_failure_view = None
    try:
        module = import_module(module_name)
        csrf_failure_view = getattr(module, function_name, None)
    except Exception:
        pass
    assert csrf_failure_view, (
        'Убедитесь, что задали настройку `CSRF_FAILURE_VIEW` '
        'в `settings.py`, и что она указывает на существующую view-функцию.')

    request = HttpRequest()
    request.method = 'POST'
    request.POST = {}

    try:
        response = csrf_failure_view(request)
    except Exception:
        raise AssertionError(
            f'Убедитесь, что view-функция `{csrf_failure_view_setting}` '
            f'работает без ошибок.')
    else:
        csrf_status = 403
        assert response.status_code == csrf_status, (
            f'Убедитесь, что view-функция `{csrf_failure_view_setting}` '
            f'возвращает статус {csrf_status}.'
        )


@pytest.mark.django_db
def test_custom_err_handlers(client, user_client):
    err_pages_vs_file_names = {
        404: '404.html',
        403: '403csrf.html',
        500: '500.html'
    }
    for status, fname in err_pages_vs_file_names.items():
        fpath = settings.TEMPLATES_DIR / 'pages' / fname
        assert os.path.isfile(fpath.resolve()), (
            f'Убедитесь, что файл шаблона `{fpath}` существует.'
        )

    try:
        from blogicum.urls import handler500
    except Exception:
        raise AssertionError(
            'Убедитесь, что задали обработчик ошибки со статусом 500 в '
            'головном файле с маршрутами, и что в этом файле нет ошибок.'
        )

    try:
        from pages import views as pages_views
    except Exception:
        raise AssertionError(
            'Убедитесь, что в файле `pages/views.py` нет ошибок.')

    for status, fname in err_pages_vs_file_names.items():
        assert fname in inspect.getsource(pages_views), (
            'Проверьте вью функции приложения `pages`: убедитесь, '
            f'что для генерации страниц со статусом ответа `{status}` '
            f'используется шаблон `pages/{fname}`')

    # test template for 404
    debug = settings.DEBUG
    settings.DEBUG = False

    status = 404
    fname = err_pages_vs_file_names[status]
    non_existing_url = uuid.uuid4()
    expected_template = f'pages/{fname}'
    response = client.get(non_existing_url)
    assertTemplateUsed(
        response, expected_template,
        f'Убедитесь, что для страниц со статусом ответа `{status}` '
        f'используется шаблон `{expected_template}`')

    settings.DEBUG = debug
