import pytest

@pytest.fixture(autouse=True)
def use_in_memory_db(monkeypatch):
    monkeypatch.setattr(
        'django.conf.settings.DATABASES',
        {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
    )
