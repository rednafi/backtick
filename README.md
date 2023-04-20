
<h1>
backtick<img src='https://user-images.githubusercontent.com/30027932/233198527-8391a8fd-91d7-4e46-9a41-fed18fda0dde.png'
align='right' width='128' height='128'></h1>

<strong>
    >> <i>A tiny fixed-point task scheduling app built on top of rq </i><<
</strong>

---


![rq][rq-badge]
![fastapi][fastapi-badge]
![pytest][pytest-badge]

Backtick demonstrates a pattern that enables you to schedule asynchronous background
tasks through HTTP calls. You can choose to execute the task immediately or schedule it
for a future timestamp. Once scheduled, a worker process will pick up the task and
execute it in the background. Additionally, you have the option to cancel a scheduled
task by calling another endpoint.

## Rationale

While working on a Django project at my workplace, we needed a way to call asynchronous
tasks at future datetimes. We didn't need any periodic scheduling or cron support.
Naturally, we went for Celery's `task.apply_async(at=<datetime>)` function but that
suffers from one major gotcha: it keeps the schedule logs in memory and loses the
scheduled tasks whenever the workers are restarted. This also causes a situation where
future task cancellation doesn't work if the associated workers lose their working memory.

To avoid this, Celery doc recommends propping up a persistent worker that'll save the
worker state in a file on the disk. This whole setup feels janky and goes against the
philosophy of keeping the workers stateless and being able to redeploy them without
losing any task.

So this prototype demonstrates an app where you'll be able to register any background
task, schedule and cancel it with HTTP calls and it'll work reliably even if you've to
restart the workers for deployment. For simplicity's sake, `backtick` keeps the
scheduling logs in the Redis broker.

## Prerequisites

To take the app for a spin:

* Make sure you have [Docker][docker] and [Docker Compose V2][docker-compose] installed
on your system.
* Clone the repo and head over to the root directory.
* Run `make up` to start the containers.
* Go to `localhost:5000/docs` to view the API docs. This will take you to an interactive
OpenAPI compliant doc that looks like this:

    ![api-doc][api-doc]

## Exploration

### Executing eager tasks

You can use the `POST /schedule` endpoint to schedule a pre-registered task. Click on
the **schedule** bar and it'll allow you to send a POST request. The app comes with a
few registered tasks that you can execute. Paste the payload below to the request
section and click on the **Execute** button:

```json
{
  "task_name": "do_something",
  "datetimes": [],
  "kwargs": {"how_long": 5}
}
```

![api-doc-eager-tasks-a][api-doc-eager-tasks-a]

Here, `do_something` is a registered task that takes the `{"how_long": 5}` keyworded
argument. The task just waits for `how_long` seconds and returns a message. Once you've
made the POST request, you'll get a response that returns the scheduled task id. In this
case, since the `datetimes` field is empty, the task will be scheduled for immediate
execution:

![api-doc-eager-tasks-b][api-doc-eager-tasks-b]

Now you can check the container logs to see that the scheduled tasks have been executed
by a worker. The task id returned by the response of the `/schedule` endpoint should
match that of the worker logs. Run:

```
docker compose logs -f worker
```

```
backtick-worker-1  | INFO:rq.worker:default: backtick.tasks.do_something(how_long=5) (9777414c-f42a-42f6-a013-2d0eeb3ab1e9)
backtick-worker-1  | INFO:root:Starting to do something
backtick-worker-1  | INFO:root:Finished doing something
backtick-worker-1  | INFO:rq.worker:default: Job OK (9777414c-f42a-42f6-a013-2d0eeb3ab1e9)
backtick-worker-1  | INFO:rq.worker:Result is kept for 60 seconds
backtick-worker-1  | INFO:rq.worker:default: backtick.tasks.do_something(how_long=5) (422f32a4-bdf4-4499-99d7-5d9991b54a96)
```

### Scheduling future tasks

Future tasks can be scheduled by sending valid datetime strings to the `datetimes`
field. The datetimes must be valid UTC strings in `YYYY-MM-DDTHH:MM:SS+00:00` or
`YYYY-MM-DDTHH:MM:SSZ` format. Multiple datetime strings can be sent to schedule
mutliple executions. The following request will launch to tasks at future datetimes
with 1 minute intervals between them.

Before making the request make sure to change the datetime strings so that they're in
the future relative to the time when you're running the command.

```sh
curl -X 'POST' \
  'http://localhost:5000/schedule' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "task_name": "do_something",
  "datetimes": ["2023-04-20T21:04:03.843Z", "2023-04-20T21:05:04.843Z"],
  "kwargs": {"how_long": 5}
}'
```

