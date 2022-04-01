import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.urls import reverse

from .models import Forum, Comment, Voter, User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.test import Client
from urllib.parse import urlencode


class ForumTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(name="Sample User", biri="123456")

        Forum.objects.create(title="Test Forum Two", text="Sample Text One", latitude=-53.3, longitude=-8, user=user)
        forum = Forum.objects.create(title="Test Forum One", text="Sample Text Two", latitude=-53.00, longitude=-7.9,
                                     user=user)

        Comment.objects.create(text="Comment Text", forum=forum)
        Voter.objects.create(forum=forum, user=user, score=0)

    def test_get_forum(self):
        forum = Forum.objects.filter(location__distance_lt=(Point(-7.9, 53.4), Distance(km=10))).first()
        self.assertEqual(forum.text, "Sample Text One")

    def test_get_forums_local(self):
        forum = Forum.objects.filter(location__distance_lt=(Point(-7.9, 53.4), Distance(km=10)))
        self.assertEqual(forum.__len__(), 2)

    def test_get_score(self):
        forum = Forum.objects.get(id=1)
        score = forum.get_score()
        self.assertEqual(score, 0)

    def test_get_user_forum(self):
        forum = Forum.objects.get(id=1)
        user = forum.get_user()
        self.assertEqual(user.name, "Sample User")

    def test_published_recent(self):
        forum = Forum.objects.get(id=1)
        self.assertEqual(forum.was_published_recently(), 1)

    def test_delete(self):
        forum = Forum.objects.get(id=1)
        forum.delete_user()
        self.assertEqual(forum.user, None)

    def test_delete_text(self):
        forum = Forum.objects.get(id=1)
        forum.delete_user()
        self.assertEqual(forum.text, "Sample Text One")


class VoterTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(name="Sample User", biri="123456")
        forum = Forum.objects.create(title="Test Forum One", text="Sample Text", latitude=-53.00, longitude=-7.9,
                                     user=user)
        Voter.objects.create(forum_voted=forum, user=user, score=0)

    def test_get_voter(self):
        voter_record = Voter.objects.get(forum_voted_id=1, user_id=1)
        self.assertEqual(voter_record.score, 0)

    def test_vote_upvote(self):
        voter_record = Voter.objects.get(forum_voted_id=1, user_id=1)
        voter_record.up_vote()
        self.assertEqual(voter_record.score, 1)

    def test_vote_down_vote(self):
        voter_record = Voter.objects.get(forum_voted_id=1, user_id=1)
        voter_record.down_vote()
        self.assertEqual(voter_record.score, -1)


class CommentTestCase(TestCase):
    def setUp(self):
        forum = Forum.objects.create(title="Test Forum Two", text="Sample Text One", latitude=-53.3, longitude=-8)
        Comment.objects.create(text="Comment Text", forum=forum)

    def test_get_comment(self):
        forum = Forum.objects.get(id=1)
        comments = forum.comment_set
        self.assertEqual(comments.first().text, 'Comment Text')

    def test_delete(self):
        comment = Comment.objects.get(id=1)
        comment.delete()
        self.assertEqual(comment.user, None)

    def test_delete_text(self):
        comment = Comment.objects.get(id=1)
        comment.delete_user()
        self.assertEqual(comment.text, "Deleted")


class VoterManagerTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(name="Sample User", biri="123456")
        forum = Forum.objects.create(title="Test Forum One", text="Sample Text", latitude=-53.00, longitude=-7.9,
                                     user=user)
        Voter.objects.create(forum_voted=forum, user=user, score=1)

    def test_get_forum(self):
        voter_record = Voter.objects.get(forum_voted_id=1, user_id=1)
        forum = Voter.voted.get_forum(voter_record)
        self.assertEqual(forum.title, "Test Forum One")

    def test_get_previously_voted(self):
        user = User.objects.get(id=1)
        forums = Voter.voted.get_previously_voted(user)
        self.assertEqual(forums[0].title, "Test Forum One")


class UserTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(name="Sample User", biri="123456")
        forum = Forum.objects.create(title="Test Forum One", text="Sample Text", latitude=-53.00, longitude=-7.9,
                                     user=user)
        Comment.objects.create(text="Sample Text", forum=forum)
        Voter.objects.create(forum=forum, user=user, score=0)

    def test_get_user(self):
        user = User.objects.get(biri=123456)
        self.assertEqual(user.name, "Sample User")

    def test_save_name(self):
        user = User.objects.create(biri="654321")
        self.assertNotEqual(user.name, "U654321")

    def test_scramble_name(self):
        user = User.objects.get(biri=123456)
        self.assertEqual(user.name, "Sample User")


