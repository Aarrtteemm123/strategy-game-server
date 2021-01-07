import time

from celery.signals import celeryd_after_setup, celeryd_init


@celeryd_init.connect
def hello():
    while True:
        print("Hello celery")
        time.sleep(1)