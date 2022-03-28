# Generated by Django 4.0.3 on 2022-03-27 18:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(blank=True, max_length=10000)),
                ('text', models.CharField(max_length=10000)),
                ('pub_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(blank=True, max_length=256)),
                ('title', models.CharField(max_length=200)),
                ('text', models.CharField(max_length=2000)),
                ('hashtag', models.CharField(blank=True, max_length=2000)),
                ('pub_date', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, upload_to='images/')),
                ('embed_video', models.URLField(blank=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, null=True, verbose_name='Latitude')),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, null=True, verbose_name='Longitude')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=24)),
                ('biri', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('comment_voted', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_voter_set', to='Forum.comment')),
                ('forum_voted', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forum_voter_set', to='Forum.forum')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Forum.user')),
            ],
        ),
        migrations.AddField(
            model_name='forum',
            name='score',
            field=models.ManyToManyField(blank=True, to='Forum.voter'),
        ),
        migrations.AddField(
            model_name='forum',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Forum.user'),
        ),
        migrations.AddField(
            model_name='comment',
            name='forum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Forum.forum'),
        ),
        migrations.AddField(
            model_name='comment',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='Forum.comment'),
        ),
        migrations.AddField(
            model_name='comment',
            name='score',
            field=models.ManyToManyField(blank=True, to='Forum.voter'),
        ),
    ]
