"""The environment variables live here."""
import os

import dotenv

from . import tasks

dotenv.load_dotenv()

BACKTICK_REDIS_URL = os.environ["BACKTICK_REDIS_URL"]

BACKTICK_TASKS = {
    "do_something": tasks.do_something,
}

BACKTICK_QUEUES = {
    "default": "default",
    "scheduled": "scheduled",
}
