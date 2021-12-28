from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse
from polls.models import Poll

User = get_user_model()


class TestPoll(TestCase):
    def setUp(self):
        self.admin = Client()
        self.user = User.objects.create_superuser(
            username='user',
            email='user@mail.ru',
            password='user'
        )
        self.admin.force_login(self.user)
        self.poll_data = {
            'title': 'testtitle',
            'description': 'testdescription',
            'start_date': '2021-12-26',
            'end_date': '2021-12-31'
        }
        self.changed_poll_data = {
            'title': 'change_testtitle',
            'description': 'change_testdescription',
            'end_date': '2021-12-30'
        }
    
    def test_poll_creation(self):
        url = reverse('poll-list')
        response = self.admin.post(url, self.poll_data)
        created_post = Poll.objects.first()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(created_post.title, self.poll_data['title'])
        self.assertEqual(created_post.description,
                         self.poll_data['description'])
        self.assertEqual(str(created_post.start_date),
                         self.poll_data['start_date'])
        self.assertEqual(str(created_post.end_date),
                         self.poll_data['end_date'])

    def test_poll_edit(self):
        url = reverse('poll-detail', kwargs={'pk': 1})
        created_post = Poll.objects.create(
            title=self.poll_data['title'],
            description=self.poll_data['description'],
            start_date=self.poll_data['start_date'],
            end_date=self.poll_data['end_date']
        )
        response = self.admin.patch(url,
                                    self.changed_poll_data,
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(created_post.title,
                            self.changed_poll_data['title'])
        self.assertNotEqual(created_post.description,
                            self.changed_poll_data['description'])
        self.assertNotEqual(created_post.end_date,
                            self.changed_poll_data['end_date'])

    def test_start_date_edit(self):
        url = reverse('poll-detail', kwargs={'pk': 1})
        created_post = Poll.objects.create(
            title=self.poll_data['title'],
            description=self.poll_data['description'],
            start_date=self.poll_data['start_date'],
            end_date=self.poll_data['end_date']
        )
        response = self.admin.patch(url,
                                    {'start_date': '2021-12-27'},
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_end_date_lt_start_date(self):
        url = reverse('poll-list')
        self.poll_data['end_date'] = '2021-12-20'
        response = self.admin.post(url, self.poll_data)
        self.assertEqual(response.status_code, 400)

    def test_poll_delete(self):
        url = reverse('poll-detail', kwargs={'pk': 1})
        created_post = Poll.objects.create(
            title=self.poll_data['title'],
            description=self.poll_data['description'],
            start_date=self.poll_data['start_date'],
            end_date=self.poll_data['end_date']
        )
        response = self.admin.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Poll.objects.count(), 0)

    def test_get_nonexistent_poll(self):
        url = reverse('poll-detail', kwargs={'pk': 222})
        response = self.admin.delete(url)
        self.assertEqual(response.status_code, 404)
    
    def test_unauthorized_client_create(self):
        url = reverse('poll-list')
        unauthorized_client = Client()
        response1 = unauthorized_client.post(url,
                                   self.poll_data,
                                   content_type='application/json')
        response2 = unauthorized_client.get(url)
        self.assertEqual(response1.status_code, 403)
        self.assertEqual(response2.status_code, 403)
