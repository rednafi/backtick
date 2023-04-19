"""Shutdown all workers."""
from rq.command import send_shutdown_command
from rq.worker import Worker

from backtick import utils


def main() -> None:
    connection = utils.get_redis()

    workers = Worker.all(connection=connection)
    for worker in workers:
        send_shutdown_command(connection, worker.name)  # Tells worker to shutdown


if __name__ == "__main__":
    main()
