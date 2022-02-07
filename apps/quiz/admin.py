from django.contrib import admin
from .models import Quiz, Question, Answer, QuizTaker, UsersAnswer
import nested_admin


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'quiz', 'technique', 'type_of_test', 'is_active', 'date_created')
    search_fields = ('title',  'quiz__title')
    autocomplete_fields = ('quiz', )
    list_filter = ('date_created', 'is_active')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'question', 'is_correct')
    search_fields = ('question__title', 'title')
    list_filter = ('is_correct', )
    autocomplete_fields = ('question', )


class UsersAnswerAdmin(admin.ModelAdmin):
    list_display = ('quiz_taker', 'id', 'question')
    search_fields = ('quiz_taker__user__name', 'question__title')


class AnswerInline(nested_admin.NestedTabularInline):
    model = Answer
    extra = 0


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [AnswerInline, ]
    extra = 0


class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline, ]
    extra = 0
    list_display = ('title', 'id', 'topic', 'date_created')
    prepopulated_fields = {'slug': ('title',), }
    search_fields = ('title', 'topic__name')


class UsersAnswerInline(admin.TabularInline):
    model = UsersAnswer
    extra = 0


class QuizTakerAdmin(admin.ModelAdmin):
    inlines = [UsersAnswerInline, ]
    list_display = ('user', 'id', 'quiz', 'score', 'completed', 'date_created')
    search_fields = ('user__name', 'quiz__title')
    list_filter = ('completed', 'date_created')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(QuizTaker, QuizTakerAdmin)
admin.site.register(UsersAnswer, UsersAnswerAdmin)
