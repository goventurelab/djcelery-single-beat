# djcelery-single-beat

Django Celery Single Beat: Expired by https://github.com/ybrs/single-beat

Quick start
-----------

1. Add "djcelery_single_beat" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'djcelery_single_beat',
    ]

2. Run `python manage.py single_beat` to start your celery beat.


Parameters
-----------

`python manage.py single_beat` accepts 2 optional parameters:

1. `--app=YOUR_APP`: Specify your django app name
2. `--pidfile=YOUR_PID_FILE`: Set the pidfile. Useful for testing multiple celery beats on one machine.


Settings
-----------

The following parameters are configurable via django settings:

1. `DJCELERY_SINGLE_BEAT_IDENTIFIER`: Lock name stored on redis
2. `DJCELERY_SINGLE_BEAT_LOCK_TIME`: Number of seconds that lock is held by a running process
3. `DJCELERY_SINGLE_BEAT_INITIAL_LOCK_TIME`: Number of seconds that lock is held by an initated running process
4. `DJCELERY_SINGLE_BEAT_HEARTBEAT_INTERVAL`: Number of seconds between each iteration of beat checks
5. `DJCELERY_SINGLE_BEAT_WAIT_MODE`: Can be `supervised` or `heartbeat`
6. `DJCELERY_SINGLE_BEAT_WAIT_BEFORE_DIE`: Number of seconds before process dies if in `supervised` mode
7. `DJCELERY_SINGLE_BEAT_REDIS_SERVER`: Address of the redis server. e.g. redis://localhost:6379
