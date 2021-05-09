from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class AboutURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_pages_access(self):
        urls_list = [
            reverse('about:author'),
            reverse('about:tech'),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech'))
        ]
        for template, reverse_name in templates_url_names:
            with self.subTest():
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
