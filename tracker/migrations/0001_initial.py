from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='Project',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('name',models.CharField(max_length=200,unique=True)),
            ('slug',models.SlugField(max_length=200,unique=True)),
            ('description',models.TextField(blank=True)),
            ('path',models.CharField(blank=True,max_length=500)),
            ('language',models.CharField(blank=True,max_length=100)),
            ('color',models.CharField(default='#00d4aa',max_length=7)),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('updated_at',models.DateTimeField(auto_now=True)),
        ],options={'ordering':['-updated_at']}),
        migrations.CreateModel(name='Session',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('started_at',models.DateTimeField(default=django.utils.timezone.now)),
            ('ended_at',models.DateTimeField(blank=True,null=True)),
            ('notes',models.TextField(blank=True)),
            ('auto_closed',models.BooleanField(default=False)),
            ('project',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='sessions',to='tracker.project')),
        ],options={'ordering':['-started_at']}),
        migrations.CreateModel(name='Event',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('event_type',models.CharField(choices=[('session_start','Session Start'),('session_end','Session End'),('server_start','Server Start'),('server_stop','Server Stop')],max_length=20)),
            ('timestamp',models.DateTimeField(default=django.utils.timezone.now)),
            ('metadata',models.JSONField(blank=True,default=dict)),
            ('session',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='events',to='tracker.session')),
        ],options={'ordering':['timestamp']}),
    ]
