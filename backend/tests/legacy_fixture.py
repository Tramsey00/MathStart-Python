"""Build historical source profile using unchanged Django migrations.

This is test fixture generation only; target fresh/runtime never imports Django.
"""
import os
import sys


def main():
    profile = sys.argv[1]
    assert os.environ['DJANGO_DB_NAME'].startswith('test_ms7_mig_v01_')
    assert os.environ['DJANGO_DB_PORT'] == '55441'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    if profile == 'A':
        targets = [('auth','0012_alter_user_first_name_max_length'), ('admin','0003_logentry_add_action_flag_choices'),
                   ('contenttypes','0002_remove_content_type_name'), ('sessions','0001_initial'), ('content','0001_initial')]
    else:
        targets = executor.loader.graph.leaf_nodes()
    executor.migrate(targets)
    connection.close()
    print('Synthetic source profile ' + profile + ' created')


if __name__ == '__main__':
    main()
