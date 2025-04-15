python manage.py migrate
python manage.py createcachetable django_cache
python manage.py collectstatic --noinput

#system
#python manage.py init_realm
#python manage.py init_realm_resource

# node
# python manage.py node_init

# monitor
# python manage.py plugin_init

# cmdb
# python manage.py model_init
supervisord -n