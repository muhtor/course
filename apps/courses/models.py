from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from slugify import slugify
from django.db.models import F
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

from ..accounts.models import User
from ..core.models import TimestampedModel


class Status(models.TextChoices):
    NEW = "new"
    PROGRESS = "progress"
    FINISHED = "finished"


class Category(TimestampedModel):
    parent_category = models.ForeignKey(
        'self', related_name='children', on_delete=models.SET_NULL, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    path = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/category', null=True, blank=True)
    sort = models.CharField(max_length=10, blank=True)
    priority = models.SmallIntegerField(
        help_text='the higher the number, the more priority',
        default=0
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-priority', 'id')
        verbose_name_plural = _('       Categories')

    @property
    def image_url(self):
        return f"{self.image.url}" if self.image else None


class CourseBase(TimestampedModel):
    name = models.CharField(max_length=100, verbose_name=_('Course name'))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_('Category'), null=True, blank=True)
    image = models.ImageField(upload_to='images/courses', verbose_name=_('Course Image'))
    description = RichTextUploadingField(verbose_name=_('Description'))

    class Meta:
        abstract = True

    @property
    def image_url(self):
        return f"{self.image.url}" if self.image else None


class Course(CourseBase):
    author = models.CharField(max_length=64)
    old_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=1)
    price = models.DecimalField(default=0.00, max_digits=10, decimal_places=1)
    views = models.PositiveIntegerField(default=0)
    person_count = models.PositiveIntegerField(default=0)
    permission = models.BooleanField(default=True)
    certificate = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    priority = models.SmallIntegerField(
        help_text='the higher the number, the more priority',
        default=0
    )

    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('     Courses')
        ordering = ('-priority', 'id')

    def __str__(self):
        return self.name

    def is_completed(self, user: User):
        last_course_topic = self.topic_courses.last()
        if last_course_topic.quiz:
            return user.quiz_takers.filter(quiz=last_course_topic.quiz, completed=True).exists()
        return user.lessons.filter(lesson=last_course_topic.lessons.last(), status=Status.FINISHED)

    @property
    def viewed_count(self):
        Course.objects.filter(pk=self.pk).update(views=F('views') + 1)
        return self.views + 1

    @property
    def lessons_count(self):
        return sum([topic.lessons.count() for topic in self.topic_courses.prefetch_related('lessons')])

    @property
    def topics_list(self):
        return self.topic_courses.all()

    @property
    def lessons_list(self):
        lessons = []
        for topic in self.topic_courses.prefetch_related('lessons'):
            lessons += [lesson for lesson in topic.lessons.all()]
        return lessons

    def get_status(self, user: User):
        try:
            if CourseCertificate.objects.filter(user=user, course=self).exists():
                return Status.FINISHED
            elif user.profile.is_course_paid(self):
                return Status.PROGRESS
        except:
            pass
        return Status.NEW


class UploadFile(TimestampedModel):
    file = models.FileField(upload_to='files/courses/lessons/audios', null=True, blank=True)

    def __str__(self):
        return f"Audio-ID {self.id}"


class CertificatedCourse(CourseBase):
    """Group of courses"""
    sub_courses = models.ManyToManyField(Course, verbose_name=_('Sub courses'), related_name='certificated_courses')
    discount_percent = models.SmallIntegerField(
        'Discount price percent',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
        help_text='The certificated course price is the sub courses price '
                  'with the discount percent. Works if a user did not paid for'
                  ' any of the sub courses'
    )

    class Meta:
        verbose_name = _('Certificated course')
        verbose_name_plural = _('Certificated courses')

    def __str__(self):
        return self.name

    @property
    def old_price(self):
        return sum([course.old_price for course in self.sub_courses.all()])

    @property
    def price(self):
        price = self.sub_courses_price
        if self.discount_percent > 0:
            price -= (price * self.discount_percent / 100)
        return price

    @property
    def sub_courses_price(self):
        return sum([course.price for course in self.sub_courses.all()])

    def get_price_for_user(self, user: User):
        """If user bought a sub course, return price of the unpaid courses"""
        courses, paid_exists = self.get_unpaid_courses(user)
        if paid_exists:
            if courses:
                return sum([course.price for course in courses])
        return self.price

    def get_unpaid_courses(self, user: User) -> tuple:
        """:return (unpaid_courses, paid_course_exists)"""
        paid_courses_id = []
        for course in self.sub_courses.all():
            if course.get_status(user) != Status.NEW:
                paid_courses_id.append(course.id)

        if paid_courses_id:
            return self.sub_courses.exclude(id__in=paid_courses_id), True
        return self.sub_courses.all(), False

    @property
    def lessons_count(self):
        return sum([course.lessons_count for course in self.sub_courses.all()])

    @property
    def sub_courses_count(self):
        return self.sub_courses.count()

    def is_completed(self, user: User):
        """If certificated course completed by the user"""
        completed_courses_in_certificated_course = 0
        for sub_course in self.sub_courses.all():
            if sub_course.is_completed(user=user):
                completed_courses_in_certificated_course += 1

            if completed_courses_in_certificated_course == self.sub_courses.count():
                return True

    def get_status(self, user: User):
        try:
            if CourseCertificate.objects.filter(user=user, certificated_course=self).exists():
                return Status.FINISHED
            for course in self.sub_courses.all():
                if user.profile.is_course_paid(course=course):
                    return Status.PROGRESS
        except:
            pass
        return Status.NEW


