import hashlib
import os
from typing import Dict

from utils.errors import CHMFCIdenticalVersionError, CHMFCMigrationsDirectoryEmptyError


class Migration:
    def __init__(
        self,
        filename: str,
        queries: list,
        checksum: str,
    ):
        self.queries = queries
        self.filename = filename
        self.num = self.get_migration_num(filename)
        self.checksum = checksum

    def get_migration_num(self, file_):
        return int(file_.split('_')[0].strip())


class Migrations:
    def get_from_path(self, migrations_path) -> Dict[int, Migration]:
        result_dict = {}

        migrations_files = []
        for (_, _, filenames) in os.walk(migrations_path):
            migrations_files = filenames

        if not migrations_files:
            raise CHMFCMigrationsDirectoryEmptyError(migrations_path)

        for file_ in migrations_files:
            checksum = ''
            with open(f'{migrations_path}/{file_}', 'rb') as f:
                checksum = hashlib.file_digest(f, "md5").hexdigest()

            queries_ = []
            with open(f'{migrations_path}/{file_}', 'r') as f:
                body = f.read()

                for raw_query in body.split(';'):
                    query = raw_query.strip()
                    if not query:
                        continue
                    queries_.append(query)

            current_migration = Migration(
                filename=file_,
                queries=queries_,
                checksum=checksum,
            )
            if current_migration.num in result_dict:
                raise CHMFCIdenticalVersionError([current_migration.filename, result_dict[current_migration.num].filename])
            result_dict[current_migration.num] = current_migration

        return result_dict
