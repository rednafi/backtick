"""Vendored rq_scheduler.scripts.rqscheduler module."""

from rq_scheduler.scheduler import Scheduler

from rq_scheduler.utils import setup_loghandlers
from . import settings, utils

def main():
    setup_loghandlers("INFO")
    scheduler = Scheduler(connection=utils.get_redis(),
                          interval=30,
                          queue_name=settings.BACKTICK_QUEUES["scheduled"])
    scheduler.run()

if __name__ == '__main__':
    main()
