# -*- coding: utf-8 -*-
from os.path import dirname, join
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.template.base import TemplateDoesNotExist
from django.http.response import Http404

_path = dirname(__file__)

@override_settings(
    TEMPLATE_DIRS=(join(_path, 'templates'),),
    INSTALLED_APPS=('template_pages'),
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    TEMPLATE_PAGES_CONTEXT_MODULE=None,
)
class TestRoutingView(TestCase):
    urls = 'template_pages.tests.urls'
    _template_pages_test_context_module = 'template_pages.tests.template_pages_context'

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_file(self):
        response = self.client.get('/test1/')
        self.assertContains(response, 'This is test1.')

    @override_settings(
        TEMPLATE_PAGES_CONTEXT_MODULE=_template_pages_test_context_module
    )
    def test_file_with_context(self):
        response = self.client.get('/test1/')
        self.assertContains(response, 'Hello World!')

    def test_index(self):
        response = self.client.get('/')
        self.assertContains(response, 'This is index.')

    @override_settings(
        TEMPLATE_PAGES_CONTEXT_MODULE=_template_pages_test_context_module
    )
    def test_index_with_context(self):
        response = self.client.get('/')
        self.assertContains(response, 'Hello World!')

    def test_directory_index(self):
        response = self.client.get('/test2/')
        self.assertContains(response, 'This is test2 index.')

    @override_settings(
        TEMPLATE_PAGES_CONTEXT_MODULE=_template_pages_test_context_module
    )
    def test_directory_index_with_context(self):
        response = self.client.get('/test2/')
        self.assertContains(response, 'Hello World!')

    def test_file_inside_directory(self):
        response = self.client.get('/test2/test3/')
        self.assertContains(response, 'This is test2/test3.')

    @override_settings(
        TEMPLATE_PAGES_CONTEXT_MODULE=_template_pages_test_context_module
    )
    def test_file_inside_with_context(self):
        response = self.client.get('/test2/test3/')
        self.assertContains(response, 'Hello World!')

    def test_unicode_path(self):
        response = self.client.get(u'/django-wymiąta/'.encode('utf-8'))
        self.assertEqual(response.status_code, 404)

    def test_dir_up(self):
        response = self.client.get('/../index/')
        self.assertEqual(response.status_code, 404)

    def test_same_dir(self):
        response = self.client.get('/./test2/')
        self.assertEqual(response.status_code, 404)

    def test_redirect_wo_trailing_slash(self):
        response = self.client.get('/test2')
        self.assertRedirects(response, '/test2/', status_code=301)

    def test_not_supressing_errors(self):
        self.assertRaises(TemplateDoesNotExist, self.client.get, '/test4/')

    @override_settings(
        DEBUG=True
    )
    def test_not_supressing_errors_in_debug(self):
        self.assertRaises(TemplateDoesNotExist, self.client.get, '/test-rocket-cat-does-not-exists/')

    @override_settings(
        DEBUG=True
    )
    def test_supressing_errors__not_in_debug(self):
        response = self.client.get('/test-rocket-cat-does-not-exists/')
        self.assertEqual(response.status_code, 404)

