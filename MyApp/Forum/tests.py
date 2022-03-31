import datetime

from django.test import TestCase
from .models import Forum, Comment, Voter, User
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


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
        self.assertEqual(user.name, "U654321")#


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
