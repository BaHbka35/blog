from django.test import TestCase, SimpleTestCase
from .models import Topic, Entry
from django.contrib.auth.models import User
from django.test.client import Client
from django.urls import reverse


class SimpleTests(SimpleTestCase):

    def test_index_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class TopicModelTest(TestCase):

    def setUp(self):
        topic = Topic.objects.create(name="Topic_1")
        topic.save()

    def test_topic(self):
        topic = Topic.objects.get(id=1)
        topic_name = f"{topic.name}"
        self.assertEqual(topic_name, "Topic_1")


class EntryModelTest(TestCase):

    def setUp(self):
        topic = Topic.objects.create(name="Topic_1")
        topic.save()
        author = User.objects.create_user(username="User_1", password="1")
        author.save()
        entry = Entry.objects.create(
            topic=topic,
            author=author,
            title="Entry_1_title",
            text="Entry_1_text",
            )
        entry.save()

    def test_text_content(self):
        entry = Entry.objects.get(id=1)
        content = {"topic": entry.topic, "title": entry.title, "text": entry.text, "author": entry.author}
        needed = content = {"topic": 1, "title": "Entry_1_title", "text": "Entry_1_text", "author": 1}
        self.assertEqual(content, needed)


class TopicsListPage(TestCase):

    def setUp(self):

        self.client = Client()
        self.user = User.objects.create_user(username="User_1", password="1")
        self.user.save()


    def test_topics_list_login_required(self):
        # If user isn't logined, return 302
        res = self.client.get(reverse("social_networks:topics_list"))
        self.assertEqual(res.status_code, 302)

    def test_view_uses_correct_template(self):
        self.client.login(username="User_1", password="1")
        res = self.client.get(reverse("social_networks:topics_list"))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "social_networks/topics_list.html")
