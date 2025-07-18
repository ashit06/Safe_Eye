web: daphne -b 0.0.0.0 -p $PORT Safe_Eye.asgi:application
worker: celery -A Safe_Eye worker --loglevel=info