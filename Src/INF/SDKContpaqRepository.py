import ctypes
import os
import pyodbc
from ctypes import c_int, c_double, c_char, Structure, byref, create_string_buffer, WinDLL
from datetime import datetime, date
from DOM.ContpaqArticuloAggregate import ContpaqArticuloAggregate
from DOM.ContpaqArticuloCollection import ContpaqArticuloCollection
from DOM.ContpaqMailingAggregate import ContpaqMailingAggregate
from DOM.ContpaqMailingCollection import ContpaqMailingCollection
from DOM.ContpaqPedidoVentaCabeceraAggregate import ContpaqPedidoVentaCabeceraAggregate
from DOM.ContpaqPedidoVentaLineaAggregate import ContpaqPedidoVentaLineaAggregate


# Traducción del struct tProducto de C# (LayoutKind.Sequential, CharSet.Ansi, Pack=4)
class tProducto(Structure):
	_pack_ = 4
	_fields_ = [
		("cCodigoProducto",              c_char * 31),
		("cNombreProducto",              c_char * 61),
		("cDescripcionProducto",         c_char * 256),
		("cTipoProducto",                c_int),
		("cFechaAltaProducto",           c_char * 24),
		("cFechaBaja",                   c_char * 24),
		("cStatusProducto",              c_int),
		("cControlExistencia",           c_int),
		("cMetodoCosteo",                c_int),
		("cCodigoUnidadBase",            c_char * 31),
		("cCodigoUnidadNoConvertible",   c_char * 31),
		("cPrecio1",                     c_double),
		("cPrecio2",                     c_double),
		("cPrecio3",                     c_double),
		("cPrecio4",                     c_double),
		("cPrecio5",                     c_double),
		("cPrecio6",                     c_double),
		("cPrecio7",                     c_double),
		("cPrecio8",                     c_double),
		("cPrecio9",                     c_double),
		("cPrecio10",                    c_double),
		("cImpuesto1",                   c_double),
		("cImpuesto2",                   c_double),
		("cImpuesto3",                   c_double),
		("cRetencion1",                  c_double),
		("cRetencion2",                  c_double),
		("cNombreCaracteristica1",       c_char * 61),
		("cNombreCaracteristica2",       c_char * 61),
		("cNombreCaracteristica3",       c_char * 61),
		("cCodigoValorClasificacion1",   c_char * 4),
		("cCodigoValorClasificacion2",   c_char * 4),
		("cCodigoValorClasificacion3",   c_char * 4),
		("cCodigoValorClasificacion4",   c_char * 4),
		("cCodigoValorClasificacion5",   c_char * 4),
		("cCodigoValorClasificacion6",   c_char * 4),
		("cTextoExtra1",                 c_char * 51),
		("cTextoExtra2",                 c_char * 51),
		("cTextoExtra3",                 c_char * 51),
		("cFechaExtra",                  c_char * 24),
		("cImporteExtra1",               c_double),
		("cImporteExtra2",               c_double),
		("cImporteExtra3",               c_double),
		("cImporteExtra4",               c_double),
	]


# Traducción del struct tCteProv de C# (LayoutKind.Sequential, CharSet.Ansi, Pack=4)
class tCteProv(Structure):
	_pack_ = 4
	_fields_ = [
		("cCodigoCliente",                          c_char * 31),
		("cRazonSocial",                            c_char * 61),
		("cFechaAlta",                              c_char * 24),
		("cRFC",                                    c_char * 21),
		("cCURP",                                   c_char * 21),
		("cDenComercial",                           c_char * 51),
		("cRepLegal",                               c_char * 51),
		("cNombreMoneda",                           c_char * 61),
		("cListaPreciosCliente",                    c_int),
		("cDescuentoMovto",                         c_double),
		("cBanVentaCredito",                        c_int),
		("cCodigoValorClasificacionCliente1",       c_char * 4),
		("cCodigoValorClasificacionCliente2",       c_char * 4),
		("cCodigoValorClasificacionCliente3",       c_char * 4),
		("cCodigoValorClasificacionCliente4",       c_char * 4),
		("cCodigoValorClasificacionCliente5",       c_char * 4),
		("cCodigoValorClasificacionCliente6",       c_char * 4),
		("cTipoCliente",                            c_int),
		("cEstatus",                                c_int),
		("cFechaBaja",                              c_char * 24),
		("cFechaUltimaRevision",                    c_char * 24),
		("cLimiteCreditoCliente",                   c_double),
		("cDiasCreditoCliente",                     c_int),
		("cBanExcederCredito",                      c_int),
		("cDescuentoProntoPago",                    c_double),
		("cDiasProntoPago",                         c_int),
		("cInteresMoratorio",                       c_double),
		("cDiaPago",                                c_int),
		("cDiasRevision",                           c_int),
		("cMensajeria",                             c_char * 21),
		("cCuentaMensajeria",                       c_char * 61),
		("cDiasEmbarqueCliente",                    c_int),
		("cCodigoAlmacen",                          c_char * 31),
		("cCodigoAgenteVenta",                      c_char * 31),
		("cCodigoAgenteCobro",                      c_char * 31),
		("cRestriccionAgente",                      c_int),
		("cImpuesto1",                              c_double),
		("cImpuesto2",                              c_double),
		("cImpuesto3",                              c_double),
		("cRetencionCliente1",                      c_double),
		("cRetencionCliente2",                      c_double),
		("cCodigoValorClasificacionProveedor1",     c_char * 4),
		("cCodigoValorClasificacionProveedor2",     c_char * 4),
		("cCodigoValorClasificacionProveedor3",     c_char * 4),
		("cCodigoValorClasificacionProveedor4",     c_char * 4),
		("cCodigoValorClasificacionProveedor5",     c_char * 4),
		("cCodigoValorClasificacionProveedor6",     c_char * 4),
		("cLimiteCreditoProveedor",                 c_double),
		("cDiasCreditoProveedor",                   c_int),
		("cTiempoEntrega",                          c_int),
		("cDiasEmbarqueProveedor",                  c_int),
		("cImpuestoProveedor1",                     c_double),
		("cImpuestoProveedor2",                     c_double),
		("cImpuestoProveedor3",                     c_double),
		("cRetencionProveedor1",                    c_double),
		("cRetencionProveedor2",                    c_double),
		("cBanInteresMoratorio",                    c_int),
		("cTextoExtra1",                            c_char * 51),
		("cTextoExtra2",                            c_char * 51),
		("cTextoExtra3",                            c_char * 51),
		("cImporteExtra1",                          c_double),
		("cImporteExtra2",                          c_double),
		("cImporteExtra3",                          c_double),
		("cImporteExtra4",                          c_double),
	]


