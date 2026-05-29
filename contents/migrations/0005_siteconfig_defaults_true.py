from django.db import migrations


PUBLIC_FIELDS = [
    'write_public',
    'archive_read_public', 'archive_comment_public', 'archive_reaction_public',
    'temporary_read_public', 'temporary_comment_public', 'temporary_reaction_public',
    'exhibition_read_public', 'exhibition_comment_public', 'exhibition_reaction_public',
    'exhibition_wishlist_public',
]


def set_all_public_true(apps, schema_editor):
    SiteConfig = apps.get_model('contents', 'SiteConfig')
    SiteConfig.objects.update(**{f: True for f in PUBLIC_FIELDS})


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0004_permissions_and_guest_comment'),
    ]

    operations = [
        migrations.RunPython(set_all_public_true, migrations.RunPython.noop),
    ]
