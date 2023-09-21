import os
import logging

from clickhouse_driver import Client

from utils.data import Migrations, Migration
from utils.errors import CHMFCBaseError, CHMFCBadQueryError
from utils.queries import ClickhouseQueries

# set looger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger("chmfc")

# get env vars
clickhouse_host = os.getenv('CHMFC_CH_HOST', 'localhost')
clickhouse_port = os.getenv('CHMFC_CH_PORT', '9000')
clickhouse_login = os.getenv('CHMFC_CH_LOGIN', 'test')
clickhouse_password = os.getenv('CHMFC_CH_PASSWORD', 'test')
clickhouse_database = os.getenv('CHMFC_CH_DATABASE', 'test')
migrations_path = os.getenv('CHMFC_MIG_PATH', 'test-migrations')
migrations_table = os.getenv('CHMFC_MIG_TABLE', 'default._migrations')

rule_queries = ClickhouseQueries(migrations_table=migrations_table)


def check_or_create_migrations_table(client: Client):
    # check migrations table and create it if needs
    exists = True
    try:
        ch_client.execute(rule_queries.exists_migrations_table())
    except Exception as e:
        if f"Table {migrations_table} doesn't exist" in str(e):
            create_shards, create_distributed = rule_queries.create_migrations_table()
            ch_client.execute(create_shards)
            ch_client.execute(create_distributed)

            exists = False
            logger.info(f"Table {migrations_table} has been created.")
        else:
            raise CHMFCBaseError(e)

    if exists:
        logger.info(f"Table {migrations_table} exists.")


def handle_migration(client: Client, version: int, v: Migration):
    writed_migration = client.execute(rule_queries.get_migration_by_version(version))

    # if exists
    if writed_migration:
        for row in writed_migration:
            if row[1] != v.checksum:
                logger.info(f'ALERT - {version} - {v.filename} - checksums are not equal')
        logger.info(f'PASS - {version} - {v.filename} - {v.checksum}')
    else:
        logger.debug(f'Migration {version} in clickhouse? {writed_migration if writed_migration else "No."}')

        # if migrations doesn't contain any query
        if not v.queries:
            logger.info(f'EMPTY - {version} - {v.filename}')
            client.execute(rule_queries.write_migration_to_the_table(version, v.filename, v.checksum))

        # else apply all queries in the migration
        for query in v.queries:
            try:
                client.execute(query)
            except Exception as e:
                exception_by_lines = str(e).split('\n')
                reason_ = ''
                for line in exception_by_lines:
                    if line.startswith('DB::Exception: '):
                        reason_ = line.replace('DB::Exception: ', '').replace('Stack trace:', '').strip()
                        break
                raise CHMFCBadQueryError(query, reason_)
        # and write migration version to the migrations table
        client.execute(rule_queries.write_migration_to_the_table(version, v.filename, v.checksum))
        logger.info(f'OK - {version} - {v.filename} - {v.checksum}')


if __name__ == "__main__":
    with Client.from_url(
        f'tcp://{clickhouse_login}:{clickhouse_password}@{clickhouse_host}:{clickhouse_port}/{clickhouse_database}'
    ) as ch_client:

        check_or_create_migrations_table(ch_client)

        for version, v in sorted(Migrations().get_from_path(migrations_path).items()):
            handle_migration(ch_client, version, v)
