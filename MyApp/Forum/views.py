import json

from django.core import serializers
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import generic
from .models import Forum, Comment, Voter, User
from Forum.forms import ForumForm, CommentForm

# Geolocation
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


def forum(request):
    if request.method == 'GET':
        # distance you can see posts of other people
        radius = 10
        # TODO remove hardcoded current user location

        # Position by long, lat
        college = Point(-7.9, 53.4)
        home = Point(-7.087, 53.052)
        dublin = Point(-6.27, 53.352)

        all_forums = Forum.objects.filter(location__distance_lt=(college, Distance(km=radius)))[:10][::-1]

        # TODO remove hardcoded user hardware URI and get from POST method
        # user = User.objects.get(ip="9563bb103459709e3e48019b27e1f48a")
        # previously_voted = Voter.voted.get_previously_voted(user=user)
        # not_voted = list(set(all_forums) - set(previously_voted))

        form = ForumForm
        context = {
            'forum_list': all_forums,
            'form': form
        }

        return render(request, 'Forum/index.html', context)

    if request.method == 'POST':
        form = ForumForm(request.POST, request.FILES)
        user = request.POST.get('biri_key')
        username = request.POST.get('name')

        if form.is_valid():
            try:
                user = get_object_or_404(User, biri=user)
                if username:
                    user.name = username
                    user.save()

            except Exception as f:
                user = User(biri=user)
                user.name = username
                user.save()
            lat = form.cleaned_data['latitude']
            long = form.cleaned_data['longitude']
            pnt = Point((lat, long), srid=4326)

            new_forum = form.save()
            new_forum.user = user
            new_forum.location = pnt
            new_forum.save()

            new_forum = new_forum.__dict__

            html = render_to_string('partials/_forum.html', {"forum": new_forum}, request=request)
            return HttpResponse(html)
        else:
            print(form.errors)
            return HttpResponse(status=400)


def forum_detail(request, forum_id):
    if request.method == "GET":
        forum_requested = get_object_or_404(Forum, id=forum_id)
        form = CommentForm
        comment_list = Comment.objects.filter(forum=forum_requested)
        context = {
            'forum': forum_requested,
            'comments': comment_list
        }
        return render(request, 'Forum/detail.html', context)

    if request.method == "DELETE":
        instance = Forum.objects.get(id=forum_id)
        instance.delete()
        return HttpResponse(status=204)


def forum_vote(request, forum_id):
    current_forum = get_object_or_404(Forum, id=forum_id)

    if request.method == 'POST':
        fingerprint = request.POST.get('fingerprint')
        vote_type = request.POST.get('vote')
        try:
            user = get_object_or_404(User, biri=fingerprint)
        except Exception as e:
            print(e)
            user = User(biri=fingerprint)
            user.save()
        try:
            voter = get_object_or_404(Voter, forum=current_forum.id, user_id=user.id)
        except Exception as f:
            print(f)
            voter = Voter(forum=current_forum.id, user=user)
            voter.save()
            current_forum.score.add(voter)

        if vote_type == "upvote":
            voter.up_vote()
        else:
            voter.down_vote()
        voter.save()
        return JsonResponse({"voter": voter.score}, status=200)

    if request.method == 'GET':
        current_score = Forum.objects.filter(id=forum_id)
        return JsonResponse({"score": current_score[0].get_score()}, status=200)

    return JsonResponse({}, status=200)


def comment(request, forum_id):
    if request.method == 'POST':
        current_forum = get_object_or_404(Forum, id=forum_id)
        form = CommentForm(request.POST)

        user = request.POST.get('biri_key')

        if form.is_valid():
            try:
                user = get_object_or_404(User, biri=user)
            except Exception as f:
                user = User(biri=user)
                user.save()

        if form.is_valid():
            new_comment = form.save()
            new_comment.user = user
            new_comment.save()

            comment_json = new_comment.__dict__
            comment_json['name'] = new_comment.get_user.name
            # comment_json['reply'] = "reply"

            html = render_to_string('partials/_comment.html', {"comment": comment_json, "forum": current_forum},
                                    request=request)
            return HttpResponse(html)
        else:
            print(form.errors)
            return HttpResponse(status=400)

    if request.method == 'GET':
        return HttpResponse(status=404)


def comment_detail(request, forum_id, comment_id):
    if request.method == 'GET':
        found_comment = Comment.objects.filter(forum=forum_id, id=comment_id).first()
        found_comment = found_comment.__dict__
        comment_json = json.dumps(found_comment, indent=4, sort_keys=True, default=str)
        return JsonResponse({"comment": comment_json}, status=200)

    if request.method == "DELETE":
        current_comment = Comment.objects.get(id=comment_id)
        current_comment.delete()
        return HttpResponse(status=204)


def comment_vote(request, forum_id, comment_id):
    current_comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        fingerprint = request.POST.get('fingerprint')
        vote_type = request.POST.get('vote')
        try:
            user = get_object_or_404(User, biri=fingerprint)
        except Exception as e:
            print(e)
            user = User(biri=fingerprint)
            user.save()
        try:
            voter = get_object_or_404(Voter, comment=current_comment.id, user_id=user.id)
        except Exception as f:
            print(f)
            voter = Voter(comment=current_comment.id, user=user)
            voter.save()
            current_comment.score.add(voter)

        if vote_type == "upvote":
            voter.up_vote()
        else:
            voter.down_vote()
        voter.save()
        return JsonResponse({"voter": voter.score}, status=200)

    if request.method == 'GET':
        current_score = Comment.objects.filter(id=comment_id)
        return JsonResponse({"score": current_score[0].get_score()}, status=200)


def success(request):
    return HttpResponse('successfully stored')


class IndexView(generic.ListView):
    template_name = 'Forum/index.html'
    context_object_name = 'latest_forum_list'

    def get_queryset(self):
        """Return the last five published forums."""
        return Forum.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Forum
    template_name = 'Forum/detail.html'