# Traducción del struct tDocumento de C# (LayoutKind.Sequential, CharSet.Ansi, Pack=4)
# kLongCodigo=31, kLongSerie=12, kLongFecha=24, kLongReferencia=21
class tDocumento(Structure):
	_pack_ = 4
	_fields_ = [
		("aFolio",          c_double),
		("aNumMoneda",      c_int),
		("aTipoCambio",     c_double),
		("aImporte",        c_double),
		("aDescuentoDoc1",  c_double),
		("aDescuentoDoc2",  c_double),
		("aSistemaOrigen",  c_int),
		("aCodConcepto",    c_char * 31),
		("aSerie",          c_char * 12),
		("aFecha",          c_char * 24),
		("aCodigoCteProv",  c_char * 31),
		("aCodigoAgente",   c_char * 31),
		("aReferencia",     c_char * 21),
		("aAfecta",         c_int),
		("aGasto1",         c_double),
		("aGasto2",         c_double),
		("aGasto3",         c_double),
	]


# Traducción del struct tMovimiento de C# (LayoutKind.Sequential, CharSet.Ansi, Pack=4)
# kLongCodigo=31, kLongReferencia=21
class tMovimiento(Structure):
	_pack_ = 4
	_fields_ = [
		("aConsecutivo",        c_int),
		("aUnidades",           c_double),
		("aPrecio",             c_double),
		("aCosto",              c_double),
		("aCodProdSer",         c_char * 31),
		("aCodAlmacen",         c_char * 31),
		("aReferencia",         c_char * 21),
		("aCodClasificacion",   c_char * 31),
	]


