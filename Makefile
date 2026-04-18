-include .env
-include vendors/deps-pipelines/shared/Makefile
-include Makefile.local

CURRENT_UID := $(shell id -u):$(shell id -g)
HASH := $(shell git rev-parse HEAD)
DATE := $(shell date)
TAG := $(shell git describe || echo "latest")
commit_short_sha := "$(CI_COMMIT_SHORT_SHA)"

APP_NAME = generic-unifier-plugin
NO_DEV_DOCKER_IMAGE = generic-unifier-plugin
DEV_DOCKER_IMAGE = generic-unifier-plugin-dev

.PHONY: config
## Show current docker compose config
config:
	docker compose -f docker-compose.yml config

.PHONY: config-test
## Show docker compose test config
config-test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml config

.PHONY: install
## Install default environment settings
install:
	cp .env.example .env

.PHONY: login
## Login in docker registry
login:
	docker login $(repository)

.PHONY: prereq
prereq:
	docker network create deps-network || true

.PHONY: prereq-tests
prereq-tests: | prereq
	docker compose -f docker-compose.yml down -v

.PHONY: run
## Run service
run: | prereq
	docker compose up -d

.PHONY: logs
## Open service logs
logs:
	docker compose logs -f

.PHONY: status
## Get running status information
status:
	docker compose ps

.PHONY: stop
## Stop runned services
stop:
	docker compose stop

.PHONY: build
## Build containers
build:
	docker compose build \
	--build-arg BUILD_HASH=$(HASH) \
	--build-arg BUILD_TAG=$(TAG) \
	--build-arg BUILD_DATE="$(DATE)"

.PHONY: migrate
## Apply database migrations
migrate:
	docker compose run --rm migrator update

.PHONY: shell-app
## Open shell in container
shell-app:
	docker compose exec -u root $(APP_NAME) /bin/sh

.PHONY: shell-db
## Open db shell
shell-db:
	@echo "No db shell"

.PHONY: format
## Apply black & isort code formatting
format:
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) black --config pyproject.toml .
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) isort --settings-path /app/setup.cfg .

.PHONY: format-check
## Check for correct code format
format-check:
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) black --config pyproject.toml .
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) isort --settings-path /app/setup.cfg --check-only .

.PHONY: lint
## Check code using linters
lint:
	docker compose run --rm --no-deps $(APP_NAME) flake8 .

.PHONY: mypy
## Check code using mypy
mypy:
	docker compose run --rm --no-deps $(APP_NAME) mypy .

.PHONY: tests-unit
## Run unit tests
tests-unit:
	docker compose run --rm --no-deps --user="root" $(APP_NAME) coverage run -a -m pytest -vv -x tests/unit

.PHONY: tests-integration
## Run integration tests
tests-integration:
	@echo "Ok"

.PHONY: tests
## Run unit & integration tests
tests: | tests-unit tests-integration

.PHONY: tests-with-coverage
tests-with-coverage:
	@#@ Test coverage
	docker compose run --rm --no-deps --user="root" $(APP_NAME) sh -c "coverage run -m pytest -vv -x tests/ && coverage report -i"

.PHONY: ci
## Run CI checks
ci: | prereq-tests format-check lint mypy tests-with-coverage prereq-tests

.PHONY: build-prod
## Build images for production
build-prod:
	$(call build_service,generic-unifier-plugin-dev,./etc/deps-generic-unifier-plugin/Dockerfile,,develop)
	$(call build_service,generic-unifier-plugin,./etc/deps-generic-unifier-plugin/Dockerfile,,,generic-unifier-plugin-dev)

.PHONY: push
## Push images to registry
push:
	$(call push_service,generic-unifier-plugin)
	$(call push_service,generic-unifier-plugin-dev)
	

.PHONY: deliver
## Build prod images and push to registry
deliver: | build-prod push

.PHONY: tag
## Retag built services
tag:
	$(call tag_service,generic-unifier-plugin)
	$(call tag_service,generic-unifier-plugin-dev)

.PHONY: pull
## Pull service images from docker registry
pull:
	$(call pull_service,generic-unifier-plugin)
	$(call pull_service,generic-unifier-plugin-dev)

.PHONY: helm-upgrade-service
helm-upgrade-service:
	helm upgrade --install $(CI_PROJECT_NAME) .helm/services \
        --values .helm/services/values.yaml $(ADDITIONAL_VALUES) \
        --set registry=$(REPOSITORY_URL) \
        --set image.tag=$(commit_short_sha) \
        --set vault_settings.enabled=$(VAULT_ENABLE) \
        --timeout 300s \
        --atomic \
        --wait \
        --debug \
        --namespace $(NAMESPACE)

.PHONY: helm-upgrade
helm-upgrade:
	make helm-upgrade-service

.PHONY: helm-deployment-rollback
helm-deployment-rollback:
	helm rollback --namespace $(NAMESPACE) $(CI_PROJECT_NAME) 0

.PHONY: helm-rollback
helm-rollback:
	make helm-deployment-rollback

.PHONY: build-no-dev
build-no-dev:
	$(call build_service,$(NO_DEV_DOCKER_IMAGE),./etc/deps-generic-unifier-plugin/Dockerfile,,build,$(DEV_DOCKER_IMAGE))
