import nested_admin
from django.contrib import admin

from .models import Answer, Poll, Question, QuestionChoice


class QuestionChoiceInLine(nested_admin.NestedStackedInline):
    model = QuestionChoice
    extra = 0


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    extra = 0
    inlines = [QuestionChoiceInLine]


class PollAdmin(nested_admin.NestedModelAdmin):
    list_display = ('id', 'title', 'description', 'start_date', 'end_date',)
    search_fields = ('id', 'title', 'description', 'start_date', 'end_date')
    list_filter = ('id', 'title', 'description', 'start_date', 'end_date')
    inlines = [QuestionInline]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if obj:  # если редактируем, то начало опроса нельзя изменить
            readonly_fields = tuple(readonly_fields) + ('start_date', )
        return readonly_fields


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'poll', 'question', 'choice', 'answer_text')
    search_fields = ('user_id', 'poll', 'question', 'choice', 'answer_text')
    list_filter = ('user_id', 'poll', 'question', 'choice', 'answer_text')


admin.site.register(Poll, PollAdmin)
admin.site.register(Answer, AnswerAdmin)