This will return:

```json
{
  "task_ids": [
    "8c0ba34a-3e35-4826-ad94-0dec86d392d7",
    "9a44357f-da5a-454e-b028-e671a68c2b77"
  ],
  "message": "Tasks scheduled successfully"
}
```

Check the worker logs to ensure that the tasks get run successfully.


### Cancelling scheduled tasks

Use the `POST /unschedule` endpoint to cancel scheduled tasks.

```sh
curl -X 'POST' \
  'http://localhost:5000/unschedule' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "task_ids": [
    "9fb6ff54-d758-4cd1-9adb-d074604b788c",
    "3691e144-fd9c-4893-809b-55199fb804ff"
  ],
  "enqueue_dependents": true
}'
```

The `enqueue_dependents` flag instructs the system whether to cancel the dependent tasks
while canceling the primary one or not. You'll see shortly how to write and schedule
dependent tasks. Calling the endpoint will give you the following response:

```json
{
  "task_ids": [
    "9fb6ff54-d758-4cd1-9adb-d074604b788c",
    "3691e144-fd9c-4893-809b-55199fb804ff"
  ],
  "message": "Tasks unscheduled successfully"
}
```

### Registering new tasks

So far, we've only seen how to invoke and cancel pre-registered tasks but this section
will talk about how you can register and run your own tasks. Tasks are any Python
callable that's decorated with the `@utils.tasks` decorator. In the `backtick.tasks`
module, you'll be able to see the `do_something` task that we've seen so far:

```python
# tasks.py

import logging
import time

from . import utils


@utils.task(
    queue=settings.BACKTICK_QUEUES["default"],
    connection=utils.get_redis(),
    timeout=60,
    result_ttl=60,
)
def do_something(*, how_long: int) -> None:
    """Do something for a while.

    Args:
        how_long (int): How long to do something for.

    Returns:
        None
    """
    logging.info("Starting to do something")
    time.sleep(how_long)
    logging.info("Finished doing something")
```

The `utils.task` decorator accepts all the arguments accepted by the
[rq.decorators.job`][rq-job-decorator] decorator. Once the task has been defined, it
needs to be included to the `BACKTICK_TASKS` dict on the `backtick.settings` module.

```python
BACKTICK_TASKS = {
    "do_something": "backtick.tasks.do_something" # fully qualified task name
}
```

On the `POST /schedule` endpoint, the `task_name` field will refer to a key in this
task mapping.

### Working with dependent tasks

WIP...

### Retrying failed tasks

WIP...

### Attaching callbacks to the tasks

WIP...

### Shutting down the workers

Backtick provides a management script that allows you to gracefully shut down all the
workers. Running the script will make the workers wait until the currently running task
is finished, and then the associated worker processes will be cleaned up. Here's the
command to stop the workers:

```
make stop-workers
```

### Cancelling the running tasks

To cancel the currently, running tasks, execute:

```
make cancel-running-tasks
```

### Cancelling all scheduled tasks

Run `make cancel-scheduled-tasks` to cancel all the future scheduled tasks.

## Tests

The tests are run inside a separate docker container.

* To execute the unit tests, run:

    ```
    make test-up && make test-unit && make test-down
    ```

    This will spin up the test container, run the tests, and shut it down.

* Similarly, you can run the integration tests with the following command. The `sleep`
is required to give the database enough time to be ready.

    ```
    make test-up && sleep 5 && make test-integration && make test-down
    ```

* To run all the tests, use this command:

    ```
    make test-up && sleep 5 && make test && make test-down
    ```

## Limitations

[rq-badge]: https://img.shields.io/badge/rq-red?style=for-the-badge
[fastapi-badge]: https://img.shields.io/badge/fastapi-teal?style=for-the-badge
[pytest-badge]: https://img.shields.io/badge/pytest-blue?style=for-the-badge
[docker]: https://www.docker.com/
[docker-compose]: https://docs.docker.com/compose/compose-v2/

[api-doc]: https://user-images.githubusercontent.com/30027932/233474567-b3850504-eaf1-41c5-a70a-013da9cca412.png
[api-doc-eager-tasks-a]: https://user-images.githubusercontent.com/30027932/233481702-f6a6dbfd-cebf-4e27-b4a2-377a2f85c84f.png
[api-doc-eager-tasks-b]: https://user-images.githubusercontent.com/30027932/233484001-0258fbca-8d4f-47ad-8efc-8adf462b1e8e.png

[rq-job-decorator]: https://python-rq.org/docs/#the-job-decorator
