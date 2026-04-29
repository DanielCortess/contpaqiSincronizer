import re
import sqlite3
from pathlib import Path

from APP import init
from DOM.ArticuloLogisticaAggregate import ArticuloLogisticaAggregate
from DOM.ContpaqArticuloLogisticaCollection import ContpaqArticuloLogisticaCollection

_FECHA_INICIAL = "19990101000000000"
_REGISTROS_REQUERIDOS = [
	{"Tabla": "Mailing",             "Programa": "Netvy"},
	{"Tabla": "Articulo",            "Programa": "Netvy"},
	{"Tabla": "PedidoVentaCabecera", "Programa": "Netvy"},
	{"Tabla": "PedidoVentaLinea",    "Programa": "Netvy"},
	{"Tabla": "Mailing",             "Programa": "Contpaq"},
	{"Tabla": "Articulo",            "Programa": "Contpaq"},
	{"Tabla": "PedidoVentaCabecera", "Programa": "Contpaq"},
	{"Tabla": "PedidoVentaLinea",    "Programa": "Contpaq"},
]


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
				Accion CHAR(1) DEFAULT NULL,
				Detalle TEXT DEFAULT NULL
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
			raise Exception(f"No se pudo crear la base de datos SQLite en la ruta: {self.db_path}")

		with self.get_connection() as connection:
			for table_name in self.TABLE_DEFINITIONS.keys():
				cursor = connection.execute(
					"SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
					(table_name,),
				)
				if cursor.fetchone() is None:
					raise Exception(
						f"La base de datos SQLite fue creada pero falta la tabla requerida: {table_name}"
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

		# Añadir únicamente las columnas que faltan, sin recrear la tabla
		existing_columns = set(self._get_table_columns(connection, table_name))
		desired_definitions = self._parse_column_definitions(create_sql)

		for col_name, col_def in desired_definitions.items():
			if col_name not in existing_columns:
				connection.execute(f'ALTER TABLE "{table_name}" ADD COLUMN {col_def}')

		connection.commit()

	def _parse_column_definitions(self, create_sql):
		"""Extrae {nombre_columna: definición_completa} del SQL de CREATE TABLE."""
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
		# Ignorar restricciones a nivel de tabla
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

	def asegurar_fechas_sincronizacion(self):
		with self.get_connection() as conn:
			for registro in _REGISTROS_REQUERIDOS:
				cursor = conn.execute(
					"SELECT FechaSincronizacionID FROM FechaSincronizacion "
					"WHERE Tabla = ? AND Programa = ?",
					(registro["Tabla"], registro["Programa"]),
				)
				if cursor.fetchone() is None:
					conn.execute(
						"INSERT INTO FechaSincronizacion (Tabla, FechaHora, Programa) "
						"VALUES (?, ?, ?)",
						(registro["Tabla"], _FECHA_INICIAL, registro["Programa"]),
					)
				conn.commit()

	def get_fechas_sincronizacion(self):
		fechas = {}
		with self.get_connection() as conn:
			for registro in _REGISTROS_REQUERIDOS:
				cursor = conn.execute(
					"SELECT FechaHora FROM FechaSincronizacion "
					"WHERE Tabla = ? AND Programa = ?",
					(registro["Tabla"], registro["Programa"]),
				)
				row = cursor.fetchone()
				tabla = (
					registro["Tabla"].lower()
					.replace("pedidoventacabecera", "pedido_venta_cabecera")
					.replace("pedidoventalinea", "pedido_venta_linea")
				)
				programa = registro["Programa"].lower()
				fechas[f"fecha_{tabla}_{programa}"] = row[0] if row else _FECHA_INICIAL
		return fechas

	def actualizar_fecha_sincronizacion(self, tabla, programa, fecha):
		with self.get_connection() as conn:
			conn.execute(
				"UPDATE FechaSincronizacion SET FechaHora = ? "
				"WHERE Tabla = ? AND Programa = ?",
				(fecha, tabla, programa),
			)
			conn.commit()

	def existe_sincronizacion_por_netvy_id(self, tabla, netvy_id):
		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT SincronizacionID FROM Sincronizacion "
				"WHERE Tabla = ? AND NetvyID = ?",
				(tabla, netvy_id),
			)
			return cursor.fetchone() is not None

	def existe_sincronizacion_por_contpaq_id(self, tabla, contpaq_id):
		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT SincronizacionID FROM Sincronizacion "
				"WHERE Tabla = ? AND ContpaqID = ?",
				(tabla, contpaq_id),
			)
			return cursor.fetchone() is not None

	def get_contpaq_id_por_netvy_id(self, tabla, netvy_id):
		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT ContpaqID FROM Sincronizacion "
				"WHERE Tabla = ? AND NetvyID = ?",
				(tabla, netvy_id),
			)
			row = cursor.fetchone()
			return row[0] if row else None

	def get_netvy_id_por_contpaq_id(self, tabla, contpaq_id):
		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT NetvyID FROM Sincronizacion "
				"WHERE Tabla = ? AND ContpaqID = ?",
				(tabla, contpaq_id),
			)
			row = cursor.fetchone()
			return row[0] if row else None

	def crear_sincronizacion(self, tabla, netvy_id, contpaq_id, fecha):
		with self.get_connection() as conn:
			conn.execute(
				"INSERT INTO Sincronizacion (Tabla, NetvyID, ContpaqID, FechaHoraUltimaSincronizacion) "
				"VALUES (?, ?, ?, ?)",
				(tabla, netvy_id, contpaq_id, fecha),
			)
			conn.commit()

	def actualizar_fecha_ultima_sincronizacion(self, tabla, netvy_id, contpaq_id, fecha):
		with self.get_connection() as conn:
			conn.execute(
				"UPDATE Sincronizacion SET FechaHoraUltimaSincronizacion = ? "
				"WHERE Tabla = ? AND NetvyID = ? AND ContpaqID = ?",
				(fecha, tabla, netvy_id, contpaq_id),
			)
			conn.commit()

	def crear_historico(self, tabla, netvy_id, contpaq_id, fecha, subida, accion, detalle):
		"""
		Registra una entrada en SincronizacionHistorico.
		subida: 1 = Contpaq -> Netvy  (subida),  0 = Netvy -> Contpaq (bajada)
		accion: 'C' = creación, 'A' = actualización, 'B' = borrar
		detalle: descripción del resultado o excepción ocurrida
		"""
		with self.get_connection() as conn:
			conn.execute(
				"INSERT INTO SincronizacionHistorico "
				"(Tabla, NetvyID, ContpaqID, FechaHoraSincronizacion, Subida, Accion, Detalle) "
				"VALUES (?, ?, ?, ?, ?, ?, ?)",
				(tabla, netvy_id, contpaq_id, fecha, subida, accion, detalle),
			)
			conn.commit()

	def getLogisticArticles(self):
		logistica_articulos = []
		with self.get_connection() as conn:
			cursor = conn.execute(
				"SELECT NetvyID, ContpaqID "
				"FROM Sincronizacion "
				"WHERE UPPER(Tabla) = 'ARTICULO'"
			)
			for row in cursor.fetchall():
				logistica_articulos.append(
					ArticuloLogisticaAggregate(
						NetvyArticuloID=row[0],
						ContpaqArticuloID=row[1],
						StockActual=None,
					)
				)

		return ContpaqArticuloLogisticaCollection(
			creacion_modificar_borrar=logistica_articulos
		)


