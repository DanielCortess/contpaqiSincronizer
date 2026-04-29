import re
import sqlite3
from pathlib import Path

from DOM.ArticuloLogisticaAggregate import ArticuloLogisticaAggregate


class SQLLiteStockRepository:
	TABLE_DEFINITIONS = {
		"articulostocks": """
			CREATE TABLE articulostocks (
				articulostocksID INTEGER PRIMARY KEY AUTOINCREMENT,
				NetvyArticuloID INT DEFAULT NULL,
				ContpaqArticuloID INT DEFAULT NULL,
				StockActual REAL DEFAULT NULL
			)
		""",
	}

	def __init__(self, config):
		if not isinstance(config, dict):
			raise ValueError("config debe ser un diccionario con la llave DBPATH")

		db_path_config = config.get("DBPATH")
		if not db_path_config:
			raise ValueError("config debe incluir la llave DBPATH")

		base_path_config = config.get("BASEPATH")
		if base_path_config:
			self.base_path = Path(base_path_config).resolve()
		else:
			self.base_path = Path(__file__).resolve().parents[1]

		configured_path = Path(db_path_config)

		if configured_path.is_absolute():
			self.db_path = configured_path
		else:
			self.db_path = (self.base_path / configured_path).resolve()

		self.local_db_path = self.db_path.parent

	def init(self):
		self.local_db_path.mkdir(parents=True, exist_ok=True)

		with self.get_connection() as connection:
			for table_name, create_sql in self.TABLE_DEFINITIONS.items():
				self._sync_table(connection, table_name, create_sql)

		if not self.db_path.exists():
			raise Exception(f"No se pudo crear la base de datos de stock en la ruta: {self.db_path}")

		with self.get_connection() as connection:
			for table_name in self.TABLE_DEFINITIONS.keys():
				cursor = connection.execute(
					"SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
					(table_name,),
				)
				if cursor.fetchone() is None:
					raise Exception(
						f"La base de datos de stock fue creada pero falta la tabla requerida: {table_name}"
					)

	def get_connection(self):
		self.local_db_path.mkdir(parents=True, exist_ok=True)
		return sqlite3.connect(self.db_path, timeout=15)

	def _sync_table(self, connection, table_name, create_sql):
		current_sql = self._get_current_table_sql(connection, table_name)

		if current_sql is None:
			connection.execute(create_sql)
			connection.commit()
			return

		existing_columns = set(self._get_table_columns(connection, table_name))
		desired_definitions = self._parse_column_definitions(create_sql)

		for col_name, col_def in desired_definitions.items():
			if col_name not in existing_columns:
				connection.execute(f'ALTER TABLE "{table_name}" ADD COLUMN {col_def}')

		connection.commit()

	def _parse_column_definitions(self, create_sql):
		inner = re.search(r'\((.+)\)\s*$', create_sql.strip(), re.DOTALL)
		if not inner:
			return {}

		content = inner.group(1)
		definitions = {}
		depth = 0
		current = []

		for char in content:
			if char == '(':
				depth += 1
				current.append(char)
			elif char == ')':
				depth -= 1
				current.append(char)
			elif char == ',' and depth == 0:
				self._registrar_columna(current, definitions)
				current = []
			else:
				current.append(char)

		self._registrar_columna(current, definitions)
		return definitions

	def _registrar_columna(self, chars, definitions):
		line = ''.join(chars).strip()
		if not line:
			return
		parts = line.split()
		if not parts:
			return
		col_name = parts[0].strip('"[]`')
		if col_name.upper() in ('PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT'):
			return
		definitions[col_name] = line

	def _get_current_table_sql(self, connection, table_name):
		cursor = connection.execute(
			"SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
			(table_name,),
		)
		row = cursor.fetchone()
		return row[0] if row and row[0] else None

	def _get_table_columns(self, connection, table_name):
		cursor = connection.execute(f'PRAGMA table_info("{table_name}")')
		return [row[1] for row in cursor.fetchall()]

	def getStockChange(self, articulo_logistica):
		if articulo_logistica is None:
			raise ValueError("articulo_logistica es obligatorio")

		if articulo_logistica.NetvyArticuloID is None:
			raise ValueError("NetvyArticuloID es obligatorio")

		if articulo_logistica.ContpaqArticuloID is None:
			raise ValueError("ContpaqArticuloID es obligatorio")

		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT StockActual FROM articulostocks "
				"WHERE NetvyArticuloID = ? AND ContpaqArticuloID = ?",
				(articulo_logistica.NetvyArticuloID, articulo_logistica.ContpaqArticuloID),
			)
			row = cursor.fetchone()

			if row is None:
				return True

			stock_actual_db = row[0]
			return stock_actual_db != articulo_logistica.StockActual

	def createUpdateLogisticArticle(self, articulo_logistica):
		if articulo_logistica is None:
			raise ValueError("articulo_logistica es obligatorio")

		if articulo_logistica.NetvyArticuloID is None:
			raise ValueError("NetvyArticuloID es obligatorio")

		if articulo_logistica.ContpaqArticuloID is None:
			raise ValueError("ContpaqArticuloID es obligatorio")

		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT articulostocksID FROM articulostocks "
				"WHERE NetvyArticuloID = ? AND ContpaqArticuloID = ?",
				(articulo_logistica.NetvyArticuloID, articulo_logistica.ContpaqArticuloID),
			)
			row = cursor.fetchone()

			if row:
				conn.execute(
					"UPDATE articulostocks SET StockActual = ? "
					"WHERE articulostocksID = ?",
					(articulo_logistica.StockActual, row[0]),
				)
			else:
				conn.execute(
					"INSERT INTO articulostocks (NetvyArticuloID, ContpaqArticuloID, StockActual) "
					"VALUES (?, ?, ?)",
					(
						articulo_logistica.NetvyArticuloID,
						articulo_logistica.ContpaqArticuloID,
						articulo_logistica.StockActual,
					),
				)

			conn.commit()
