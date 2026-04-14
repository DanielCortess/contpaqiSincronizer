import sqlite3
from pathlib import Path

from APP import init


class SQLLiteRepository:
	
	# Mantener el SQL visible facilita ajustar la estructura durante el desarrollo.
	TABLE_DEFINITIONS = {
		"FechaSincronizacion": """
			CREATE TABLE FechaSincronizacion (
				FechaSincronizacionID INTEGER PRIMARY KEY AUTOINCREMENT,
				Tabla VARCHAR(255) DEFAULT NULL,
				FechaHora DATETIME DEFAULT NULL,
				Programa VARCHAR(255) DEFAULT NULL
			)
		""",
		"Sincronizacion": """
			CREATE TABLE Sincronizacion (
				SincronizacionID INTEGER PRIMARY KEY AUTOINCREMENT,
				Tabla VARCHAR(255) DEFAULT NULL,
				NetvyID INT NOT NULL,
				ContpaqID INT NOT NULL,
				FechaHoraUltimaSincronizacion DATETIME DEFAULT NULL
			)
		""",
		"SincronizacionHistorico": """
			CREATE TABLE SincronizacionHistorico (
				SincronizacionHistoricoID INTEGER PRIMARY KEY AUTOINCREMENT,
				Tabla VARCHAR(255) DEFAULT NULL,
				NetvyID INT NOT NULL,
				ContpaqID INT NOT NULL,
				FechaHoraSincronizacion DATETIME DEFAULT NULL,
				Subida INTEGER DEFAULT NULL CHECK (Subida IN (0, 1) OR Subida IS NULL),
				Accion CHAR(1) DEFAULT NULL
			)
		""",
	}

	def __init__(self, config):
		if not isinstance(config, dict):
			raise ValueError("config debe ser un diccionario con la llave DBPATH")

		db_path_config = config.get("DBPATH")
		if not db_path_config:
			raise ValueError("config debe incluir la llave DBPATH")

		self.base_path = Path(__file__).resolve().parents[1]
		configured_path = Path(db_path_config)

		if configured_path.is_absolute():
			self.db_path = configured_path
		else:
			self.db_path = (self.base_path / configured_path).resolve()

		self.local_db_path = self.db_path.parent

	def init(self):
		self.local_db_path.mkdir(parents=True, exist_ok=True)

		with sqlite3.connect(self.db_path) as connection:
			for table_name, create_sql in self.TABLE_DEFINITIONS.items():
				self._sync_table(connection, table_name, create_sql)

	def get_connection(self):
		self.local_db_path.mkdir(parents=True, exist_ok=True)
		return sqlite3.connect(self.db_path)

	def _sync_table(self, connection, table_name, create_sql):
		current_sql = self._get_current_table_sql(connection, table_name)
		desired_sql = self._normalize_sql(create_sql)

		if current_sql is None:
			connection.execute(create_sql)
			connection.commit()
			return

		if self._normalize_sql(current_sql) == desired_sql:
			return

		self._recreate_table(connection, table_name, create_sql)
		connection.commit()

	def _get_current_table_sql(self, connection, table_name):
		cursor = connection.execute(
			"SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
			(table_name,),
		)
		row = cursor.fetchone()
		return row[0] if row and row[0] else None

	def _recreate_table(self, connection, table_name, create_sql):
		backup_table_name = f"{table_name}__backup"

		connection.execute(f'ALTER TABLE "{table_name}" RENAME TO "{backup_table_name}"')
		connection.execute(create_sql)

		old_columns = self._get_table_columns(connection, backup_table_name)
		new_columns = self._get_table_columns(connection, table_name)
		shared_columns = [column for column in new_columns if column in old_columns]

		if shared_columns:
			column_list = ", ".join(f'"{column}"' for column in shared_columns)
			connection.execute(
				f'INSERT INTO "{table_name}" ({column_list}) '
				f'SELECT {column_list} FROM "{backup_table_name}"'
			)

		connection.execute(f'DROP TABLE "{backup_table_name}"')

	def _get_table_columns(self, connection, table_name):
		cursor = connection.execute(f'PRAGMA table_info("{table_name}")')
		return [row[1] for row in cursor.fetchall()]

	def _normalize_sql(self, sql):
		return " ".join(sql.strip().replace("\n", " ").split()).lower()
