from rest_framework import permissions


class IsLessonCoursePaid(permissions.BasePermission):
    message = 'Course was not paid'

    def has_object_permission(self, request, view, lesson):
        try:
            lesson.previous_lesson.id
        except IndexError:
            return True  # If the lesson is first, it's not blocked
        return request.user.profile.is_course_paid(lesson.topic.course)


class IsUserLessonCoursePaid(permissions.BasePermission):
    message = 'Course was not paid'

    def has_object_permission(self, request, view, user_lesson):
        return request.user.profile.is_course_paid(user_lesson.lesson.topic.course)


class IsAvailableForLesson(permissions.BasePermission):
    message = 'Previous lesson was not completed'

    def has_object_permission(self, request, view, lesson):
        return not lesson.is_blocked(request.user)
