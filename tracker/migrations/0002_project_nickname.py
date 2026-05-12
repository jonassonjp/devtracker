from django.db import migrations, models


def populate_nicknames(apps, schema_editor):
    Project = apps.get_model('tracker', 'Project')
    for project in Project.objects.all():
        project.nickname = project.slug
        project.save()


class Migration(migrations.Migration):
    dependencies = [
        ('tracker', '0001_initial'),
    ]
    operations = [
        migrations.AddField(
            model_name='project',
            name='nickname',
            field=models.SlugField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.RunPython(populate_nicknames, migrations.RunPython.noop),
    ]
