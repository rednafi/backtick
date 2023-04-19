
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

## Prerequisites

To take the app for a spin:

* Make sure you have [Docker][docker] and [Docker Compose V2][docker-compose] installed
on your system.
* Clone the repo and head over to the root directory.
* Run `make up` to start the containers.
* Go to `localhost:5000/docs` to view the API docs.

## Exploration

### Registering new tasks

WIP...

### Executing earger tasks

WIP...

### Scheduling future tasks

WIP...

### Running multiple tasks

WIP...

### Cancelling scheduled tasks

WIP...

### Working with dependent tasks

WIP...

### Retrying failed tasks

WIP...

### Attaching callbacks to the tasks

WIP...

### Shutting down the workers

WIP...

### Cancelling the running tasks

WIP...

## Running the tests

WIP...

## Limitations

[rq-badge]: https://img.shields.io/badge/rq-red?style=for-the-badge
[fastapi-badge]: https://img.shields.io/badge/fastapi-teal?style=for-the-badge
[pytest-badge]: https://img.shields.io/badge/pytest-blue?style=for-the-badge
[docker]: https://www.docker.com/
[docker-compose]: https://docs.docker.com/compose/compose-v2/
