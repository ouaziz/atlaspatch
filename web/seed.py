import os
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atlaspatchserver.settings")

import django
django.setup()


from django.db import connection
from django.contrib.auth.models import Group, Permission

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


FIXTURES = [
    "fixtures/group.json",
    "fixtures/user.json",
]


def seed_data():
    # for all
    print("=============fixtures/group.json")
    os.system(f"python manage.py loaddata fixtures/group.json ")
    # seed for dev
    print("=============fixtures/user.json")
    os.system(f"python manage.py loaddata fixtures/user.json ")
    # print("=============fixtures/profile.json")
    # os.system(f"python manage.py loaddata fixtures/profile.json ")

    ## set permissions to groups
    permissions = Permission.objects.exclude(content_type__app_label__in=["admin","sessions"])
    administrator = Group.objects.get(name='Administrator')
    user = Group.objects.get(name='User')
    for permission in permissions:
        administrator.permissions.add(permission)
        if "view" in permission.name:
            user.permissions.add(permission)



def seed_and_migrate():
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    # reset migrations
    with connection.cursor() as cursor:
        print(f"=============Drop schema: Public")
        cursor.execute("DROP SCHEMA public CASCADE;")
        print(f"=============Create schema: Public")
        cursor.execute("CREATE SCHEMA public;")
    
    print("=============python manage.py makemigrations")
    os.system("python manage.py makemigrations")
    print("=============python manage.py migrate")
    os.system("python manage.py migrate")

    print("=============python manage.py flush")
    os.system("python manage.py flush")

    # seed data
    seed_data()
    # add admin root
    os.system("python manage.py createsuperuser --username superuser --email superuser@admin.com")




if __name__ == "__main__":
    seed_and_migrate()