class SDKContpaqRepository:

	def __init__(self, config):
		"""
		Inicializa el repositorio de Contpaq con la configuración SQL Server y SDK.
		
		Args:
			config (dict): Diccionario con las llaves:
				- DRIVER: Driver ODBC de SQL Server (ej: {SQL Server})
				- SERVER: Servidor SQL Server
				- DATABASE: Base de datos
				- Trusted_Connection: 'yes' (autenticación integrada de Windows)
				- PATH: Ruta de instalación del SDK (donde está MGWServicios.dll)
				- USER: Usuario de Contpaqi (default: SUPERVISOR)
				- PASSWORD: Contraseña de Contpaqi
				- EMPRESA_ID: ID numérico de la empresa a abrir
				- NOMBRE_PAQ: Nombre del PAQ (default: CONTPAQ I COMERCIAL)
		"""
		if not isinstance(config, dict):
			raise ValueError("config debe ser un diccionario con la configuración de SQL Server")

		self.driver = config.get("DRIVER", "{SQL Server}")
		self.server = config.get("SERVER")
		self.database = config.get("DATABASE")
		self.trusted_connection = config.get("Trusted_Connection", "yes")
		self.sql_user = config.get("SQL_USER", "")
		self.sql_password = config.get("SQL_PASSWORD", "")

		if not self.server or not self.database:
			raise ValueError("config debe incluir las llaves SERVER y DATABASE")

		self.sdk_path = config.get("PATH")
		self.sdk_user = config.get("USER", "SUPERVISOR")
		self.sdk_password = config.get("PASSWORD", "")
		self.contabilidad_user = config.get("CONTABILIDAD_USER", "")
		self.contabilidad_password = config.get("CONTABILIDAD_PASSWORD", "")
		self.ruta_empresa = config.get("RUTAEMPRESA")
		self.nombre_paq = config.get("NOMBRE_PAQ", "CONTPAQ I COMERCIAL")

		if not self.ruta_empresa:
			raise ValueError("config debe incluir la llave RUTAEMPRESA con la ruta de la empresa")

		# Validar conexión al inicializar
		self._get_connection()

	def _format_fecha(self, dt):
		"""Formatea un datetime a YYYYMMDDHHMMSSСCC (17 chars con milisegundos)."""
		return dt.strftime("%Y%m%d%H%M%S") + f"{dt.microsecond // 1000:03d}"

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

		# SQLite devuelve valores numéricos como int cuando la columna es DATETIME
		if isinstance(fecha, int):
			fecha = str(fecha)

		if not isinstance(fecha, str):
			raise ValueError(f"Formato de fecha inválido: {fecha}")
		
		fecha = fecha.strip()

		# Formatos numéricos propios PRIMERO (antes de fromisoformat, que en
		# Python 3.11 puede parsear strings de 17 dígitos de forma incorrecta)

		# Formato YYYYMMDDHHMMSSMMM (17 chars con milisegundos)
		if len(fecha) == 17:
			try:
				dt = datetime.strptime(fecha[:14], "%Y%m%d%H%M%S")
				return dt.replace(microsecond=int(fecha[14:17]) * 1000)
			except ValueError:
				pass

		# Formato YYYYMMDDHHMMSS (14 chars)
		if len(fecha) == 14:
			try:
				return datetime.strptime(fecha, "%Y%m%d%H%M%S")
			except ValueError:
				pass

		# Formato YYYYMMDD (8 chars)
		if len(fecha) == 8:
			try:
				return datetime.strptime(fecha, "%Y%m%d")
			except ValueError:
				pass

		# Último recurso: formato ISO con separadores (ej: '2026-04-21T11:05:15')
		try:
			return datetime.fromisoformat(fecha)
		except ValueError:
			pass

		raise ValueError(f"Formato de fecha no soportado: {fecha}. Use YYYYMMDDHHMMSSMMM (17), YYYYMMDDHHMMSS (14), YYYYMMDD (8) o ISO")

	def _get_connection(self):
		"""
		Establece y retorna una conexión a SQL Server.
		Usa autenticación Windows si Trusted_Connection=yes, o SQL Server si se proporcionan SQL_USER y SQL_PASSWORD.
		"""
		try:
			if self.trusted_connection.lower() == "yes":
				connection_string = f"Driver={self.driver};Server={self.server};Database={self.database};Trusted_Connection=yes;"
			else:
				if not self.sql_user:
					raise ValueError("Se requiere SQL_USER cuando Trusted_Connection no es 'yes'")
				connection_string = f"Driver={self.driver};Server={self.server};Database={self.database};UID={self.sql_user};PWD={self.sql_password};"
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
				fechaHoraDesde=self._format_fecha(fecha_desde),
				fechaHoraHasta=self._format_fecha(fecha_hasta),
				creacion_modificar_borrar=[]
			)

		# Obtener los artículos en el rango de fechas
		articulos = self._get_articulos(fecha_desde, fecha_hasta)

		return ContpaqArticuloCollection(
			tabla="dbo.admProductos",
			fechaHoraDesde=self._format_fecha(fecha_desde),
			fechaHoraHasta=self._format_fecha(fecha_hasta),
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
			ORDER BY CAST(CTIMESTAMP AS DATETIME) DESC
			"""

			cursor.execute(query, (fecha_desde,))
			result = cursor.fetchone()
			cursor.close()
			conn.close()

			if result:
				timestamp = result[0]
				# Si el timestamp es datetime lo retornamos, si es string lo convertimos
				if isinstance(timestamp, str):
					# El formato es 'MM/DD/YYYY HH:MM:SS:fff', convertir a 'MM/DD/YYYY HH:MM:SS.fff'
					timestamp = timestamp.rsplit(':', 1)[0] + '.' + timestamp.rsplit(':', 1)[1]
					return datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S.%f')
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
			ORDER BY CAST(CTIMESTAMP AS DATETIME) DESC
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
				fechaHoraDesde=self._format_fecha(fecha_desde),
				fechaHoraHasta=self._format_fecha(fecha_hasta),
				creacion_modificar_borrar=[]
			)

		# Obtener los clientes en el rango de fechas
		mailings = self._get_mailings(fecha_desde, fecha_hasta)

		return ContpaqMailingCollection(
			tabla="dbo.admClientes",
			fechaHoraDesde=self._format_fecha(fecha_desde),
			fechaHoraHasta=self._format_fecha(fecha_hasta),
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
			ORDER BY CAST(CTIMESTAMP AS DATETIME) DESC
			"""

			cursor.execute(query, (fecha_desde,))
			result = cursor.fetchone()
			cursor.close()
			conn.close()

			if result:
				timestamp = result[0]
				# Si el timestamp es datetime lo retornamos, si es string lo convertimos
				if isinstance(timestamp, str):
					# El formato es 'MM/DD/YYYY HH:MM:SS:fff', convertir a 'MM/DD/YYYY HH:MM:SS.fff'
					timestamp = timestamp.rsplit(':', 1)[0] + '.' + timestamp.rsplit(':', 1)[1]
					return datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S.%f')
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
			ORDER BY CAST(CTIMESTAMP AS DATETIME) DESC
			"""

			cursor.execute(query, (fecha_desde, fecha_hasta))
			rows = cursor.fetchall()
			cursor.close()
			conn.close()

			mailings = [self._map_mailing(row) for row in rows]
			return mailings

		except Exception as e:
			raise Exception(f"Error al obtener clientes de SQL Server: {str(e)}")

	def getArticleByID(self, articulo_id):
		"""
		Obtiene un artículo de Contpaq por CIDPRODUCTO.

		Args:
			articulo_id (int): ID del artículo en Contpaq.

		Returns:
			ContpaqArticuloAggregate: Aggregate del artículo encontrado o vacío
			si no existe.
		"""
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT TOP 1 CIDPRODUCTO, CCODIGOPRODUCTO, CNOMBREPRODUCTO, CTIPOPRODUCTO,
			       CFECHAALTAPRODUCTO, CFECHABAJA, CTIMESTAMP
			FROM dbo.admProductos
			WHERE CIDPRODUCTO = ?
			"""

			cursor.execute(query, (articulo_id,))
			row = cursor.fetchone()
			cursor.close()
			conn.close()

			if row:
				return self._map_articulo(row)

			return ContpaqArticuloAggregate()
		except Exception as e:
			raise Exception(f"Error al obtener artículo por ID en SQL Server: {str(e)}")

	def getMailingByID(self, mailing_id):
		"""
		Obtiene un mailing (cliente/proveedor) de Contpaq por CIDCLIENTEPROVEEDOR.

		Args:
			mailing_id (int): ID del mailing en Contpaq.

		Returns:
			ContpaqMailingAggregate: Aggregate del mailing encontrado o vacío
			si no existe.
		"""
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT TOP 1 CIDCLIENTEPROVEEDOR, CCODIGOCLIENTE, CRAZONSOCIAL,
			       CFECHAALTA, CRFC, CTIMESTAMP
			FROM dbo.admClientes
			WHERE CIDCLIENTEPROVEEDOR = ?
			"""

			cursor.execute(query, (mailing_id,))
			row = cursor.fetchone()
			cursor.close()
			conn.close()

			if row:
				return self._map_mailing(row)

			return ContpaqMailingAggregate()
		except Exception as e:
			raise Exception(f"Error al obtener mailing por ID en SQL Server: {str(e)}")

	def getLogisticArticleStock(self, articulo_logistica):
		"""
		Obtiene el stock neto de un artículo desde admMovimientos y actualiza
		el atributo StockActual del aggregate recibido.

		Args:
			articulo_logistica (ArticuloLogisticaAggregate): Aggregate con
				ContpaqArticuloID informado.

		Returns:
			ArticuloLogisticaAggregate: El mismo aggregate recibido, con
				StockActual actualizado.
		"""
		if articulo_logistica is None:
			raise ValueError("articulo_logistica es obligatorio")

		if articulo_logistica.ContpaqArticuloID is None:
			raise ValueError("ContpaqArticuloID es obligatorio para consultar stock")

		conn = None
		cursor = None
		try:
			conn = self._get_connection()
			cursor = conn.cursor()

			query = """
			SELECT
				admMovimientos.CIDPRODUCTO,
				SUM(
					CASE
						WHEN admMovimientos.CTIPOTRASPASO IN (1, 3) THEN admMovimientos.CUNIDADES
						WHEN admMovimientos.CTIPOTRASPASO = 2       THEN -admMovimientos.CUNIDADES
						ELSE 0
					END
				) AS CUNIDADES_NETAS
			FROM admMovimientos
			WHERE admMovimientos.CIDPRODUCTO = ?
			  AND admMovimientos.CAFECTADOINVENTARIO = 1
			GROUP BY
				admMovimientos.CIDPRODUCTO
			"""

			cursor.execute(query, (articulo_logistica.ContpaqArticuloID,))
			result = cursor.fetchone()

			if result and result[1] is not None:
				articulo_logistica.StockActual = float(result[1])
			else:
				articulo_logistica.StockActual = 0.0

			return articulo_logistica
		except Exception as e:
			raise Exception(f"Error al obtener stock logístico del artículo: {str(e)}")
		finally:
			if cursor is not None:
				cursor.close()
			if conn is not None:
				conn.close()

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

	# -------------------------------------------------------------------------
	# Métodos de escritura usando el SDK nativo de Contpaqi (MGWServicios.dll)
	# NOTA: La DLL es 32 bits. El proceso Python que ejecute estos métodos
	#       también debe ser de 32 bits (Python x86).
	# -------------------------------------------------------------------------

	def _iniciar_sdk(self):
		"""Carga la DLL, autentica, y abre la empresa. Returna (sdk, cwd_original)."""
		if not self.sdk_path:
			raise ValueError("config debe incluir la llave PATH para usar el SDK")

		dll_path = os.path.join(self.sdk_path, "MGWServicios.dll")
		cwd_original = os.getcwd()
		os.chdir(self.sdk_path)

		try:
			sdk = WinDLL(dll_path)
		except OSError as ex:
			os.chdir(cwd_original)
			raise OSError(
				f"No se pudo cargar MGWServicios.dll: {ex}. "
				"Verifique que el proceso Python sea de 32 bits (x86)."
			)

		# Estas funciones son void en la DLL — sin restype ctypes lee basura de EAX
		sdk.fInicioSesionSDK.restype = None
		sdk.fCierraEmpresa.restype = None
		sdk.fTerminaSDK.restype = None

		sdk.fInicioSesionSDK(
			self.sdk_user.encode("latin-1"),
			self.sdk_password.encode("latin-1"),
		)

		result = sdk.fSetNombrePAQ(self.nombre_paq.encode("latin-1"))
		if result != 0:
			sdk.fTerminaSDK()
			os.chdir(cwd_original)
			raise Exception(f"Error fSetNombrePAQ: código {result}")

		# Si hay credenciales de Contabilidad configuradas, autenticar en silencio
		# para evitar el diálogo de login que aparece al abrir empresas vinculadas.
		if self.contabilidad_user:
			if hasattr(sdk, "fInicioSesionContabilidadSDK"):
				sdk.fInicioSesionContabilidadSDK.restype = None
				sdk.fInicioSesionContabilidadSDK(
					self.contabilidad_user.encode("latin-1"),
					self.contabilidad_password.encode("latin-1"),
				)

		result = sdk.fAbreEmpresa(self.ruta_empresa.encode("latin-1"))
		if result != 0:
			sdk.fTerminaSDK()
			os.chdir(cwd_original)
			raise Exception(f"Error fAbreEmpresa: código {result}")

		return sdk, cwd_original

	def _cerrar_sdk(self, sdk, cwd_original):
		"""Cierra la empresa, termina el SDK y restaura el directorio de trabajo."""
		try:
			sdk.fCierraEmpresa()
			sdk.fTerminaSDK()
		finally:
			os.chdir(cwd_original)

	def _leer_error_sdk(self, sdk, codigo_error):
		"""Devuelve el mensaje de error en texto legible usando fError de la DLL."""
		sdk.fError.restype = None
		error_buf = create_string_buffer(512)
		sdk.fError(codigo_error, error_buf, 512)
		return error_buf.value.decode("latin-1", errors="replace")

	def createArticle(self, articulo):
		"""
		Crea un artículo en Contpaqi usando el SDK nativo (fAltaProducto).

		Args:
			articulo (ContpaqArticuloAggregate): Aggregate con los datos del artículo.
				Se usan: CCODIGOPRODUCTO, CNOMBREPRODUCTO, CTIPOPRODUCTO.

		Returns:
			int: ID del artículo creado (CIDPRODUCTO). También actualiza articulo.CIDPRODUCTO.

		Raises:
			Exception: Si el SDK devuelve un código de error distinto de 0.
		"""
		sdk, cwd = self._iniciar_sdk()
		try:
			producto = tProducto()
			producto.cCodigoProducto    = (articulo.CCODIGOPRODUCTO or "")[:30].encode("latin-1")
			producto.cNombreProducto    = (articulo.CNOMBREPRODUCTO or "")[:60].encode("latin-1")
			producto.cTipoProducto      = articulo.CTIPOPRODUCTO if articulo.CTIPOPRODUCTO is not None else 1
			producto.cFechaAltaProducto = date.today().strftime("%m/%d/%Y").encode("latin-1")
			producto.cStatusProducto    = 1

			nuevo_id = c_int(0)
			result = sdk.fAltaProducto(byref(nuevo_id), byref(producto))
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fAltaProducto al crear artículo: código {result} — {msg}")

			articulo.CIDPRODUCTO = nuevo_id.value
			return nuevo_id.value
		finally:
			self._cerrar_sdk(sdk, cwd)

	def createMailing(self, mailing):
		"""
		Crea un cliente/proveedor en Contpaqi usando el SDK nativo (fAltaCteProv).

		Args:
			mailing (ContpaqMailingAggregate): Aggregate con los datos del cliente.
				Se usan: CCODIGOCLIENTE, CRAZONSOCIAL, CRFC.

		Returns:
			int: ID del cliente creado (CIDCLIENTEPROVEEDOR).
				 También actualiza mailing.CIDCLIENTEPROVEEDOR.

		Raises:
			Exception: Si el SDK devuelve un código de error distinto de 0.
		"""
		sdk, cwd = self._iniciar_sdk()
		try:
			cliente = tCteProv()
			cliente.cCodigoCliente = (mailing.CCODIGOCLIENTE or "")[:30].encode("latin-1")
			cliente.cRazonSocial   = (mailing.CRAZONSOCIAL or "")[:60].encode("latin-1")
			cliente.cRFC           = (mailing.CRFC or "")[:20].encode("latin-1")
			cliente.cFechaAlta     = date.today().strftime("%m/%d/%Y").encode("latin-1")
			cliente.cTipoCliente   = 1   # Cliente
			cliente.cEstatus       = 1   # Activo

			nuevo_id = c_int(0)
			result = sdk.fAltaCteProv(byref(nuevo_id), byref(cliente))
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fAltaCteProv al crear cliente: código {result} — {msg}")

			mailing.CIDCLIENTEPROVEEDOR = nuevo_id.value
			return nuevo_id.value
		finally:
			self._cerrar_sdk(sdk, cwd)

	def createSalesOrderHeader(self, pedido):
		"""
		Crea el documento de un pedido de venta en Contpaqi usando el SDK nativo.

		Args:
			pedido (ContpaqPedidoVentaCabeceraAggregate): Aggregate con los datos
				de entrada del documento (CCODIGOCONCEPTO, CCODIGOCTEPROV,
				CFECHA, CSERIE, CFOLIO, CNUMMONEDA, CTIPOCAMBIO,
				CREFERENCIA).

		Returns:
			int: CIDDOCUMENTO generado. También actualiza el aggregate.

		Raises:
			Exception: Si el SDK devuelve un código de error distinto de 0.
		"""
		sdk, cwd = self._iniciar_sdk()
		try:
			fecha_doc = pedido.CFECHA or date.today().strftime("%m/%d/%Y")

			# Si no se proporcionó folio, obtener el siguiente automáticamente
			folio = pedido.CFOLIO
			serie_buf = create_string_buffer(12)
			if not folio:
				folio_ref = c_double(0.0)
				sdk.fSiguienteFolio.restype = c_int
				result = sdk.fSiguienteFolio(
					pedido.CCODIGOCONCEPTO.encode("latin-1"),
					serie_buf,
					byref(folio_ref),
				)
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSiguienteFolio: código {result} — {msg}")
				folio = folio_ref.value
				serie = serie_buf.value.decode("latin-1")
			else:
				serie = pedido.CSERIE

			# Paso 1: Crear el documento (encabezado del pedido)
			doc = tDocumento()
			doc.aCodConcepto   = pedido.CCODIGOCONCEPTO[:30].encode("latin-1")
			doc.aSerie         = serie[:11].encode("latin-1")
			doc.aFolio         = folio
			doc.aFecha         = fecha_doc[:23].encode("latin-1")
			doc.aCodigoCteProv = pedido.CCODIGOCTEPROV[:30].encode("latin-1")
			doc.aNumMoneda     = pedido.CNUMMONEDA
			doc.aTipoCambio    = pedido.CTIPOCAMBIO
			doc.aReferencia    = (pedido.CREFERENCIA or "")[:20].encode("latin-1")

			nuevo_doc_id = c_int(0)
			result = sdk.fAltaDocumento(byref(nuevo_doc_id), byref(doc))
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fAltaDocumento al crear pedido: código {result} — {msg}")

			pedido.CIDDOCUMENTO    = nuevo_doc_id.value

			return nuevo_doc_id.value
		finally:
			self._cerrar_sdk(sdk, cwd)

	def createSalesOrderLine(self, linea):
		"""
		Crea un movimiento de pedido de venta en un documento existente.

		Args:
			linea (ContpaqPedidoVentaLineaAggregate): Aggregate con los datos
				de entrada del movimiento (CIDDOCUMENTO, CCODIGOPRODUCTO,
				CUNIDADES, CPRECIO, CCODALMACEN, CREFERENCIA).

		Returns:
			int: CIDMOVIMIENTO generado. También actualiza el aggregate.

		Raises:
			Exception: Si el SDK devuelve un código de error distinto de 0.
		"""
		sdk, cwd = self._iniciar_sdk()
		try:
			if linea.CIDDOCUMENTO is None:
				raise ValueError("CIDDOCUMENTO es obligatorio para crear el movimiento")
			if not linea.CCODIGOPRODUCTO:
				raise ValueError("CCODIGOPRODUCTO es obligatorio para crear el movimiento")
			codigo_producto = str(linea.CCODIGOPRODUCTO).strip()
			if not codigo_producto:
				raise ValueError("CCODIGOPRODUCTO es obligatorio para crear el movimiento")

			sdk.fBuscarIdDocumento.restype = c_int
			sdk.fBuscarIdDocumento.argtypes = [c_int]
			sdk.fBuscaProducto.restype = c_int
			sdk.fBuscaProducto.argtypes = [ctypes.c_char_p]

			sdk.fAltaMovimiento.restype = c_int
			sdk.fAltaMovimiento.argtypes = [
				c_int,
				ctypes.POINTER(c_int),
				ctypes.POINTER(tMovimiento),
			]

			# Posicionar y validar documento para evitar alta sobre IDs inválidos.
			res_doc = sdk.fBuscarIdDocumento(int(linea.CIDDOCUMENTO))
			if res_doc != 0:
				msg = self._leer_error_sdk(sdk, res_doc)
				raise Exception(f"Documento no válido para crear movimiento (CIDDOCUMENTO={linea.CIDDOCUMENTO}): código {res_doc} — {msg}")

			# Validar que el producto exista antes de insertar el movimiento.
			res_prod = sdk.fBuscaProducto(codigo_producto.encode("latin-1"))
			if res_prod != 0:
				msg = self._leer_error_sdk(sdk, res_prod)
				raise Exception(f"Producto no válido para crear movimiento (CCODIGOPRODUCTO={codigo_producto}): código {res_prod} — {msg}")

			mov = tMovimiento()
			mov.aCodProdSer = codigo_producto[:30].encode("latin-1")
			mov.aUnidades = float(linea.CUNIDADES or 0.0)
			mov.aPrecio = float(linea.CPRECIO or 0.0)
			mov.aCodAlmacen = (linea.CCODALMACEN or "1")[:30].encode("latin-1")
			mov.aReferencia = (linea.CREFERENCIA or "")[:20].encode("latin-1")

			nuevo_mov_id = c_int(0)
			result = sdk.fAltaMovimiento(int(linea.CIDDOCUMENTO), byref(nuevo_mov_id), byref(mov))
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fAltaMovimiento al crear renglón: código {result} — {msg}")

			linea.CIDMOVIMIENTO = nuevo_mov_id.value
			linea.CNUMEROMOVIMIENTO = 1

			return nuevo_mov_id.value
		finally:
			self._cerrar_sdk(sdk, cwd)

	def updateArticle(self, articulo):
		"""
		Actualiza un artículo existente en Contpaqi usando el SDK nativo.

		Args:
			articulo (ContpaqArticuloAggregate): Aggregate con identificador y
				campos a actualizar (CCODIGOPRODUCTO, CNOMBREPRODUCTO).

		Returns:
			int: CIDPRODUCTO actualizado.
		"""
		if articulo is None:
			raise ValueError("articulo es obligatorio")
		if articulo.CIDPRODUCTO is None and not articulo.CCODIGOPRODUCTO:
			raise ValueError("CIDPRODUCTO o CCODIGOPRODUCTO es obligatorio para actualizar artículo")

		sdk, cwd = self._iniciar_sdk()
		try:
			sdk.fBuscaIdProducto.restype = c_int
			sdk.fBuscaIdProducto.argtypes = [c_int]
			sdk.fBuscaProducto.restype = c_int
			sdk.fBuscaProducto.argtypes = [ctypes.c_char_p]
			sdk.fEditaProducto.restype = c_int
			sdk.fSetDatoProducto.restype = c_int
			sdk.fSetDatoProducto.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
			sdk.fGuardaProducto.restype = c_int

			if articulo.CIDPRODUCTO is not None:
				result = sdk.fBuscaIdProducto(int(articulo.CIDPRODUCTO))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fBuscaIdProducto: código {result} — {msg}")
			else:
				result = sdk.fBuscaProducto(str(articulo.CCODIGOPRODUCTO).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fBuscaProducto: código {result} — {msg}")

			result = sdk.fEditaProducto()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fEditaProducto: código {result} — {msg}")

			if articulo.CCODIGOPRODUCTO is not None:
				result = sdk.fSetDatoProducto(b"CCODIGOPRODUCTO", str(articulo.CCODIGOPRODUCTO).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoProducto(CCODIGOPRODUCTO): código {result} — {msg}")

			if articulo.CNOMBREPRODUCTO is not None:
				result = sdk.fSetDatoProducto(b"CNOMBREPRODUCTO", str(articulo.CNOMBREPRODUCTO).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoProducto(CNOMBREPRODUCTO): código {result} — {msg}")

			result = sdk.fGuardaProducto()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fGuardaProducto: código {result} — {msg}")

			return articulo.CIDPRODUCTO
		finally:
			self._cerrar_sdk(sdk, cwd)

	def updateMailing(self, mailing):
		"""
		Actualiza un cliente/proveedor existente en Contpaqi usando el SDK nativo.

		Args:
			mailing (ContpaqMailingAggregate): Aggregate con identificador y
				campos a actualizar (CCODIGOCLIENTE, CRAZONSOCIAL, CRFC).

		Returns:
			int: CIDCLIENTEPROVEEDOR actualizado.
		"""
		if mailing is None:
			raise ValueError("mailing es obligatorio")
		if mailing.CIDCLIENTEPROVEEDOR is None and not mailing.CCODIGOCLIENTE:
			raise ValueError("CIDCLIENTEPROVEEDOR o CCODIGOCLIENTE es obligatorio para actualizar mailing")

		sdk, cwd = self._iniciar_sdk()
		try:
			sdk.fBuscaIdCteProv.restype = c_int
			sdk.fBuscaIdCteProv.argtypes = [c_int]
			sdk.fBuscaCteProv.restype = c_int
			sdk.fBuscaCteProv.argtypes = [ctypes.c_char_p]
			sdk.fEditaCteProv.restype = c_int
			sdk.fSetDatoCteProv.restype = c_int
			sdk.fSetDatoCteProv.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
			sdk.fGuardaCteProv.restype = c_int

			if mailing.CIDCLIENTEPROVEEDOR is not None:
				result = sdk.fBuscaIdCteProv(int(mailing.CIDCLIENTEPROVEEDOR))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fBuscaIdCteProv: código {result} — {msg}")
			else:
				result = sdk.fBuscaCteProv(str(mailing.CCODIGOCLIENTE).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fBuscaCteProv: código {result} — {msg}")

			result = sdk.fEditaCteProv()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fEditaCteProv: código {result} — {msg}")

			if mailing.CCODIGOCLIENTE is not None:
				result = sdk.fSetDatoCteProv(b"CCODIGOCLIENTE", str(mailing.CCODIGOCLIENTE).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoCteProv(CCODIGOCLIENTE): código {result} — {msg}")

			if mailing.CRAZONSOCIAL is not None:
				result = sdk.fSetDatoCteProv(b"CRAZONSOCIAL", str(mailing.CRAZONSOCIAL).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoCteProv(CRAZONSOCIAL): código {result} — {msg}")

			if mailing.CRFC is not None:
				result = sdk.fSetDatoCteProv(b"CRFC", str(mailing.CRFC).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoCteProv(CRFC): código {result} — {msg}")

			result = sdk.fGuardaCteProv()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fGuardaCteProv: código {result} — {msg}")

			return mailing.CIDCLIENTEPROVEEDOR
		finally:
			self._cerrar_sdk(sdk, cwd)

	def updateSalesOrderHeader(self, pedido):
		"""
		Actualiza una cabecera de pedido de venta usando el SDK nativo.
		"""
		if pedido is None:
			raise ValueError("pedido es obligatorio")
		if pedido.CIDDOCUMENTO is None:
			raise ValueError("CIDDOCUMENTO es obligatorio para actualizar cabecera")

		if pedido.COBSERVACIONES is None and pedido.CREFERENCIA is None:
			return pedido.CIDDOCUMENTO

		sdk, cwd = self._iniciar_sdk()
		try:
			sdk.fBuscarIdDocumento.restype = c_int
			sdk.fBuscarIdDocumento.argtypes = [c_int]
			sdk.fEditarDocumento.restype = c_int
			sdk.fSetDatoDocumento.restype = c_int
			sdk.fSetDatoDocumento.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
			sdk.fGuardaDocumento.restype = c_int

			result = sdk.fBuscarIdDocumento(int(pedido.CIDDOCUMENTO))
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fBuscarIdDocumento: código {result} — {msg}")

			result = sdk.fEditarDocumento()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fEditarDocumento: código {result} — {msg}")

			if pedido.COBSERVACIONES is not None:
				result = sdk.fSetDatoDocumento(b"COBSERVACIONES", str(pedido.COBSERVACIONES).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoDocumento(COBSERVACIONES): código {result} — {msg}")

			if pedido.CREFERENCIA is not None:
				result = sdk.fSetDatoDocumento(b"CREFERENCIA", str(pedido.CREFERENCIA).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoDocumento(CREFERENCIA): código {result} — {msg}")

			result = sdk.fGuardaDocumento()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fGuardaDocumento: código {result} — {msg}")

			return pedido.CIDDOCUMENTO
		finally:
			self._cerrar_sdk(sdk, cwd)

	def updateSalesOrderLine(self, linea):
		"""
		Actualiza una línea de pedido de venta usando el SDK nativo.
		"""
		if linea is None:
			raise ValueError("linea es obligatoria")
		if linea.CIDMOVIMIENTO is None:
			raise ValueError("CIDMOVIMIENTO es obligatorio para actualizar línea")

		if linea.CUNIDADES is None and linea.CPRECIO is None and linea.CREFERENCIA is None:
			return linea.CIDMOVIMIENTO

		sdk, cwd = self._iniciar_sdk()
		try:
			sdk.fBuscarIdMovimiento.restype = c_int
			sdk.fBuscarIdMovimiento.argtypes = [c_int]
			sdk.fEditarMovimiento.restype = c_int
			sdk.fSetDatoMovimiento.restype = c_int
			sdk.fSetDatoMovimiento.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
			sdk.fGuardaMovimiento.restype = c_int

			result = sdk.fBuscarIdMovimiento(int(linea.CIDMOVIMIENTO))
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fBuscarIdMovimiento: código {result} — {msg}")

			result = sdk.fEditarMovimiento()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fEditarMovimiento: código {result} — {msg}")

			if linea.CUNIDADES is not None:
				result = sdk.fSetDatoMovimiento(b"CUNIDADES", str(float(linea.CUNIDADES)).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoMovimiento(CUNIDADES): código {result} — {msg}")

			if linea.CPRECIO is not None:
				result = sdk.fSetDatoMovimiento(b"CPRECIO", str(float(linea.CPRECIO)).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoMovimiento(CPRECIO): código {result} — {msg}")

			if linea.CREFERENCIA is not None:
				result = sdk.fSetDatoMovimiento(b"CREFERENCIA", str(linea.CREFERENCIA).encode("latin-1"))
				if result != 0:
					msg = self._leer_error_sdk(sdk, result)
					raise Exception(f"Error fSetDatoMovimiento(CREFERENCIA): código {result} — {msg}")

			result = sdk.fGuardaMovimiento()
			if result != 0:
				msg = self._leer_error_sdk(sdk, result)
				raise Exception(f"Error fGuardaMovimiento: código {result} — {msg}")

			return linea.CIDMOVIMIENTO
		finally:
			self._cerrar_sdk(sdk, cwd)
