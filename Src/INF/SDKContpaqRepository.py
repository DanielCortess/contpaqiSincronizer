import pyodbc
from datetime import datetime
from DOM.ContpaqArticuloAggregate import ContpaqArticuloAggregate
from DOM.ContpaqArticuloCollection import ContpaqArticuloCollection
from DOM.ContpaqMailingAggregate import ContpaqMailingAggregate
from DOM.ContpaqMailingCollection import ContpaqMailingCollection


class SDKContpaqRepository:

	def __init__(self, config):
		"""
		Inicializa el repositorio de Contpaq con la configuración SQL Server.
		
		Args:
			config (dict): Diccionario con las llaves:
				- DRIVER: Driver ODBC de SQL Server (ej: {SQL Server})
				- SERVER: Servidor SQL Server
				- DATABASE: Base de datos
				- Trusted_Connection: 'yes' (autenticación integrada de Windows)
		"""
		if not isinstance(config, dict):
			raise ValueError("config debe ser un diccionario con la configuración de SQL Server")

		self.driver = config.get("DRIVER", "{SQL Server}")
		self.server = config.get("SERVER")
		self.database = config.get("DATABASE")
		self.trusted_connection = config.get("Trusted_Connection", "yes")

		if not self.server or not self.database:
			raise ValueError("config debe incluir las llaves SERVER y DATABASE")

		# Validar conexión al inicializar
		self._get_connection()

	def _parse_fecha(self, fecha):
		"""
		Parsea una fecha en diferentes formatos.
		
		Args:
			fecha: Puede ser:
				- datetime object
				- String ISO format: '2026-01-01' o '2026-01-01 12:30:45'
				- String YYYYMMDD: '20260101'
				- String YYYYMMDDHHmmSS: '20260101123045'
		
		Returns:
			datetime: Objeto datetime parseado
		"""
		if isinstance(fecha, datetime):
			return fecha
		
		if not isinstance(fecha, str):
			raise ValueError(f"Formato de fecha inválido: {fecha}")
		
		fecha = fecha.strip()
		
		# Intenta formato ISO primero
		try:
			return datetime.fromisoformat(fecha)
		except ValueError:
			pass
		
		# Intenta formato YYYYMMDDHHMMSS
		if len(fecha) == 14:
			try:
				return datetime.strptime(fecha, "%Y%m%d%H%M%S")
			except ValueError:
				pass
		
		# Intenta formato YYYYMMDD
		if len(fecha) == 8:
			try:
				return datetime.strptime(fecha, "%Y%m%d")
			except ValueError:
				pass
		
		raise ValueError(f"Formato de fecha no soportado: {fecha}. Use ISO (2026-01-01) o YYYYMMDD (20260101) o YYYYMMDDHHmmSS (20260101120000)")

	def _get_connection(self):
		"""
		Establece y retorna una conexión a SQL Server con autenticación integrada.
		"""
		try:
			connection_string = f"Driver={self.driver};Server={self.server};Database={self.database};Trusted_Connection=yes;"
			conn = pyodbc.connect(connection_string)
			return conn
		except Exception as e:
			raise Exception(f"Error al conectar a SQL Server: {str(e)}")

	def getArticles(self, fecha):
		"""
		Obtiene los artículos de Contpaq desde la fecha especificada.
		
		Args:
			fecha (str): Fecha en formato ISO (ej: '2026-04-15'), YYYYMMDD (ej: '20260415') 
						 o YYYYMMDDHHmmSS (ej: '20260415123045')
			
		Returns:
			ContpaqArticuloCollection: Colección con los artículos organizados
		"""
		# Si la fecha está vacía, retornar colección vacía
		if not fecha or (isinstance(fecha, str) and fecha.strip() == ""):
			return ContpaqArticuloCollection(
				tabla="dbo.admProductos",
				fechaHoraDesde=None,
				fechaHoraHasta=None,
				creacion_modificar_borrar=[]
			)

		# Parsear fecha
		try:
			fecha_desde = self._parse_fecha(fecha)
		except ValueError as e:
			raise ValueError(f"Error al parsear fecha: {str(e)}")

		# Obtener la fecha hasta (máximo timestamp después de fecha_desde)
		fecha_hasta = self._get_fecha_hasta_articulos(fecha_desde)

		# Si las fechas son iguales, retornar colección vacía
		if fecha_desde == fecha_hasta:
			return ContpaqArticuloCollection(
				tabla="dbo.admProductos",
				fechaHoraDesde=fecha_desde.isoformat(),
				fechaHoraHasta=fecha_hasta.isoformat(),
				creacion_modificar_borrar=[]
			)

		# Obtener los artículos en el rango de fechas
		articulos = self._get_articulos(fecha_desde, fecha_hasta)

		return ContpaqArticuloCollection(
			tabla="dbo.admProductos",
			fechaHoraDesde=fecha_desde.isoformat(),
			fechaHoraHasta=fecha_hasta.isoformat(),
			creacion_modificar_borrar=articulos
		)

	def _get_fecha_hasta_articulos(self, fecha_desde):
		"""
		Obtiene el máximo timestamp de la tabla de productos después de la fecha especificada.
		
		Args:
			fecha_desde (datetime): Fecha de inicio
			
		Returns:
			datetime: La fecha más reciente encontrada o la misma fecha si no hay resultados
		"""
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT TOP 1 CTIMESTAMP
			FROM dbo.admProductos
			WHERE CTIMESTAMP > ?
			ORDER BY CTIMESTAMP DESC
			"""

			cursor.execute(query, (fecha_desde,))
			result = cursor.fetchone()
			cursor.close()
			conn.close()

			if result:
				timestamp = result[0]
				# Si el timestamp es datetime lo retornamos, si es string lo convertimos
				if isinstance(timestamp, str):
					return datetime.fromisoformat(timestamp)
				return timestamp
			else:
				return fecha_desde

		except Exception as e:
			raise Exception(f"Error al obtener fecha hasta de artículos: {str(e)}")

	def _get_articulos(self, fecha_desde, fecha_hasta):
		"""
		Obtiene los artículos de Contpaq en el rango de fechas especificado.
		
		Args:
			fecha_desde (datetime): Fecha de inicio
			fecha_hasta (datetime): Fecha de fin
			
		Returns:
			list: Lista de ContpaqArticuloAggregate
		"""
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT CIDPRODUCTO, CCODIGOPRODUCTO, CNOMBREPRODUCTO, CTIPOPRODUCTO,
			       CFECHAALTAPRODUCTO, CFECHABAJA, CTIMESTAMP
			FROM dbo.admProductos
			WHERE CTIMESTAMP > ? AND CTIMESTAMP <= ?
			ORDER BY CTIMESTAMP DESC
			"""

			cursor.execute(query, (fecha_desde, fecha_hasta))
			rows = cursor.fetchall()
			cursor.close()
			conn.close()

			articulos = [self._map_articulo(row) for row in rows]
			return articulos

		except Exception as e:
			raise Exception(f"Error al obtener artículos de SQL Server: {str(e)}")

	def _map_articulo(self, row):
		"""
		Mapea una fila de SQL Server a ContpaqArticuloAggregate.
		
		Args:
			row: Fila del resultado de SQL Server
			
		Returns:
			ContpaqArticuloAggregate: Aggregate del artículo
		"""
		return ContpaqArticuloAggregate(
			CIDPRODUCTO=row[0],
			CCODIGOPRODUCTO=row[1],
			CNOMBREPRODUCTO=row[2],
			CTIPOPRODUCTO=row[3],
			CFECHAALTAPRODUCTO=row[4],
			CFECHABAJA=row[5],
			CTIMESTAMP=row[6]
		)

	def getMailings(self, fecha):
		"""
		Obtiene los clientes (mailings) de Contpaq desde la fecha especificada.
		
		Args:
			fecha (str): Fecha en formato ISO (ej: '2026-04-15'), YYYYMMDD (ej: '20260415')
						 o YYYYMMDDHHmmSS (ej: '20260415123045')
			
		Returns:
			ContpaqMailingCollection: Colección con los clientes organizados
		"""
		# Si la fecha está vacía, retornar colección vacía
		if not fecha or (isinstance(fecha, str) and fecha.strip() == ""):
			return ContpaqMailingCollection(
				tabla="dbo.admClientes",
				fechaHoraDesde=None,
				fechaHoraHasta=None,
				creacion_modificar_borrar=[]
			)

		# Parsear fecha
		try:
			fecha_desde = self._parse_fecha(fecha)
		except ValueError as e:
			raise ValueError(f"Error al parsear fecha: {str(e)}")

		# Obtener la fecha hasta (máximo timestamp después de fecha_desde)
		fecha_hasta = self._get_fecha_hasta_mailings(fecha_desde)

		# Si las fechas son iguales, retornar colección vacía
		if fecha_desde == fecha_hasta:
			return ContpaqMailingCollection(
				tabla="dbo.admClientes",
				fechaHoraDesde=fecha_desde.isoformat(),
				fechaHoraHasta=fecha_hasta.isoformat(),
				creacion_modificar_borrar=[]
			)

		# Obtener los clientes en el rango de fechas
		mailings = self._get_mailings(fecha_desde, fecha_hasta)

		return ContpaqMailingCollection(
			tabla="dbo.admClientes",
			fechaHoraDesde=fecha_desde.isoformat(),
			fechaHoraHasta=fecha_hasta.isoformat(),
			creacion_modificar_borrar=mailings
		)

	def _get_fecha_hasta_mailings(self, fecha_desde):
		"""
		Obtiene el máximo timestamp de la tabla de clientes después de la fecha especificada.
		
		Args:
			fecha_desde (datetime): Fecha de inicio
			
		Returns:
			datetime: La fecha más reciente encontrada o la misma fecha si no hay resultados
		"""
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT TOP 1 CTIMESTAMP
			FROM dbo.admClientes
			WHERE CTIMESTAMP > ?
			ORDER BY CTIMESTAMP DESC
			"""

			cursor.execute(query, (fecha_desde,))
			result = cursor.fetchone()
			cursor.close()
			conn.close()

			if result:
				timestamp = result[0]
				# Si el timestamp es datetime lo retornamos, si es string lo convertimos
				if isinstance(timestamp, str):
					return datetime.fromisoformat(timestamp)
				return timestamp
			else:
				return fecha_desde

		except Exception as e:
			raise Exception(f"Error al obtener fecha hasta de mailings: {str(e)}")

	def _get_mailings(self, fecha_desde, fecha_hasta):
		"""
		Obtiene los clientes de Contpaq en el rango de fechas especificado.
		
		Args:
			fecha_desde (datetime): Fecha de inicio
			fecha_hasta (datetime): Fecha de fin
			
		Returns:
			list: Lista de ContpaqMailingAggregate
		"""
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT CIDCLIENTEPROVEEDOR, CCODIGOCLIENTE, CRAZONSOCIAL,
			       CFECHAALTA, CRFC, CTIMESTAMP
			FROM dbo.admClientes
			WHERE CTIMESTAMP > ? AND CTIMESTAMP <= ?
			ORDER BY CTIMESTAMP DESC
			"""

			cursor.execute(query, (fecha_desde, fecha_hasta))
			rows = cursor.fetchall()
			cursor.close()
			conn.close()

			mailings = [self._map_mailing(row) for row in rows]
			return mailings

		except Exception as e:
			raise Exception(f"Error al obtener clientes de SQL Server: {str(e)}")

	def _map_mailing(self, row):
		"""
		Mapea una fila de SQL Server a ContpaqMailingAggregate.
		
		Args:
			row: Fila del resultado de SQL Server
			
		Returns:
			ContpaqMailingAggregate: Aggregate del cliente
		"""
		return ContpaqMailingAggregate(
			CIDCLIENTEPROVEEDOR=row[0],
			CCODIGOCLIENTE=row[1],
			CRAZONSOCIAL=row[2],
			CFECHAALTA=row[3],
			CRFC=row[4],
			CTIMESTAMP=row[5]
		)
