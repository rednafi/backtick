###########################################
## Help
###########################################

path := .

define Comment
	- Run `make help` to see all the available options.
	- Run `make lint` to run the linter.
	- Run `make lint-check` to check linter conformity.
	- Run `dep-lock` to lock the deps in 'requirements.txt' and 'requirements-dev.txt'.
	- Run `dep-sync` to sync current environment up to date with the locked deps.
endef


.PHONY: help
help: ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


###########################################
# Dependency management
###########################################

.PHONY: dep-lock
dep-lock: ## Freeze deps in 'requirements.txt' file.
	@pip-compile \
		requirements.in -o requirements.txt --no-emit-options --resolver backtracking
	@pip-compile \
		requirements-dev.in -o requirements-dev.txt --no-emit-options --resolver backtracking


.PHONY: dep-sync
dep-sync: ## Sync venv installation with 'requirements.txt' file.
	@pip-sync


###########################################
## Lint
###########################################

.PHONY: lint
lint: black blacken-docs ruff mypy	## Apply all the linters.


.PHONY: lint-check
lint-check:  ## Check whether the codebase satisfies the linter rules.
	@echo
	@echo "Checking linter rules..."
	@echo "========================"
	@echo
	@black --check $(path)
	@ruff $(path)
	@echo 'y' | mypy $(path) --install-types


.PHONY: black
black: ## Apply black.
	@echo
	@echo "Applying black..."
	@echo "================="
	@echo
	@black --fast $(path)
	@echo


.PHONY: blacken-docs
blacken-docs: ## Apply black to docs.
	@echo
	@echo "Applying blacken-docs..."
	@echo "========================"
	@echo
	@blacken-docs -l 88 -t py311 README.md
	@echo


.PHONY: ruff
ruff: ## Apply ruff.
	@echo "Applying ruff..."
	@echo "================"
	@echo
	@ruff --fix $(path)


.PHONY: mypy
mypy: ## Apply mypy.
	@echo
	@echo "Applying mypy..."
	@echo "================="
	@echo
	@mypy $(path)


###########################################
# Container management
###########################################

.PHONY: up
up: ## Start the development environment.
	@docker compose up -d


.PHONY: down
down: ## Stop the development environment.
	@docker compose down


.PHONY: test-up
test-up: ## Start the integration test environment.
	@docker compose -f docker-compose-test.yml up -d


.PHONY: test-down
test-down: ## Stop the integration test environment.
	@docker compose -f docker-compose-test.yml down


###########################################
## Tests
###########################################

.PHONY: test
test: ## Run all the tests.
	@docker compose -f docker-compose-test.yml exec test pytest -v -s


.PHONY: test-integration
test-integration: ## Run the integration tests.
	@docker compose -f docker-compose-test.yml exec test pytest -v -s -m integration


.PHONY: test-unit
test-unit: ## Run the unit tests.
	@docker compose -f docker-compose-test.yml exec test pytest -v -s -m 'not integration'


###########################################
# Worker & task management
###########################################

.PHONY: stop-workers
stop-workers: ## Stop the workers.
	@docker compose exec worker python -m scripts.stop_workers


.PHONY: cancel-running-tasks
cancel-running-tasks: ## Cancel all the running tasks.
	@docker compose exec worker python -m scripts.cancel_tasks --running


.PHONY: cancel-scheduled-tasks
cancel-scheduled-tasks: ## Cancel all the scheduled tasks.
	@docker compose exec worker python -m scripts.cancel_tasks --scheduled


.PHONY: cancel-all-tasks
cancel-all-tasks: ## Cancel all the tasks.
	@docker compose exec worker python -m scripts.cancel_tasks --all
