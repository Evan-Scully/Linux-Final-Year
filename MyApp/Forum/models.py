import datetime
import json
import math

from django.contrib import admin
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.timezone import now, utc
from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from django.contrib.gis.db import models as sp_models


class User(models.Model):
    name = models.CharField(max_length=24)
    biri = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = "U" + self.biri
        super(User, self).save(*args, **kwargs)


class VoterManager(models.Manager):
    def get_previously_voted(self, user):
        forums = []
        for vote in super().get_queryset().filter(user_id=user.id).exclude(score=0):
            forums.append(self.get_forum(vote))

        return forums

    def get_forum(self, voter):
        for forum in Forum.objects.filter(id=voter.forum_voted.id):
            return forum


class Voter(models.Model):
    forum_voted = models.ForeignKey('Forum', on_delete=models.CASCADE, blank=True, null=True,
                                    related_name='forum_voter_set')
    comment_voted = models.ForeignKey('Comment', on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='comment_voter_set')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def up_vote(self):
        if self.score < 1:
            self.score = self.score + 1

    def down_vote(self):
        if self.score > -1:
            self.score = self.score - 1

    objects = models.Manager()
    voted = VoterManager()


class Forum(models.Model):
    slug = models.CharField(max_length=256, blank=True)

    title = models.CharField(max_length=200, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=2000, blank=False)
    hashtag = models.CharField(max_length=2000, blank=True)
    pub_date = models.DateTimeField(default=now, blank=True)

    score = models.ManyToManyField(Voter, blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True, default="default.jpg")
    embed_video = models.URLField(max_length=200, blank=True, null=True)

    latitude = sp_models.DecimalField(decimal_places=6, max_digits=9, blank=False, null=True, verbose_name='Latitude')
    longitude = sp_models.DecimalField(decimal_places=6, max_digits=9, blank=False, null=True, verbose_name='Longitude')

    # DELETE DATABASE, then comment location then migrate then uncomment
    # ADD IN LOCATION LAST COMMENT IT OUT FIRST THEN RUN MIGRATIONS
    location = sp_models.PointField(geography=True, null=True, blank=True)

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Published recently?',
    )
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Forum, self).save(*args, **kwargs)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def get_age(self):
        current_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        time_since_post = current_time - self.pub_date

        if time_since_post.days > 1:
            return time_since_post.days
        else:
            return time_since_post.seconds * 3600

    def __str__(self):
        return self.title

    def get_score(self):
        score = 0
        for vote in Voter.objects.filter(forum=self.id):
            score += vote.score
        return score

    def get_user(self):
        user = User.objects.get(id=self.user.id)
        return user

    def check_if_image_exists(self):
        if not self.image:
            return False
        else:
            return True

    objects = models.Manager()


class Comment(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    path = models.CharField(max_length=10000, blank=True)

    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    text = models.CharField(max_length=10000, blank=False)
    pub_date = models.DateTimeField(default=now, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    score = models.ManyToManyField(Voter, blank=True)

    class MPTTMeta:
        order_insertion_by = ['-pub_date']

    def get_score(self):
        score = 0
        for vote in Voter.objects.filter(comment=self.id):
            score += vote.score
        return score

    def get_user(self):
        user = User.objects.get(id=self.user.id)
        return user

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_age(self):
        current_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        time_since_post = current_time - self.pub_date

        if time_since_post.days >= 2:
            days = time_since_post.days
            return str(days) + " days ago"
        elif time_since_post.days == 1:
            days = time_since_post.days
            return str(days) + " day ago"
        else:
            hours = math.trunc(time_since_post.seconds / 3600)
            if hours <= 0:
                minutes = math.trunc(time_since_post.seconds / 60)
                if minutes >= 1:
                    return str(minutes) + " m ago"
                else:
                    if time_since_post.seconds == 0:
                        return "now"
                    else:
                        return str(time_since_post.seconds) + " s ago"
            return str(hours) + "h ago"
