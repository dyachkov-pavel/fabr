import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse
from polls.models import Answer, Poll, Question, QuestionChoice

User = get_user_model()


class TestUser(TestCase):
    def setUp(self):
        self.unauthorized_client = Client()
        self.poll = Poll.objects.create(
            title='testtitle',
            description='testdescription',
            start_date='2021-12-26',
            end_date='2022-12-31'
        )
        self.question1 = Question.objects.create(
            poll=self.poll,
            question_text='Write your name',
            question_type='TEXT'
        )
        self.question2 = Question.objects.create(
            poll=self.poll,
            question_text='Choose something',
            question_type='CHOICE',
        )
        self.choice1 = QuestionChoice.objects.create(
            question=self.question2,
            choice_text='First choice'
        )
        self.choice2 = QuestionChoice.objects.create(
            question=self.question2,
            choice_text='Second choice'
        )
        self.text_answer_data = {
            "user_id": 1,
            "question": 1,
            "answer_text": "My name is Paul"
        }
        self.choice_answer_data = {
            "user_id": 1,
            "question": 2,
            "choice": 1,
        }

    def test_poll_list(self):
        url = reverse('poll_view')
        response = self.unauthorized_client.get(url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0].get('poll_id'), self.poll.id)
        self.assertEqual(data[0].get('title'), self.poll.title)
        self.assertEqual(data[0].get('description'), self.poll.description)
        self.assertEqual(data[0].get('start_date'), self.poll.start_date)
        self.assertEqual(data[0].get('end_date'), self.poll.end_date)

    def test_poll_detailed_list(self):
        url = reverse('poll_detail_view', kwargs={'pk': 1})
        response = self.unauthorized_client.get(url)
        data = json.loads(response.content)
        choices = len(data.get('poll_questions')[1].get('question_choice'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data.get('poll_questions', 0)),
                         Question.objects.count())
        self.assertEqual(len(data.get('poll_questions', 0)),
                         Question.objects.count())
        self.assertEqual(data.get('poll_questions')[0].get('question_id'),
                         self.question1.id)
        self.assertEqual(choices, QuestionChoice.objects.count())

    def test_get_nonexistent_poll(self):
        url = reverse('poll_detail_view', kwargs={'pk': 222})
        response = self.unauthorized_client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_answer(self):
        url = reverse('create_answer_view', kwargs={'poll_id': 1})
        response1 = self.unauthorized_client.post(
            url,
            self.text_answer_data,
            content_type='application/json'
        )
        response2 = self.unauthorized_client.post(
            url,
            self.choice_answer_data,
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 201)
        self.assertEqual(Answer.objects.count(), 2)

    def test_answer_list(self):
        url = reverse('user_answer_view', kwargs={'user_id': 1})
        text_answer = Answer.objects.create(
            poll=self.poll,
            user_id=1,
            question=self.question1,
            answer_text="My name is Paul"
        )
        choice_answer = Answer.objects.create(
            poll=self.poll,
            user_id=1,
            question=self.question2,
            choice=self.choice1
        )
        # ответ другого пользователя не должен отобразиться на странице
        different_user_answer = Answer.objects.create(
            poll=self.poll,
            user_id=2,
            question=self.question2,
            choice=self.choice1
        )
        response = self.unauthorized_client.get(url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data[0].get('user_answers')), 2)

    def test_choice_answer_for_text_type(self):
        url = reverse('create_answer_view', kwargs={'poll_id': 1})
        self.text_answer_data['choice'] = 1
        # запрос на создание с текстом и выбором
        response1 = self.unauthorized_client.post(
            url,
            self.text_answer_data,
            content_type='application/json'
        )
        data = json.loads(response1.content)
        self.assertEqual(data.get('non_field_errors')[0],
                         'Ответ состоит либо из предустановленного '
                         'выбора, либо из своего текста')
        self.assertEqual(response1.status_code, 400)
        self.assertEqual(Answer.objects.count(), 0)
        self.text_answer_data.pop('answer_text')
        # запрос на создание только с выбором
        response2 = self.unauthorized_client.post(
            url,
            self.text_answer_data,
            content_type='application/json'
        )
        data = json.loads(response2.content)
        self.assertEqual(data.get('non_field_errors')[0],
                         'На этот вопрос необходимо '
                         'написать свой ответ текстом')
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(Answer.objects.count(), 0)

    def test_text_answer_for_choice_type(self):
        url = reverse('create_answer_view', kwargs={'poll_id': 1})
        self.choice_answer_data['answer_text'] = "bla-bla-bla"
        self.choice_answer_data.pop('choice')
        response = self.unauthorized_client.post(
            url,
            self.choice_answer_data,
            content_type='application/json'
        )
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data.get('non_field_errors')[0],
                         'На этот вопрос необходимо выбрать ответ')
        self.assertEqual(Answer.objects.count(), 0)

    def test_create_second_answer_to_question(self):
        url = reverse('create_answer_view', kwargs={'poll_id': 1})
        response1 = self.unauthorized_client.post(
            url,
            self.text_answer_data,
            content_type='application/json'
        )
        response2 = self.unauthorized_client.post(
            url,
            self.text_answer_data,
            content_type='application/json'
        )
        data = json.loads(response2.content)
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(Answer.objects.count(), 1)
        self.assertEqual(data.get('non_field_errors')[0],
                         'Вы уже отвечали на этот вопрос')
