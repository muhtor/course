from rest_framework import permissions


class IsAvailableForQuiz(permissions.BasePermission):
    message = "Previous material wasn't completed"

    def has_object_permission(self, request, view, quiz):
        return not quiz.is_blocked_for_user(request.user)


class IsQuizTakerAvailable(permissions.BasePermission):
    message = "Quiz is blocked for you now"

    def has_object_permission(self, request, view, quiz):
        return not request.user.quiz_takers.filter(quiz=quiz).last().is_blocked
