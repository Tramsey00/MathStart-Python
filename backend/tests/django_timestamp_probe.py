"""Real Django pre-save comparison, only in the caller's reserved disposable DB."""
from datetime import datetime, timedelta, timezone
import json
import os


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from django.db import connection
    from django.contrib.auth.models import User
    from content.models import Grade, ContentPage, LessonPublication, MediaAsset
    from users.models import StudentProfile, IdentityReceipt
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), shobj_description(oid,'pg_database') FROM pg_database WHERE datname=current_database()")
        name, marker = cursor.fetchone()
    if not name.startswith('test_ms7_mig_v01_') or marker != 'MS7-MIG-V01 disposable synthetic test database':
        raise RuntimeError('Timestamp probe requires reserved disposable database')
    old = datetime(2000, 1, 1, tzinfo=timezone.utc)
    grade = Grade.objects.create(title='Django', slug='django-time', created_at=old)
    page = ContentPage.objects.create(title='Django', slug='django-time', created_at=old, updated_at=old)
    publication = LessonPublication.objects.create(page=page, source_path='synthetic/django', published_digest='0'*64, published_at=old)
    media = MediaAsset.objects.create(file='synthetic/django.svg', created_at=old)
    user = User.objects.create(username='django-time')
    profile = StudentProfile.objects.create(user=user, created_at=old)
    receipt = IdentityReceipt.objects.create(scope='synthetic-django', operation='register', key_digest='0'*64,
                request_digest='1'*64, created_at=old, expires_at=old+timedelta(days=7))
    records = [(grade, 'created_at'), (page, 'created_at'), (page, 'updated_at'),
               (publication, 'published_at'), (media, 'created_at'), (profile, 'created_at'), (receipt, 'created_at')]
    result = {'insert_preserves_old': {obj._meta.db_table+'.'+field: getattr(obj, field) == old for obj, field in records}}
    ContentPage.objects.filter(pk=page.pk).update(created_at=old, updated_at=old)
    page.refresh_from_db()
    page.title = 'Restricted'; page.save(update_fields=['title']); page.refresh_from_db()
    result['restricted_save_preserves_auto_now'] = page.updated_at == old
    page.save(); page.refresh_from_db()
    result['full_save_preserves_auto_now_add'] = page.created_at == old
    result['full_save_preserves_auto_now'] = page.updated_at == old
    page.updated_at = old; page.save(update_fields=['updated_at']); page.refresh_from_db()
    result['included_auto_now_preserves_old'] = page.updated_at == old
    ContentPage.objects.filter(pk=page.pk).update(updated_at=old)
    page.refresh_from_db()
    result['bulk_update_preserves_explicit_old'] = page.updated_at == old
    LessonPublication.objects.filter(pk=publication.pk).update(published_at=old)
    publication.refresh_from_db()
    publication.published_digest='1'*64; publication.save(update_fields=['published_digest']); publication.refresh_from_db()
    result['publication_restricted_save_preserves_auto_now'] = publication.published_at == old
    publication.save(); publication.refresh_from_db()
    result['publication_full_save_preserves_auto_now'] = publication.published_at == old
    publication.published_at=old; publication.save(update_fields=['published_at']); publication.refresh_from_db()
    result['publication_included_auto_now_preserves_old'] = publication.published_at == old
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
