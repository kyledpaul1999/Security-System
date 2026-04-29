
import pytest
from django.db import IntegrityError
from django.utils import timezone
from .models import User, Role, UserRole, Session, ApiKey

@pytest.mark.django_db
class TestUserModel:

    def test_create_user(self):
        """Test creating a standard user."""
        user = User.objects.create_user(username="testuser", password="password123")
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("password123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(username="admin", password="password123")
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_username_must_be_unique(self):
        """Test that usernames are unique."""
        User.objects.create_user(username="testuser", password="p1")
        with pytest.raises(IntegrityError):
            User.objects.create_user(username="testuser", password="p2")

@pytest.mark.django_db
class TestRoleAndUserRoleModels:

    def test_create_role(self):
        """Test creating a Role."""
        role = Role.objects.create(name="Administrator", description="Full system access")
        assert role.name == "Administrator"

    def test_role_name_unique(self):
        """Test that role names are unique."""
        Role.objects.create(name="Admin")
        with pytest.raises(IntegrityError):
            Role.objects.create(name="Admin")

    def test_assign_role_to_user(self):
        """Test the UserRole relationship."""
        user = User.objects.create_user(username="viewer", password="password")
        role = Role.objects.create(name="Viewer")
        UserRole.objects.create(user=user, role=role)
        assert user.userrole_set.count() == 1
        assert role.userrole_set.count() == 1

    def test_user_role_unique_together(self):
        """Test that a user cannot be assigned the same role twice."""
        user = User.objects.create_user(username="editor", password="p")
        role = Role.objects.create(name="Editor")
        UserRole.objects.create(user=user, role=role)
        with pytest.raises(IntegrityError):
            UserRole.objects.create(user=user, role=role)

    def test_delete_user_cascades_user_role(self):
        """Test that deleting a user removes their role assignments."""
        user = User.objects.create_user(username="test", password="p")
        role = Role.objects.create(name="TestRole")
        UserRole.objects.create(user=user, role=role)
        assert UserRole.objects.count() == 1
        user.delete()
        assert UserRole.objects.count() == 0

@pytest.mark.django_db
class TestSessionAndApiKeyModels:

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="api_user", password="password")

    def test_create_session(self, user):
        """Test creating a user session."""
        session = Session.objects.create(
            user=user,
            refresh_token_hash="some_hash",
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
        assert user.session_set.count() == 1
        assert session.user == user

    def test_create_api_key(self, user):
        """Test creating an API key for a user."""
        api_key = ApiKey.objects.create(
            user=user,
            key_hash="another_hash",
            name="My Test Key"
        )
        assert user.apikey_set.count() == 1
        assert api_key.name == "My Test Key"

    def test_delete_user_cascades_sessions_and_apikeys(self, user):
        """Test that deleting a user deletes their sessions and API keys."""
        Session.objects.create(user=user, refresh_token_hash="s_hash", expires_at=timezone.now())
        ApiKey.objects.create(user=user, key_hash="a_hash", name="A Key")
        assert Session.objects.count() == 1
        assert ApiKey.objects.count() == 1
        user.delete()
        assert Session.objects.count() == 0
        assert ApiKey.objects.count() == 0
