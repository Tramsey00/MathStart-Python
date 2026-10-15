"""Independent Django admin ordering/search oracle against disposable V02 rows."""
import json
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    from django.apps import apps
    from django.contrib import admin
    from django.contrib.admin.views.main import ChangeList
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    from backend.infrastructure.http.contracts import document
    policy = document('specs/migration/r02-v1/staff-list-policy-v1.json')['resources']
    outputs = []
    for case in json.load(sys.stdin):
        if case['resource'] == '__content':
            from content.models import ContentPage
            from content.services.catalogue import catalogue_context
            from django.http import QueryDict
            context = catalogue_context(QueryDict(case.get('query', '')))
            outputs.append({'case': case, 'ids': [t.pk for t in context['catalogue_topics']],
                'seo': {str(p.pk): {'title': p.meta_title, 'description': p.meta_description,
                    'canonical_path': p.get_absolute_url()} for p in ContentPage.objects.filter(is_published=True)}})
            continue
        rule = policy[case['resource']]
        model = apps.get_model(rule['model'])
        registered = admin.site._registry[model]
        request = RequestFactory().get('/admin/', {'q': case.get('q', '')})
        request.user = User.objects.get(pk=902)
        cl = ChangeList.__new__(ChangeList)
        cl.model, cl.lookup_opts, cl.model_admin = model, model._meta, registered
        cl.list_display, cl.params = list(registered.list_display), {}
        sort = case.get('sort', 'default')
        if sort != 'default':
            cl.params['o'] = '.'.join(('-' if term.startswith('-') else '')
                + str(cl.list_display.index(term.lstrip('-'))) for term in sort.split(','))
        queryset = registered.get_queryset(request)
        ordering = cl.get_ordering(request, queryset)
        queryset = queryset.order_by(*ordering)
        queryset, distinct = registered.get_search_results(request, queryset, case.get('q', ''))
        if distinct:
            queryset = queryset.distinct()
        outputs.append({'case': case, 'ordering': ordering, 'ids': list(queryset.values_list('pk', flat=True))})
    print(json.dumps(outputs, ensure_ascii=False))


if __name__ == '__main__':
    main()
