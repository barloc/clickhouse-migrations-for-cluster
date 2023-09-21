# clickhouse migrations for cluster mode

Service applies migrations from the directory to the clickhouse cluster. Main goal of the service - dev or test environments, which are identical with production environment.

## Important

Clickhouse doesn't have transactions for replicated tables, so we can not provide apllying migration in the single transaction. It is always applying migration queries step by step and after it writing success message to the trunsactions table in the cluster.

## Usage

Add your migrations directory to the docker image and then execute it.

`docker run -v ... -e ... barloc/clickhouse-migrations-for-cluster:0.0.1`

### Params

Only via envs.

* CHMFC_CH_HOST - hostname of the cluster (default: localhost)
* CHMFC_CH_PORT - port (default: 9000)
* CHMFC_CH_LOGIN - login (default: test)
* CHMFC_CH_PASSWORD - password (default: test)
* CHMFC_CH_DATABASE - database for connection (default: test)
* CHMFC_MIG_PATH - path to the directory with migrations (default: test-migrations)
* CHMFC_MIG_TABLE - name of the table with applying migrations (default: test._migrations)

### Migrations name (file)

* Every file with migration must have prefix with number (0001, 01, 010...), it is version of migrations. Migrations applies in the order of this prefix (version).
* Every file contains one or many query with `;` between.

## Local development

You need: docker, make, python >3.11.

### Install environment:

Install `venv`:

```
python3 -m venv ./venv
```

Activate:

```
source ./venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

### Linter

```
make linter
```

### Local env

Up clickhouse cluster for work:

```
make dev_env_up
```

Down cluster:

```
make dev_env_down
```

### Integration test

```
make ci
```

### Clickhouse version

Tested with yandex/clickhouse-server:21.8.5.7. If you want up version then rewrite it in the test-dockerfiles/docker-compose.*.yml.
