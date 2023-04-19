import os

import dotenv

found = dotenv.load_dotenv(".env")

if not found:  # pragma: no cover
    dotenv.load_dotenv(".env.sample")


BACKTICK_REDIS_URL = os.environ["BACKTICK_REDIS_URL"]

BACKTICK_LOG_LEVEL = os.environ["BACKTICK_LOG_LEVEL"]


BACKTICK_TASKS = {
    "do_something": "backtick.tasks.do_something",
    "raise_exception": "backtick.tasks.raise_exception",
}

BACKTICK_QUEUES = {
    "default": "default",
    "another": "another",
}
