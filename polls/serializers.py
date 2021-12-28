from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Answer, Poll, Question, QuestionChoice


class PollSerializer(serializers.ModelSerializer):

    poll_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Poll
        fields = ['poll_id', 'title', 'description',
                  'start_date', 'end_date']

    def validate_start_date(self, value):
        if self.instance:
            if self.instance.start_date != value:
                raise serializers.ValidationError(
                    'Нельзя изменять дату начала опроса'
                )
        return value

    def validate_end_date(self, value):
        if self.instance:
            if self.instance.start_date > value:
                raise serializers.ValidationError(
                    'Дата окончания не может '
                    'быть раньше даты начала!'
                )
        return value

    def validate(self, data):
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError(
                    'Дата окончания не может '
                    'быть раньше даты начала!'
                )
        return data


class QuestionChoiceSerializer(serializers.ModelSerializer):

    choice_id = serializers.IntegerField(source='id',
                                         read_only=True)

    class Meta:
        model = QuestionChoice
        fields = ['choice_id', 'choice_text']


class QuestionSerializer(serializers.ModelSerializer):

    question_id = serializers.IntegerField(source='id',
                                           read_only=True)
    question_choice = QuestionChoiceSerializer(many=True)
    poll = serializers.HiddenField(default=None)

    class Meta:
        model = Question
        fields = ['question_id', 'poll', 'question_text',
                  'question_type', 'question_choice']

    def create(self, validated_data):
        question_choices = validated_data.pop('question_choice')
        question = Question.objects.create(**validated_data)
        if question.question_type in ['CHOICE', 'MULTICHOICE']:
            for choice in question_choices:
                choice = QuestionChoice.objects.create(
                    question=question,
                    choice_text=choice['choice_text']
                )
        return question

    def update(self, instance, validated_data):
        instance.question_text = validated_data.get(
            'question_text', instance.question_text
        )
        instance.question_type = validated_data.get(
            'question_type', instance.question_type
        )
        question_choice = instance.question_choice
        instance.save()
        if (instance.question_type in ['CHOICE', 'MULTICHOICE'] and
                not validated_data.get('question_choice')):
            raise serializers.ValidationError(
                'Создайте хотя бы один вариант ответа'
            )
        if (validated_data.get('question_choice') and
                instance.question_type in ['TEXT']):
            raise serializers.ValidationError(
                'Нельзя создать вариант ответа для '
                'вопроса с типом ответа "TEXT"!'
            )
        question_choice.all().delete()
        if instance.question_type in ['CHOICE', 'MULTICHOICE']:
            question_choices = validated_data.pop('question_choice')
            for choice in question_choices:
                choice = QuestionChoice.objects.create(
                    question=instance,
                    choice_text=choice['choice_text']
                )
        return instance

    def validate(self, data):
        if (data.get('question_type') in ['TEXT'] and
                data.get('question_choice')):
            raise serializers.ValidationError(
                'Нельзя создать вариант ответа для '
                'вопроса с типом ответа "TEXT"!'
            )
        if (data.get('question_type') in ['CHOICE', 'MULTICHOICE'] and
                not data.get('question_choice')):
            raise serializers.ValidationError(
                'Создайте хотя бы один вариант ответа'
            )
        return data


class PollDetailSerializer(serializers.ModelSerializer):

    poll_id = serializers.IntegerField(source='id')
    poll_questions = QuestionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ['poll_id', 'title', 'description',
                  'start_date', 'end_date', 'poll_questions']


class AnswerSerializer(serializers.ModelSerializer):

    answer_id = serializers.IntegerField(source='id',
                                         read_only=True)

    class Meta:
        model = Answer
        fields = ['answer_id', 'user_id', 'question',
                  'choice', 'answer_text']

    def validate(self, data):
        poll_id = self.context['poll_id']
        question = data['question']
        poll = get_object_or_404(Poll, id=poll_id)
        if question not in poll.poll_questions.all():
            raise serializers.ValidationError(
                'Вопрос с таким id не существует в этом опросе'
            )

        if data.get('choice') and data.get('answer_text'):
            raise serializers.ValidationError(
                'Ответ состоит либо из предустановленного '
                'выбора, либо из своего текста'
            )

        if (question.question_type in ['CHOICE', 'MULTICHOICE'] and
                not data.get('choice')):
            raise serializers.ValidationError(
                'На этот вопрос необходимо выбрать ответ'
            )

        if question.question_type == 'TEXT' and not data.get('answer_text'):
            raise serializers.ValidationError(
                'На этот вопрос необходимо написать свой ответ текстом'
            )

        if (data.get('choice') not in question.question_choice.all() and
                question.question_choice.all()):
            raise serializers.ValidationError(
                'Вы выбрали несуществующий вариант '
                'ответа на данный вопрос'
            )

        if (question.question_type in ['MULTICHOICE'] and
            Answer.objects.filter(user_id=data['user_id'],
                                  question=question,
                                  choice=data.get('choice')).exists()):
            raise serializers.ValidationError(
                'Вы уже выбрали этот вариант ответа'
            )

        if (question.question_type in ['CHOICE', 'TEXT'] and
            Answer.objects.filter(user_id=data['user_id'],
                                  question=question).exists()):
            raise serializers.ValidationError(
                'Вы уже отвечали на этот вопрос'
            )

        return data
