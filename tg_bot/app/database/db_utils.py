import csv
import tempfile
from .db_base import DatabaseBase


class UtilsDatabase(DatabaseBase):
    async def export_table_to_csv(self, table_name: str) -> str:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f'SELECT * FROM {table_name}')
            columns = rows[0].keys() if rows else []
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8')
            writer = csv.writer(tmp_file)
            writer.writerow(columns)
            for row in rows:
                writer.writerow([row[col] for col in columns])
            tmp_file.close()
            return tmp_file.name