class CourseCertificate(models.Model):
    """Certificate for course completing"""
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.DO_NOTHING, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='certificates', blank=True, null=True)
    hash = models.CharField(_('Hash for verify'), max_length=150, blank=True, null=True)
    certificated_course = models.ForeignKey(CertificatedCourse, on_delete=models.DO_NOTHING,
                                            related_name='certificates', blank=True, null=True)
    pdf = models.FileField(upload_to='files/courses/certificates/', verbose_name=_('PDF file'), blank=True, null=True)
    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    qr = models.ImageField(upload_to='images/courses/certificates/',
                           verbose_name=_('QR code (link to the certificate)'), blank=True, null=True)

    class Meta:
        verbose_name = _('Course certificate')
        verbose_name_plural = _('Courses certificates')
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.phone} - {self.certificated_object.name}'

    def save(self, *args, **kwargs):
        if (not self.course and not self.certificated_course) or (self.course and self.certificated_course):
            raise ValidationError('Course or certificated course must be defined only')
        super().save(*args, **kwargs)

    @property
    def certificated_object(self):
        """If the course defined, return it, else return the certificated course"""
        if self.course:
            return self.course
        return self.certificated_course


class Topic(TimestampedModel):
    course = models.ForeignKey(Course, verbose_name=_('Course'), on_delete=models.CASCADE, related_name='topic_courses')
    name = models.CharField(max_length=100, verbose_name=_('Topic name'))

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('    Topics')
        ordering = ['id']

    def __str__(self):
        return self.name

    def get_index_in_course_topics(self):
        """Returns the topic index (position) in list of all the course topics"""
        return list(self.course.topics_list).index(self)

    @property
    def previous_topic(self):
        topic_index = self.get_index_in_course_topics()
        if topic_index == 0:
            raise IndexError('Previous lesson doesnt exist')
        return self.course.topics_list[topic_index - 1]


class UserLesson(models.Model):
    """User lesson. Needs for completing a course step-by-step and show the lessons status"""
    user = models.ForeignKey(User, related_name='lessons', on_delete=models.CASCADE)
    lesson = models.ForeignKey('Lesson', related_name='users_lessons', on_delete=models.CASCADE)
    status = models.CharField(
        _('Process status'), max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        verbose_name = _('User lesson')
        verbose_name_plural = _('User lessons')

    def __str__(self):
        return f'#{self.id} | {self.user.get_full_name()} - {self.lesson.name}'

    def get_lesson_course(self):
        return self.lesson.course


class Lesson(TimestampedModel):
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'), on_delete=models.PROTECT, related_name='lessons')
    name = models.CharField(max_length=255, verbose_name=_('Lesson Name'))
    description = RichTextUploadingField(verbose_name=_('Lesson Description'))

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['id']

    def __str__(self):
        return self.name

    def get_process_status(self, user: User):
        try:
            return user.lessons.get(lesson=self).status
        except UserLesson.DoesNotExist:
            return Status.NEW

    def get_index_in_course_lessons(self):
        """Returns the lesson index (position) in list of all the course lessons"""
        return self.course.lessons_list.index(self)

    @property
    def previous_lesson(self):
        lesson_index = self.get_index_in_course_lessons()
        if lesson_index == 0:
            raise IndexError('Previous lesson doesnt exist')
        return self.course.lessons_list[lesson_index - 1]

    def is_blocked(self, user: User = None) -> bool:
        """Is lesson blocked for given user"""
        try:
            previous_lesson_id = self.previous_lesson.id
        except IndexError:
            return False  # If the lesson is first, it's not blocked

        # Check if the previous quiz was passed
        try:
            if not user.is_authenticated or not self.topic.previous_topic.quiz.is_completed(user):
                return True
        except (IndexError, Topic.quiz.RelatedObjectDoesNotExist):
            pass

        # Check if the course was paid (But first and second lessons are free)
        if not user.profile.is_course_paid(course=self.course):
            return True

        # Check if the previous lesson was completed
        return not user.lessons.filter(lesson__id=previous_lesson_id, status=Status.FINISHED).exists()

    def is_lesson_finished(self, user: User) -> bool:
        """Check if there lesson is finished by a user"""
        try:
            return UserLesson.objects.filter(user=user, lesson=self, status=Status.FINISHED).exists()
        except:
            return False

    @property
    def course(self):
        return self.topic.course


class UserCourse(TimestampedModel):
    user = models.ForeignKey(User, related_name='courses', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='user_courses', on_delete=models.CASCADE)
    status = models.CharField(_('Process status'), max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        verbose_name = _('User Course')
        verbose_name_plural = _('User Courses')

    def __str__(self):
        return f'#{self.id} | {self.user.get_full_name()} - {self.course.name}'


def pre_save_parent_category(sender, instance, **kwargs):
    instance.path = instance.title
    parent_category_obj = instance.parent_category
    while parent_category_obj is not None:
        instance.path = parent_category_obj.title + " > " + instance.path
        parent_category_obj = parent_category_obj.parent_category
pre_save.connect(pre_save_parent_category, sender=Category)
