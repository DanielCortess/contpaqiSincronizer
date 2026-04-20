import time
from datetime import datetime
import win32evtlog
import win32evtlogutil

from APP import init
from INF.SQLLiteRepository import SQLLiteRepository
from INF.ApiNetvyRepository import ApiNetvyRepository
from INF.SDKContpaqRepository import SDKContpaqRepository
from DOM.ContpaqArticuloAggregate import ContpaqArticuloAggregate
from DOM.ContpaqMailingAggregate import ContpaqMailingAggregate
from DOM.ContpaqPedidoVentaCabeceraAggregate import ContpaqPedidoVentaCabeceraAggregate
from DOM.NetvyArticuloAggregate import NetvyArticuloAggregate
from DOM.NetvyMailingAggregate import NetvyMailingAggregate

_APP_NAME = "SincronizadorContpaqi"


class SyncContpaqController:

	def __init__(self, config):
		self._interval = config["GENERAL"]["TIME"]

		self._sqllite  = SQLLiteRepository(config["SQLLITE"])
		self._netvy    = ApiNetvyRepository(config["NETVY"])
		self._contpaq  = SDKContpaqRepository(config["CONTPAQ"])

		# Fechas de última sincronización (se cargan en init())
		self.fecha_mailing_netvy                 = None
		self.fecha_articulo_netvy                = None
		self.fecha_pedido_venta_cabecera_netvy   = None
		self.fecha_mailing_contpaq               = None
		self.fecha_articulo_contpaq              = None
		self.fecha_pedido_venta_cabecera_contpaq = None

	def init(self):
		# 1. Cargar variables globales de Netvy (FamiliaID, MonedaID, token)
		self._netvy.login()
		self._netvy.getFamilyConfig()
		self._netvy.getCurrencieConfig()

		# 2. Inicializar SQLite (crea el archivo y las tablas si no existen)
		self._sqllite.init()

		# 3. Asegurar registros base en FechaSincronizacion
		self._sqllite.asegurar_fechas_sincronizacion()

		# 4. Cargar fechas en atributos locales
		fechas = self._sqllite.get_fechas_sincronizacion()
		for attr, valor in fechas.items():
			setattr(self, attr, valor)

	def run(self):
		self.init()
		while True:
			self._sincronizar()
			time.sleep(self._interval)

	def _sincronizar(self):
		self.syncNetvy()
		self.syncContpaq()

	# -------------------------------------------------------------------------
	# Sincronización Netvy → Contpaq
	# -------------------------------------------------------------------------

	def syncContpaq(self):
		# 1. Obtener colecciones desde Netvy
		articulos_netvy = None
		mailings_netvy  = None
		pedidos_netvy   = None

		try:
			articulos_netvy = self._netvy.getArticles(self.fecha_articulo_netvy)
		except Exception as ex:
			self._log_error(f"getArticles Netvy falló: {ex}")

		try:
			mailings_netvy = self._netvy.getMailings(self.fecha_mailing_netvy)
		except Exception as ex:
			self._log_error(f"getMailings Netvy falló: {ex}")

		try:
			pedidos_netvy = self._netvy.getPedidoVentaCabecera(self.fecha_pedido_venta_cabecera_netvy)
		except Exception as ex:
			self._log_error(f"getPedidoVentaCabecera Netvy falló: {ex}")

		# 2. Crear artículos en Contpaq
		if articulos_netvy:
			for netvy_art in articulos_netvy.creacion:
				if netvy_art.ArticuloID is None:
					continue
				if self._sqllite.existe_sincronizacion_por_netvy_id("Articulo", netvy_art.ArticuloID):
					continue
				try:
					contpaq_art = ContpaqArticuloAggregate(
						CCODIGOPRODUCTO=netvy_art.Codigo,
						CNOMBREPRODUCTO=netvy_art.Nombre,
						CTIPOPRODUCTO=1,
					)
					self._contpaq.createArticle(contpaq_art)
					self._sqllite.crear_sincronizacion("Articulo", netvy_art.ArticuloID, contpaq_art.CIDPRODUCTO, self.fecha_articulo_netvy)
				except Exception as ex:
					self._log_error(
						f"createArticle Contpaq falló "
						f"(codigo={netvy_art.Codigo}): {ex}"
					)

		# 3. Crear mailings en Contpaq
		if mailings_netvy:
			for netvy_mail in mailings_netvy.creacion:
				if netvy_mail.MailingID is None:
					continue
				if self._sqllite.existe_sincronizacion_por_netvy_id("Mailing", netvy_mail.MailingID):
					continue
				try:
					contpaq_mail = ContpaqMailingAggregate(
						CCODIGOCLIENTE=netvy_mail.ReferenciaCodigo,
						CRAZONSOCIAL=netvy_mail.Nombre,
						CRFC=netvy_mail.Cif,
					)
					self._contpaq.createMailing(contpaq_mail)
					self._sqllite.crear_sincronizacion("Mailing", netvy_mail.MailingID, contpaq_mail.CIDCLIENTEPROVEEDOR, self.fecha_mailing_netvy)
				except Exception as ex:
					self._log_error(
						f"createMailing Contpaq falló "
						f"(codigo={netvy_mail.ReferenciaCodigo}): {ex}"
					)

		# 4. Crear pedidos de venta en Contpaq
		if pedidos_netvy:
			for netvy_ped in pedidos_netvy.creacion:
				if netvy_ped.PedidoVentaCabeceraID is None:
					continue
				if self._sqllite.existe_sincronizacion_por_netvy_id("PedidoVentaCabecera", netvy_ped.PedidoVentaCabeceraID):
					continue
				try:
					contpaq_ped = ContpaqPedidoVentaCabeceraAggregate(
						CIDMOVIMIENTO=None,
						CIDDOCUMENTO=None,
						CNUMEROMOVIMIENTO=None,
						CIDDOCUMENTODE=None,
						CIDPRODUCTO=None,
						CCODIGOCONCEPTO="2",        # TODO: mapear desde config cuando esté disponible
						CCODIGOCTEPROV="12345",     # TODO: reemplazar cuando Netvy exponga el código
						CCODIGOPRODUCTO="12345P",   # TODO: reemplazar cuando las líneas del pedido estén disponibles
						CUNIDADES=1.0,
						CPRECIO=0.0,
						CREFERENCIA=netvy_ped.ReferenciaNuestra or "",
					)
					self._contpaq.createSalesOrderHeader(contpaq_ped)
					self._sqllite.crear_sincronizacion("PedidoVentaCabecera", netvy_ped.PedidoVentaCabeceraID, contpaq_ped.CIDDOCUMENTO, self.fecha_pedido_venta_cabecera_netvy)
				except Exception as ex:
					self._log_error(
						f"createSalesOrderHeader Contpaq falló "
						f"(referencia={netvy_ped.ReferenciaNuestra}): {ex}"
					)

		# 5. Actualizar fechas de sincronización
		if articulos_netvy and articulos_netvy.fechaHoraHasta:
			try:
				fecha = self._normalizar_fecha(articulos_netvy.fechaHoraHasta)
				self._sqllite.actualizar_fecha_sincronizacion("Articulo", "Netvy", fecha)
				self.fecha_articulo_netvy = fecha
			except Exception as ex:
				self._log_error(f"actualizar_fecha_sincronizacion Articulo/Netvy falló: {ex}")

		if mailings_netvy and mailings_netvy.fechaHoraHasta:
			try:
				fecha = self._normalizar_fecha(mailings_netvy.fechaHoraHasta)
				self._sqllite.actualizar_fecha_sincronizacion("Mailing", "Netvy", fecha)
				self.fecha_mailing_netvy = fecha
			except Exception as ex:
				self._log_error(f"actualizar_fecha_sincronizacion Mailing/Netvy falló: {ex}")

		if pedidos_netvy and pedidos_netvy.fechaHoraHasta:
			try:
				fecha = self._normalizar_fecha(pedidos_netvy.fechaHoraHasta)
				self._sqllite.actualizar_fecha_sincronizacion("PedidoVentaCabecera", "Netvy", fecha)
				self.fecha_pedido_venta_cabecera_netvy = fecha
			except Exception as ex:
				self._log_error(f"actualizar_fecha_sincronizacion PedidoVentaCabecera/Netvy falló: {ex}")

	def _normalizar_fecha(self, fecha):
		"""Convierte cualquier formato de fecha a YYYYMMDDHHMMSSСCC (17 chars) para uso consistente."""
		if not fecha:
			return fecha
		if isinstance(fecha, datetime):
			return fecha.strftime("%Y%m%d%H%M%S") + f"{fecha.microsecond // 1000:03d}"
		try:
			dt = datetime.fromisoformat(str(fecha).replace("Z", "+00:00"))
			return dt.strftime("%Y%m%d%H%M%S") + f"{dt.microsecond // 1000:03d}"
		except ValueError:
			pass
		s = str(fecha)
		if len(s) == 14:  # YYYYMMDDHHMMSS — agregar 000 de milisegundos
			return s + "000"
		if len(s) == 17:  # Ya en formato correcto
			return s
		# Cualquier otro formato soportado: devolver tal cual
		return fecha

	def _log_error(self, mensaje):
		try:
			win32evtlogutil.ReportEvent(
				appName=_APP_NAME,
				eventID=1,
				eventType=win32evtlog.EVENTLOG_WARNING_TYPE,
				strings=[mensaje],
			)
		except Exception:
			pass

	# -------------------------------------------------------------------------
	# Sincronización Contpaq → Netvy
	# -------------------------------------------------------------------------

	def syncNetvy(self):
		# 1. Obtener colecciones desde Contpaq
		articulos_contpaq = None
		mailings_contpaq  = None

		try:
			articulos_contpaq = self._contpaq.getArticles(self.fecha_articulo_contpaq)
		except Exception as ex:
			self._log_error(f"getArticles Contpaq falló: {ex}")

		try:
			mailings_contpaq = self._contpaq.getMailings(self.fecha_mailing_contpaq)
		except Exception as ex:
			self._log_error(f"getMailings Contpaq falló: {ex}")

		# 2. Crear artículos en Netvy
		if articulos_contpaq:
			for contpaq_art in articulos_contpaq.creacion_modificar_borrar:
				if contpaq_art.CIDPRODUCTO is None:
					continue
				if self._sqllite.existe_sincronizacion_por_contpaq_id("Articulo", contpaq_art.CIDPRODUCTO):
					continue
				try:
					netvy_art = NetvyArticuloAggregate(
						Codigo=contpaq_art.CCODIGOPRODUCTO,
						Nombre=contpaq_art.CNOMBREPRODUCTO,
						Descripcion=contpaq_art.CNOMBREPRODUCTO,
						Activo=True,
					)
					self._netvy.createArticle(netvy_art)
					self._sqllite.crear_sincronizacion("Articulo", netvy_art.ArticuloID, contpaq_art.CIDPRODUCTO, self.fecha_articulo_contpaq)
				except Exception as ex:
					self._log_error(
						f"createArticle Netvy falló "
						f"(codigo={contpaq_art.CCODIGOPRODUCTO}): {ex}"
					)

		# 3. Crear mailings en Netvy
		if mailings_contpaq:
			for contpaq_mail in mailings_contpaq.creacion_modificar_borrar:
				if contpaq_mail.CIDCLIENTEPROVEEDOR is None:
					continue
				if self._sqllite.existe_sincronizacion_por_contpaq_id("Mailing", contpaq_mail.CIDCLIENTEPROVEEDOR):
					continue
				try:
					netvy_mail = NetvyMailingAggregate(
						ReferenciaCodigo=contpaq_mail.CCODIGOCLIENTE,
						Nombre=contpaq_mail.CRAZONSOCIAL,
						Cif=contpaq_mail.CRFC,
					)
					self._netvy.createMailing(netvy_mail)
					self._sqllite.crear_sincronizacion("Mailing", netvy_mail.MailingID, contpaq_mail.CIDCLIENTEPROVEEDOR, self.fecha_mailing_contpaq)
				except Exception as ex:
					self._log_error(
						f"createMailing Netvy falló "
						f"(codigo={contpaq_mail.CCODIGOCLIENTE}): {ex}"
					)

		# 4. Actualizar fechas de sincronización
		if articulos_contpaq and articulos_contpaq.fechaHoraHasta:
			try:
				fecha = self._normalizar_fecha(articulos_contpaq.fechaHoraHasta)
				self._sqllite.actualizar_fecha_sincronizacion("Articulo", "Contpaq", fecha)
				self.fecha_articulo_contpaq = fecha
			except Exception as ex:
				self._log_error(f"actualizar_fecha_sincronizacion Articulo/Contpaq falló: {ex}")

		if mailings_contpaq and mailings_contpaq.fechaHoraHasta:
			try:
				fecha = self._normalizar_fecha(mailings_contpaq.fechaHoraHasta)
				self._sqllite.actualizar_fecha_sincronizacion("Mailing", "Contpaq", fecha)
				self.fecha_mailing_contpaq = fecha
			except Exception as ex:
				self._log_error(f"actualizar_fecha_sincronizacion Mailing/Contpaq falló: {ex}")

