from datetime import datetime, timezone, timedelta

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone as django_timezone
from django.utils.translation import gettext_lazy as _

from slugify import slugify
from ..core.models import TimestampedModel
from ..accounts.models import User


class Quiz(TimestampedModel):
    title = models.CharField(max_length=100, verbose_name=_('Quiz Name'))
    topic = models.OneToOneField(
        'courses.Topic', on_delete=models.CASCADE, verbose_name=_('Topic (if quiz is not final)'),
        related_name='quiz', null=True, blank=True
    )
    course = models.OneToOneField(
        'courses.Course', on_delete=models.CASCADE, verbose_name=_('Course (if quiz is final)'),
        related_name='final_quiz', null=True, blank=True
    )
    certificated_course = models.OneToOneField(
        'courses.CertificatedCourse', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('Certificated course (if quiz for them)'), related_name='quiz'
    )
    duration = models.IntegerField(
        default=40, verbose_name=_('Test duration'), help_text=_('Duration of the quiz in minutes'))
    required_score_to_pass = models.IntegerField(
        help_text=_('Required score to pass the quiz (%)'), default=80, verbose_name=_('Required score'))
    chances = models.SmallIntegerField(_('Chances count'), default=5)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('  Quizzes')
        ordering = ['id']

    def save(self, *args, **kwargs):
        objects = (self.topic, self.course, self.certificated_course)
        defined_objects_count = 0
        for obj in objects:
            if obj:
                defined_objects_count += 1
        if defined_objects_count > 1:
            raise ValueError('You should define only 1 obj: topic, course, certificated course')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_final(self):
        return bool(self.course)

    @property
    def is_for_certificated_course(self):
        return bool(self.certificated_course)

    def is_completed(self, user: User) -> bool:
        try:
            return QuizTaker.objects.get(user=user, quiz=self).completed
        except:
            return False

    def is_certificated_quiz_blocked(self, user: User) -> bool:
        return not self.certificated_course.is_completed(user)

    def is_blocked_for_user(self, user: User) -> bool:
        if self.is_for_certificated_course:
            return self.is_certificated_quiz_blocked(user)
        elif self.is_final:
            last_lesson = self.course.topic_courses.last().lessons.last()
        else:
            last_lesson = self.topic.lessons.last()
        if not self.is_final or not Quiz.objects.filter(topic=self.course.topic_courses.last()).exists():
            # Quiz isn't final or there're no any quizzes except the 'self'
            # Last lesson in the topic should be finished
            return not last_lesson.is_lesson_finished(user)

        try:
            # Last quiz should be passed if the quiz is final
            return not QuizTaker.objects.get(user=user, quiz=self.course.topic_courses.last().quiz).completed
        except:
            return True

    @property
    def course_object(self):
        if self.is_final:
            return self.course
        if self.certificated_course:
            return self.certificated_course
        return self.topic.course

    def get_questions_count(self):
        return self.questions.all().count()


class Question(TimestampedModel):
    SCALE = (
        (0, _('Interval Test')),
        (1, _('Final Test'))
    )
    Type = (
        (0, _('Single Choice')),
        (1, _('Multiple Choice')),
        (2, _('True/False')),
    )
    quiz = models.ForeignKey(Quiz, default=1, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255, verbose_name=_('Question Title'))
    technique = models.IntegerField(choices=Type, default=0, verbose_name=_('Type of Question'))
    type_of_test = models.IntegerField(choices=SCALE, default=0, verbose_name=_('Type of Test'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active Status'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Created'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _(' Questions')
        ordering = ['id']

    def get_technique_name(self, technique_index):
        for idx, name in self.Type:
            if idx == technique_index:
                return name


class Answer(TimestampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default=1, related_name='answers')
    title = models.CharField(max_length=100, verbose_name=_('Answer text'))
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answers')
        ordering = ['id']


class QuizTaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_takers')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name=_('Quiz'), related_name='takers')
    score = models.IntegerField(default=0, verbose_name=_('Score'))
    completed = models.BooleanField(default=False, verbose_name=_('Completed'))
    chances_left = models.SmallIntegerField(_('Chances left'), default=5)
    unlock_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Unlock quiz at'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Created'))

    class Meta:
        verbose_name = _('Quiz Taker')
        verbose_name_plural = _('Quiz Takers')
        ordering = ['id']

    def save(self, *args, **kwargs):
        if self.chances_left == 0:
            self.unlock_at = datetime.utcnow() + timedelta(days=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.phone}"

    @property
    def time_left(self):
        processing_seconds = (datetime.now(timezone.utc) - self.date_created).total_seconds()
        left_seconds = int(self.quiz.duration * 60 - processing_seconds)
        return str(timedelta(seconds=left_seconds))

    @property
    def is_blocked(self) -> bool:
        if not self.unlock_at:
            return False

        blocked = django_timezone.now() < self.unlock_at
        if not blocked:
            if self.chances_left < 1:
                # Increase chances if locked time has gone
                self.increase_chances(5)
            return False
        return True

    def decrease_chances(self, count: int = 1):
        self.chances_left -= count
        self.save(update_fields=('chances_left',))

    def increase_chances(self, count: int = 1):
        self.chances_left += count
        self.save(update_fields=('chances_left',))


class UsersAnswer(models.Model):
    quiz_taker = models.ForeignKey(QuizTaker, on_delete=models.CASCADE, verbose_name=_('Quiz Taker'),
                                   related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_('Question'),
                                 related_name='users_answers')
    answers = models.ManyToManyField(Answer, blank=True, verbose_name=_('Answers'), related_name='users_answers')

    def __str__(self):
        return self.question.title

    @property
    def answers_string(self):
        return ', '.join([str(answer) for answer in self.answers.all()])

    def clear(self):
        self.answers.clear()


@receiver(pre_save, sender=Quiz)
def slugify_name(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.title)
