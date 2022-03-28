from better_profanity import profanity
from django import forms
from profanityfilter import ProfanityFilter

from Forum.models import Forum, Comment

from django.core.exceptions import ValidationError


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = "__all__"

    def clean(self):
        cd = self.cleaned_data
        return cd


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'forum', 'parent']

    def clean(self):
        cd = self.cleaned_data

        text = self.cleaned_data['text']

        # profanity-filter
        # pf = ProfanityFilter()
        # censored_text = pf.censor(text)

        # better-profanity-filter
        # TODO hate-sonar implementation or a better alternative
        profanity.load_censor_words()
        censored_text = profanity.censor(text)

        self.cleaned_data['text'] = censored_text
        return cd

