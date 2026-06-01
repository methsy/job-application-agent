from app.core.config import settings


def test_settings_load_database_url():
    assert settings.database_url
    assert "postgresql+psycopg" in settings.database_url
