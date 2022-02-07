from ..accounts.models import User
from ..courses.utils.certificates.certificates import create_certificate
from .models import Quiz, QuizTaker


def get_certificate(quiz: Quiz, user: User, quiztaker: QuizTaker, domain: str):
    """Create certificates for course and certificated_courses if necessary"""
    if quiz.is_final:
        course = quiz.course_object
        if course.certificate:
            return create_certificate(user, domain, course=quiztaker.quiz.course_object)

    if quiz.is_for_certificated_course:
        certificated_course = quiz.certificated_course
        return create_certificate(user, domain, certificated_course=certificated_course)
