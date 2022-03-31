from django.contrib import admin

from .models import Forum, Comment, Voter, User
from django.db import models
from django.forms import TextInput, Textarea


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    pass


class VoterAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    pass


class CommentAdmin(admin.TabularInline):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2})}
    }

    fieldsets = [
        (None, {'fields': ['text', 'user', 'parent']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    model = Comment
    extra = 1


class ForumAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 2})}
    }

    fieldsets = [
        (None, {'fields': ['title', 'text', 'hashtag', 'image', 'location', 'user', 'embed_video']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]

    inlines = [CommentAdmin]
    list_filter = ['pub_date']
    search_fields = ['title']

    css = {
        'all': 'style.css'
    }


admin.site.register(Forum, ForumAdmin)
admin.site.register(Voter, VoterAdmin)
admin.site.register(User, UserAdmin)
