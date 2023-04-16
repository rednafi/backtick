import os

import dotenv

from . import tasks

dotenv.load_dotenv()

BACKTICK_REDIS_URL = os.environ["BACKTICK_REDIS_URL"]
BACKTICK_LOG_LEVEL = os.environ["BACKTICK_LOG_LEVEL"]

BACKTICK_TASKS = {
    "do_something": tasks.do_something,
}

BACKTICK_QUEUES = {
    "default": "default",
    "scheduled": "scheduled",
}
