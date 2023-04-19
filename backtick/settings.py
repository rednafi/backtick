import os

import dotenv

if not dotenv.load_dotenv(".env"):  # pragma: no cover
    dotenv.load_dotenv(".sample.env")


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
