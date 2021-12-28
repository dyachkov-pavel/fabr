from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls.base import reverse
from polls.models import Poll, Question, QuestionChoice

User = get_user_model()


class TestQuestion(TestCase):
    def setUp(self):
        self.admin = Client()
        self.user = User.objects.create_superuser(
            username='user',
            email='user@mail.ru',
            password='user'
        )
        self.admin.force_login(self.user)
        self.poll = Poll.objects.create(
            title='testtitle',
            description='testdescription',
            start_date='2021-12-26',
            end_date='2021-12-31'
        )
        self.text_question_data = {
            'question_text': 'Как дела?',
            'question_type': 'TEXT',
            'question_choice': []
        }
        self.choice_question_data = {
            'question_text': 'Как дела?',
            'question_type': 'CHOICE',
            'question_choice': [{
                "choice_text": "Хорошо"
            },
                {
                "choice_text": "Плохо"
            },
                {
                "choice_text": "Не знаю"
            }]
        }
        self.multichoice_question_data = {
            'question_text': 'Как дела?',
            'question_type': 'MULTICHOICE',
            'question_choice': [{
                "choice_text": "Плохо"
            },
                {
                "choice_text": "Хорошо"
            },
                {
                "choice_text": "Не знаю"
            }]
        }

    def test_text_question_creation(self):
        url = reverse('question-list', kwargs={'poll_id': 1})
        response = self.admin.post(url,
                                   self.text_question_data,
                                   content_type='application/json')
        created_question = Question.objects.first()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(created_question.question_text,
                         self.text_question_data['question_text'])
        self.assertEqual(created_question.question_type,
                         self.text_question_data['question_type'])
        self.assertEqual(created_question.question_choice.count(), 0)

    def test_choice_question_creation(self):
        url = reverse('question-list', kwargs={'poll_id': 1})
        response = self.admin.post(url,
                                   self.choice_question_data,
                                   content_type='application/json')
        created_question = Question.objects.first()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(created_question.question_text,
                         self.choice_question_data['question_text'])
        self.assertEqual(created_question.question_type,
                         self.choice_question_data['question_type'])
        self.assertEqual(created_question.question_choice.count(), 3)
        self.assertEqual(created_question.question_choice.first().choice_text,
                         "Хорошо")

    def test_multichoice_question_creation(self):
        url = reverse('question-list', kwargs={'poll_id': 1})
        response = self.admin.post(url,
                                   self.multichoice_question_data,
                                   content_type='application/json')
        created_question = Question.objects.first()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(created_question.question_text,
                         self.multichoice_question_data['question_text'])
        self.assertEqual(created_question.question_type,
                         self.multichoice_question_data['question_type'])
        self.assertEqual(created_question.question_choice.count(), 3)
        self.assertEqual(created_question.question_choice.first().choice_text,
                         "Плохо")

    def test_text_question_choice_creation(self):
        url = reverse('question-list', kwargs={'poll_id': 1})
        self.text_question_data['question_choice'] = {
            "choice_text": "Выбор для текстового вопроса"
        }
        response = self.admin.post(url,
                                   self.text_question_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Question.objects.count(), 0)

    def test_choice_question_without_choices_creation(self):
        url = reverse('question-list', kwargs={'poll_id': 1})
        self.choice_question_data['question_choice'] = []
        response = self.admin.post(url,
                                   self.choice_question_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Question.objects.count(), 0)

    def test_question_edit(self):
        url = reverse('question-detail', kwargs={'poll_id': 1,
                                                 'pk': 1})
        prev_text = 'Prev Text'
        created_question = Question.objects.create(
            poll=self.poll,
            question_text=prev_text,
            question_type='TEXT'
        )
        new_text = {'question_text': 'New text'}
        response = self.admin.patch(url,
                                    new_text,
                                    content_type='application/json')
        q = get_object_or_404(Question,
                              question_text=new_text['question_text'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 1)
        self.assertNotEqual(prev_text, q.question_text)

    def test_question_edit_choice(self):
        url = reverse('question-detail', kwargs={'poll_id': 1,
                                                 'pk': 1})
        prev_choice = 'choice_number1'
        created_question = Question.objects.create(
            poll=self.poll,
            question_text='BLABLA',
            question_type='CHOICE',
        )
        choice = QuestionChoice.objects.create(
            question=created_question,
            choice_text=prev_choice
        )
        response = self.admin.put(url,
                                  self.choice_question_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuestionChoice.objects.count(), 3)
        self.assertEqual(QuestionChoice.objects.first().choice_text, 'Хорошо')

    def test_question_delete(self):
        url = reverse('question-detail', kwargs={'poll_id': 1,
                                                 'pk': 1})
        created_question = Question.objects.create(
            poll=self.poll,
            question_text='BLABLA',
            question_type='TEXT',
        )
        response = self.admin.delete(url)
        self.assertEqual((response.status_code), 204)
        self.assertEqual(Question.objects.count(), 0)

    def test_delete_nonexistent_question(self):
        url = reverse('question-detail', kwargs={'poll_id': 1,
                                                 'pk': 1})
        response = self.admin.delete(url)
        self.assertEqual((response.status_code), 404)
        self.assertEqual(Question.objects.count(), 0)

    def test_unauthorized_client_create(self):
        url = reverse('question-list', kwargs={'poll_id': 1})
        unauthorized_client = Client()
        response1 = unauthorized_client.post(
            url,
            self.choice_question_data,
            content_type='application/json'
        )
        response2 = unauthorized_client.get(url)
        self.assertEqual(response1.status_code, 403)
        self.assertEqual(response2.status_code, 403)
