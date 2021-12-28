import datetime as dt

from rest_framework import generics, mixins, permissions, views, viewsets
from rest_framework.response import Response

from .models import Answer, Poll, Question
from .serializers import (AnswerSerializer, PollDetailSerializer,
                          PollSerializer, QuestionSerializer)


class PollView(generics.ListAPIView):
    """
    Список активных опросов
    """
    serializer_class = PollSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Poll.objects.all()

    def get_queryset(self):
        queryset = self.queryset.filter(end_date__gte=dt.date.today())
        return queryset


class PollRetrieveView(generics.RetrieveAPIView):
    """
    Детальный опрос
    """
    serializer_class = PollDetailSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Poll.objects.all()


class PollCreateUpdateDestroyView(mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  mixins.DestroyModelMixin,
                                  viewsets.GenericViewSet):
    """
    Создать, обновить, удалить опрос (админ)
    """
    serializer_class = PollSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Poll.objects.all()


class QuestionCreateUpdateDestroyView(mixins.CreateModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin,
                                      viewsets.GenericViewSet):
    """
    Создать, обновить, удалить вопрос (админ)
    """
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Question.objects.all()

    def perform_create(self, serializer):
        serializer.save(poll_id=self.kwargs['poll_id'])


class CreateAnswerView(generics.CreateAPIView):
    """
    Создать ответ на вопрос
    """
    serializer_class = AnswerSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Answer.objects.all()

    def get_serializer_context(self):
        return {'poll_id': self.kwargs['poll_id']}

    def perform_create(self, serializer):
        poll_id = self.kwargs['poll_id']
        serializer.save(poll_id=poll_id)


class UserAnswerView(views.APIView):
    """
    Ответы конкретного пользователя
    """

    def get(self, requset, user_id):
        result = []
        poll_queryset = Poll.objects.filter(
            id__in=Answer.objects.filter(user_id=user_id).values('poll'))
        for poll in poll_queryset:
            poll_info = {'poll_id': poll.id,
                         'poll_title': poll.title,
                         'poll_description': poll.description,
                         'user_answers': []}
            for answer in Answer.objects.filter(user_id=user_id, poll=poll.id):
                question_type = answer.question.question_type
                question_text = answer.question.question_text
                question_answer = {'question_id': answer.question_id,
                                   'question_type': question_type,
                                   'question_text': question_text, }
                if answer.question.question_type in ['TEXT']:
                    question_answer['answer_text'] = answer.answer_text
                    question_answer['choice'] = ""
                if answer.question.question_type in ['CHOICE', 'MULTICHOICE']:
                    question_answer['answer_text'] = ""
                    question_answer['choice'] = answer.choice.choice_text
                poll_info['user_answers'].append(question_answer)
            result.append(poll_info)
        return Response(result)
