"""
Test coverage for the core things an interviewer will actually ask about:
auth, RBAC enforcement, and basic CRUD correctness.

Run with: pytest
"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from tasks.models import Project, Task

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username="admin1", password="pass1234", role="ADMIN")


@pytest.fixture
def member_user(db):
    return User.objects.create_user(username="member1", password="pass1234", role="MEMBER")


@pytest.fixture
def other_member(db):
    return User.objects.create_user(username="member2", password="pass1234", role="MEMBER")


def auth_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def project(admin_user):
    return Project.objects.create(name="Website Revamp", owner=admin_user)


@pytest.fixture
def task(project, member_user):
    return Task.objects.create(project=project, title="Design homepage", assignee=member_user)


# --- Auth -----------------------------------------------------------------

@pytest.mark.django_db
def test_jwt_login_returns_access_token(member_user):
    client = APIClient()
    response = client.post("/api/auth/login/", {"username": "member1", "password": "pass1234"})
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_unauthenticated_request_is_rejected():
    client = APIClient()
    response = client.get("/api/tasks/")
    assert response.status_code == 401


# --- RBAC: the core of the project -----------------------------------------

@pytest.mark.django_db
def test_admin_can_see_all_tasks(admin_user, task):
    client = auth_client(admin_user)
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_member_only_sees_own_tasks(member_user, other_member, project, task):
    # A task assigned to someone else
    Task.objects.create(project=project, title="Not mine", assignee=other_member)

    client = auth_client(member_user)
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == "Design homepage"


@pytest.mark.django_db
def test_member_cannot_access_others_task_directly(other_member, task):
    client = auth_client(other_member)
    response = client.get(f"/api/tasks/{task.id}/")
    # get_queryset already filters it out for members, so this correctly 404s
    assert response.status_code == 404


@pytest.mark.django_db
def test_member_cannot_create_project(member_user):
    client = auth_client(member_user)
    response = client.post("/api/projects/", {"name": "New Project"})
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_create_project(admin_user):
    client = auth_client(admin_user)
    response = client.post("/api/projects/", {"name": "New Project"})
    assert response.status_code == 201
    assert response.data["owner"]["username"] == "admin1"


# --- CRUD correctness -------------------------------------------------

@pytest.mark.django_db
def test_member_can_update_own_task_status(member_user, task):
    client = auth_client(member_user)
    response = client.patch(f"/api/tasks/{task.id}/", {"status": "DONE"})
    assert response.status_code == 200
    task.refresh_from_db()
    assert task.status == "DONE"


@pytest.mark.django_db
def test_task_filtering_by_status(admin_user, project, member_user):
    Task.objects.create(project=project, title="A", status="DONE", assignee=member_user)
    Task.objects.create(project=project, title="B", status="TODO", assignee=member_user)

    client = auth_client(admin_user)
    response = client.get("/api/tasks/?status=DONE")
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["title"] == "A"
