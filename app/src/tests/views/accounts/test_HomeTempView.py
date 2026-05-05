import pytest
from django.urls import reverse
from tests.base.BaseTestView import BaseTestView


@pytest.mark.django_db
class TestHomeTempView(BaseTestView):

    @pytest.fixture
    def url(self):
        return reverse('home')

    def test_title_in_context(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
        assert 'title' in response.context
        assert response.context['title'] == 'Bienvenido a Base Sistema'
