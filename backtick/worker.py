# Preload libraries
from rq import Worker

from . import settings, utils

def main() -> None:
    """Run the worker."""
    # Provide the worker with the list of queues (str) to listen to.
    w = Worker(settings.BACKTICK_QUEUES.values(), connection=utils.get_redis())
    w.work()

if __name__ == "__main__":
    main()
