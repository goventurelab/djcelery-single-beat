import logging
import os
import redis
import pyuv
import signal
import sys
import time

from django.conf import settings


logging.basicConfig(level=0)
logger = logging.getLogger(__name__)


class Process(object):
    def __init__(self, options):
        self.state = None
        self.options = options
        self.t1 = time.time()

        self.identifier = self.read_settings("DJCELERY_SINGLE_BEAT_IDENTIFIER", "DJCELERY_SINGLE_BEAT")
        self.lock_time = self.read_settings("DJCELERY_SINGLE_BEAT_LOCK_TIME", 3)
        self.initial_lock_time = self.read_settings("DJCELERY_SINGLE_BEAT_INITIAL_LOCK_TIME", self.lock_time * 2)
        assert self.lock_time < self.initial_lock_time, "Inital lock time must be greater than lock time "

        self.heartbeat_interval = int(self.read_settings("DJCELERY_SINGLE_BEAT_HEARTBEAT_INTERVAL", 1))
        assert self.heartbeat_interval < (self.lock_time / 2.0), "Heartbeat interval must be smaller than lock time / 2"

        self.wait_mode = self.read_settings("DJCELERY_SINGLE_BEAT_WAIT_MODE", "heartbeat")
        assert self.wait_mode in ('supervised', 'heartbeat')

        self.wait_before_die = int(self.read_settings("DJCELERY_SINGLE_BEAT_WAIT_BEFORE_DIE", 60))

        self.rds = redis.Redis.from_url(self.read_settings("DJCELERY_SINGLE_BEAT_REDIS_SERVER", "redis://localhost:6379"))
        self.rds.ping()

        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)

        self.loop = pyuv.Loop.default_loop()
        self.timer = pyuv.Timer(self.loop)
        self.state = 'WAITING'
        self.lock_key = None

    def read_settings(self, field, default):
        return getattr(settings, field, default)

    def proc_exit_cb(self, proc, exit_status, term_signal):
        sys.exit(exit_status)

    def stdout_read_cb(self, handle, data, error):
        if data:
            sys.stdout.write(data.decode('utf-8'))

    def stderr_read_cb(self, handle, data, error):
        if data:
            sys.stdout.write(data.decode('utf-8'))

    def timer_cb(self, timer):
        logger.debug("timer called %s state=%s",
                     time.time() - self.t1, self.state)
        self.t1 = time.time()
        if self.state == 'WAITING':
            if self.acquire_lock():
                self.spawn_process()
            else:
                if self.wait_mode == 'supervised':
                    logging.debug("already running, will exit after %s seconds"
                                  % self.wait_before_die)
                    time.sleep(self.wait_before_die)
                    sys.exit()
        elif self.state == "RUNNING":
            self.rds.set(
                self.identifier,
                self.proc.pid,
                ex=self.lock_time
            )

    def acquire_lock(self):
        return self.rds.execute_command(
            'SET',
            self.identifier,
            'Empty',
            'NX',
            'EX',
            self.initial_lock_time
        )

    def sigterm_handler(self, signum, frame):
        logging.debug("our state %s", self.state)
        if self.state == 'WAITING':
            sys.exit(signum)
        elif self.state == 'RUNNING':
            logger.debug('already running sending signal to child - %s',
                         self.proc.pid)
            os.kill(self.proc.pid, signum)

    def run(self):
        self.timer.start(self.timer_cb, 0.1, self.heartbeat_interval)
        self.loop.run()

    def spawn_process(self):
        self.proc = pyuv.Process(self.loop)

        stdout_pipe = pyuv.Pipe(self.loop)
        stderr_pipe = pyuv.Pipe(self.loop)

        stdio = []
        stdio.append(pyuv.StdIO(flags=pyuv.UV_IGNORE))
        stdio.append(pyuv.StdIO(
            stream=stdout_pipe,
            flags=pyuv.UV_CREATE_PIPE | pyuv.UV_WRITABLE_PIPE))
        stdio.append(pyuv.StdIO(
            stream=stderr_pipe,
            flags=pyuv.UV_CREATE_PIPE | pyuv.UV_WRITABLE_PIPE))

        self.state = "RUNNING"

        args = ["beat"]
        for key, val in self.options.iteritems():
            if val is not None:
                args.append('--{}={}'.format(key, val))
        self.proc.spawn(file="celery",
                        args=args,
                        cwd=os.getcwd(),
                        exit_callback=self.proc_exit_cb,
                        stdio=stdio)

        stdout_pipe.start_read(self.stdout_read_cb)
        stderr_pipe.start_read(self.stderr_read_cb)
