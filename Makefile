NAME=clickhouse-migrations-for-cluster
DEV_COMPOSE_FLAGS=-f test-dockerfiles/docker-compose.yml -f test-dockerfiles/docker-compose.dev.yml -p dev

.PHONY: env_up env_test env_down
env_up: env_down
	docker compose $(COMPOSE_FLAGS) up -d
env_down:
	docker compose $(COMPOSE_FLAGS) down -v

.PHONY: dev_env_up dev_env_deploy dev_env_test dev_env_down
dev_env_up: COMPOSE_FLAGS=${DEV_COMPOSE_FLAGS}
dev_env_up: env_up
dev_env_down: COMPOSE_FLAGS=${DEV_COMPOSE_FLAGS}
dev_env_down: env_down

.PHONY: linter
linter:
	docker compose -f test-dockerfiles/docker-compose.linter.yml down
	docker compose -f test-dockerfiles/docker-compose.linter.yml up --build
	docker compose -f test-dockerfiles/docker-compose.linter.yml down

.PHONY: ci
ci:
	docker compose -f test-dockerfiles/docker-compose.ci.yml down
	docker compose -f test-dockerfiles/docker-compose.ci.yml up --build chmfc
	docker compose -f test-dockerfiles/docker-compose.ci.yml down
