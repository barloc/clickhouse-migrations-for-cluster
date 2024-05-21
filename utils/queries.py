class ClickhouseQueries:
    def __init__(self, migrations_table: str):
        self.migrations_table = migrations_table
        self.schema = migrations_table.split('.')[0]
        self.table = migrations_table.split('.')[1]

    def exists_migrations_table(self):
        return f"select uuid from system.tables where database = '{self.schema}' and name = '{self.table}'"

    def create_migrations_table(self):
        create_shards_query = '''
            CREATE TABLE IF NOT EXISTS %s_shard  on cluster '{cluster}' (
                version     UInt32,
                name        String,
                checksum    String,
                created_at  DateTime DEFAULT now()
            ) engine=ReplicatedReplacingMergeTree('/clickhouse/{installation}/{cluster}/tables/{shard}/{database}/{table}', '{replica}')
            ORDER BY (version);
        ''' % self.migrations_table

        create_distributed_query = '''
            CREATE TABLE IF NOT EXISTS %s on cluster '{cluster}' AS %s_shard
            ENGINE = Distributed('{cluster}', %s, %s_shard, rand());
        ''' % (self.migrations_table, self.migrations_table, self.schema, self.table)

        return create_shards_query, create_distributed_query

    def get_migration_by_version(self, ver):
        return f'select version, checksum from {self.migrations_table} where version = {ver} limit 1'

    def write_migration_to_the_table(self, ver, name, checksum):
        return f"insert into {self.migrations_table} (version,name,checksum) values ({ver},'{name}','{checksum}')"
