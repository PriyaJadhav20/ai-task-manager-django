from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsAdminOrReadOnlyForProject, IsAdminOrAssignedMember
from .ai_utils import suggest_priority_and_subtasks

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnlyForProject]

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN":
            return Project.objects.all()
        # Members only see projects they own or belong to
        return Project.objects.filter(members=user) | Project.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrAssignedMember]
    filterset_fields = ["status", "priority", "assignee", "project"]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN":
            return Task.objects.all()
        return Task.objects.filter(assignee=user)

    @action(detail=True, methods=["post"], url_path="ai-suggest")
    def ai_suggest(self, request, pk=None):
        """
        POST /api/tasks/{id}/ai-suggest/
        Calls Groq to suggest a priority + subtasks for this task, and
        stores the raw suggestion on the task for later reference.
        """
        task = self.get_object()
        result = suggest_priority_and_subtasks(task.title, task.description)
        task.ai_suggestion = str(result)
        task.save(update_fields=["ai_suggestion"])
        return Response(result)