class AgeTestCase(TestCase):
    # Boundary Value Analysis
    # < 1 second, now
    # 1 - 59 seconds, minutes
    # 1 - 11 months
    # 1 -> max_years

    def setUp(self):
        Forum.objects.create(title="Test Forum Two", text="Sample Text One", latitude=-53.3, longitude=-8)

    def test_get_age_now(self):
        forum = Forum.objects.get(id=1)
        self.assertEqual(forum.get_age(), "now")

    def test_get_age_minutes(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(minutes=1)
        self.assertEqual(forum.get_age(), "1m ago")

    def test_get_age_hours(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(minutes=60)
        self.assertEqual(forum.get_age(), "1h ago")

    def test_get_age_seconds(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(seconds=55)
        self.assertEqual(forum.get_age(), "55s ago")

    def test_get_age_days(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(days=1)
        self.assertEqual(forum.get_age(), "1 day ago")

    def test_get_age_days_greater(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(days=2)
        self.assertEqual(forum.get_age(), "2 days ago")

    def test_get_age_year(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(days=365)
        self.assertEqual(forum.get_age(), "1 year ago")

    def test_get_age_year_greater(self):
        forum = Forum.objects.get(id=1)
        forum.pub_date = forum.pub_date - datetime.timedelta(days=730)
        self.assertEqual(forum.get_age(), "2 years ago")


class ClientForumTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(name="Sample User", biri="123456")
        User.objects.create(name="Sample User Two", biri="1234567")
        Forum.objects.create(title="Test Forum Two", text="Sample Text One", latitude=-53.3, longitude=-8, user=user)

    # FORUM HTTP REQUESTS GET, DELETE, POST

    def test_post_forum(self):
        c = Client()
        data = urlencode({'title': 'Title One', 'text': 'Sample Text', 'latitude': 9, 'longitude': 9,
                          'biri_key': 12345, "name": "Username 1"})
        response = c.post(reverse('Forum:forum'), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)

    def test_get_forum(self):
        c = Client()
        response = c.get(reverse('Forum:forum'))
        self.assertEqual(response.status_code, 200)

    def test_get_forum_detail_exists(self):
        c = Client()
        response = c.get(reverse('Forum:forum_detail', args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_get_forum_detail_not_exists(self):
        c = Client()
        response = c.get(reverse('Forum:forum_detail', args=[2]))
        self.assertEqual(response.status_code, 404)

    def test_forum_vote_upvote(self):
        c = Client()
        data = urlencode({'type': 'up-vote', 'fingerprint': 12345})
        response = c.post(reverse('Forum:forum_vote', args=[1]), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content, encoding='utf8'), '{"voter": -1}')

    def test_forum_vote_downvote(self):
        c = Client()
        data = urlencode({'type': 'down-vote', 'fingerprint': 12345})
        response = c.post(reverse('Forum:forum_vote', args=[1]), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content, encoding='utf8'), '{"voter": -1}')

    def test_forum_vote_no_user(self):
        c = Client()
        data = urlencode({'type': 'up-vote', 'fingerprint': 4567})
        response = c.post(reverse('Forum:forum_vote', args=[1]), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)

    def test_forum_delete(self):
        c = Client()
        response = c.delete('/Forum/1?biri_key=123456')
        forum = Forum.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(forum.user, None)

    def test_forum_delete_incorrect_user(self):
        c = Client()
        response = c.delete('/Forum/1?biri_key=1234567')
        self.assertEqual(response.status_code, 403)


class ClientCommentTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(name="Sample User", biri="123456")
        User.objects.create(name="Sample User Two", biri="1234567")
        forum = Forum.objects.create(title="Test Forum Two", text="Sample Text One", latitude=-53.3, longitude=-8,
                                     user=user)
        Comment.objects.create(text="Sample Text", forum=forum, user=user)

    def test_post_comment_exist(self):
        c = Client()
        data = urlencode({'text': 'Sample Text', 'biri_key': 123456, 'forum': 1})
        response = c.post(reverse('Forum:comment', args=[1]), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)

    def test_post_comment_no_exist(self):
        c = Client()
        data = urlencode({'text': 'Sample Text', 'biri_key': 123456, 'forum': 1})
        response = c.post(reverse('Forum:comment', args=[2]), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 404)

    def test_comment_vote_upvote(self):
        c = Client()
        data = urlencode({'type': 'up-vote', 'fingerprint': 123456})
        response = c.post(reverse('Forum:comment_vote', args=[1, 1]), data,
                          content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content, encoding='utf8'), '{"voter": -1}')

    def test_comment_vote_downvote(self):
        c = Client()
        data = urlencode({'type': 'down-vote', 'fingerprint': 12345})
        response = c.post(reverse('Forum:comment_vote', args=[1, 1]), data,
                          content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content, encoding='utf8'), '{"voter": -1}')

    def test_comment_vote_no_user(self):
        c = Client()
        data = urlencode({'type': 'up-vote', 'fingerprint': 4567})
        response = c.post(reverse('Forum:forum_vote', args=[1]), data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(response.status_code, 200)

    def test_comment_delete(self):
        c = Client()
        response = c.delete('/Forum/1/1?biri_key=123456')
        comment = Comment.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.text, "")
        self.assertEqual(comment.user, None)

    def test_comment_delete_incorrect_user(self):
        c = Client()
        response = c.delete('/Forum/1/1?biri_key=1234567')
        self.assertEqual(response.status_code, 403)
