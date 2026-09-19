from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Project, Task


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner", "members", "created_at"]
        read_only_fields = ["owner"]


class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = UserSerializer(source="assignee", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "project", "title", "description",
            "assignee", "assignee_detail",
            "status", "priority", "due_date",
            "ai_suggestion", "created_at", "updated_at",
        ]
        read_only_fields = ["ai_suggestion"]
