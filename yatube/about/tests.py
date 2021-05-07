from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_pages_access(self):
        urls_list = [
            '/about/author/',
            '/about/tech/',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            ('about/author.html', '/about/author/'),
            ('about/tech.html', '/about/tech/')
        ]
        for template, reverse_name in templates_url_names:
            with self.subTest():
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
