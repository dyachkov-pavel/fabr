from django.core.exceptions import ValidationError
from django.db import models


class Poll(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')

    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ['-id']

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError('Дата окончания не может '
                                  'быть раньше даты начала!')
        if self.end_date == self.start_date:
            raise ValidationError('Выберите следующий день от даты '
                                  'начала опроса, если опрос '
                                  'идёт на протяжении одного дня')


class Question(models.Model):

    QUESTION_TYPE = (
        ('CHOICE', 'CHOICE'),
        ('MULTICHOICE', 'MULTICHOICE'),
        ('TEXT', 'TEXT'),
    )

    poll = models.ForeignKey(Poll,
                             on_delete=models.CASCADE,
                             related_name='poll_questions',
                             verbose_name='Опрос')
    question_text = models.CharField(max_length=256,
                                     verbose_name='Текст вопроса')
    question_type = models.CharField(max_length=15,
                                     choices=QUESTION_TYPE,
                                     default='TEXT',
                                     verbose_name='Тип вопроса')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question_text

    def clean(self):
        if (self.question_type in ['CHOICE', 'MULTICHOICE'] and
                not self.question_choice.exists()):
            raise ValidationError('Создайте хотя бы один вариант ответа')


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 related_name='question_choice',
                                 blank=True,
                                 null=True,
                                 verbose_name='Вопрос')
    choice_text = models.CharField(max_length=256,
                                   blank=True,
                                   verbose_name='Вариант ответа')

    class Meta:
        verbose_name = 'Выбор'
        verbose_name_plural = 'Выборы'

    def __str__(self):
        return self.choice_text

    def clean(self):
        if self.question.question_type not in ['CHOICE', 'MULTICHOICE']:
            raise ValidationError('Нельзя создать вариант ответа '
                                  'для вопроса с типом ответа "TEXT"')


class Answer(models.Model):
    user_id = models.PositiveIntegerField(verbose_name='ID пользователя')
    poll = models.ForeignKey(Poll,
                             on_delete=models.CASCADE,
                             related_name='poll_answer',
                             verbose_name='Опрос')
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 related_name='question_answer',
                                 verbose_name='Вопрос')
    choice = models.ForeignKey(QuestionChoice,
                               on_delete=models.CASCADE,
                               related_name='choice_answer',
                               blank=True,
                               null=True,
                               verbose_name='Выбранный ответ')
    answer_text = models.CharField(max_length=256,
                                   blank=True,
                                   verbose_name='Текст ответа')

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователя'

    def __str__(self):
        return (f'{self.user_id} - {self.question.question_text}:'
                f' {self.answer_text or self.choice}')

    def clean(self):
        if self.choice and self.answer_text:
            raise ValidationError('Ответ состоит либо из предустановленного '
                                  'выбора, либо из своего текста')

        if self.question not in self.poll.poll_questions.all():
            raise ValidationError('Вопрос на который вы ответили '
                                  'не существует в выбранном опросе')

        if (self.question.question_type in ['CHOICE', 'MULTICHOICE'] and
                not self.choice):
            raise ValidationError('На этот вопрос необходимо выбрать ответ')

        if self.question.question_type == 'TEXT' and not self.answer_text:
            raise ValidationError('На этот вопрос необходимо '
                                  'написать свой ответ текстом')

        if (self.choice not in self.question.question_choice.all() and
                self.question.question_choice.all()):
            raise ValidationError('Вы выбрали несуществующий вариант '
                                  'ответа на данный вопрос')

        if (self.question.question_type in ['MULTICHOICE'] and
            Answer.objects.filter(user_id=self.user_id,
                                  question=self.question,
                                  choice=self.choice).exists()):
            raise ValidationError('Вы уже выбрали этот вариант ответа')

        if (self.question.question_type in ['CHOICE', 'TEXT'] and
            Answer.objects.filter(user_id=self.user_id,
                                  question=self.question).exists()):
            raise ValidationError('Вы уже отвечали на этот вопрос')
