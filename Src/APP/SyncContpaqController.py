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
from DOM.ContpaqPedidoVentaLineaAggregate import ContpaqPedidoVentaLineaAggregate
from DOM.NetvyArticuloAggregate import NetvyArticuloAggregate
from DOM.NetvyMailingAggregate import NetvyMailingAggregate

_APP_NAME = "SincronizadorContpaqi"


class SyncContpaqController:

	def __init__(self, config):
		self._interval = config["GENERAL"]["TIME"]
		self._iteracion = 0

		self._sqllite  = SQLLiteRepository(config["SQLLITE"])
		self._netvy    = ApiNetvyRepository(config["NETVY"])
		self._contpaq  = SDKContpaqRepository(config["CONTPAQ"])

		# Fechas de última sincronización (se cargan en init())
		self.fecha_mailing_netvy                 = None
		self.fecha_articulo_netvy                = None
		self.fecha_pedido_venta_cabecera_netvy   = None
		self.fecha_pedido_venta_linea_netvy      = None
		self.fecha_mailing_contpaq               = None
		self.fecha_articulo_contpaq              = None
		self.fecha_pedido_venta_cabecera_contpaq = None
		self.fecha_pedido_venta_linea_contpaq    = None

	def init(self):
		# 1. Cargar variables globales de Netvy (FamiliaID, MonedaID, token)
		self._netvy.login()
		self._netvy.getFamilyConfig()
		self._netvy.getCurrencieConfig()
		self._netvy.getConfigTipoDocumentoID()
		self._netvy.getConfigTipoPersonaID()

		# 2. Inicializar SQLite (crea el archivo y las tablas si no existen)
		self._sqllite.init()

		# 3. Asegurar registros base en FechaSincronizacion
		self._sqllite.asegurar_fechas_sincronizacion()

		# 4. Cargar fechas en atributos locales
		fechas = self._sqllite.get_fechas_sincronizacion()
		for attr, valor in fechas.items():
			setattr(self, attr, valor)

	def run(self, stop_event=None):
		try:
			self.init()
			self._log_info("Inicialización completada. Iniciando ciclo de sincronización.")
		except Exception as ex:
			self._log_error(f"Error crítico en init, el sincronizador no puede arrancar: {ex}")
			return
		while True:
			if stop_event is not None and stop_event.is_set():
				self._log_info("Se recibió señal de parada. Finalizando servicio.")
				return
			self._sincronizar()
			if stop_event is None:
				time.sleep(self._interval)
			else:
				stop_event.wait(self._interval)

	def _sincronizar(self):
		self._iteracion += 1
		inicio = datetime.now()
		self._log_info(f"=== Iteración {self._iteracion} iniciada: {inicio.isoformat()} ===")
		self.syncNetvy()
		self.syncContpaq()
		fin = datetime.now()
		duracion = (fin - inicio).total_seconds()
		self._log_info(f"=== Iteración {self._iteracion} finalizada: {fin.isoformat()} (duración {duracion:.2f}s) ===")

	# -------------------------------------------------------------------------
	# Sincronización Netvy → Contpaq
	# -------------------------------------------------------------------------

	def syncContpaq(self):
		self._log_info("[Netvy -> Contpaq] Inicio de sincronización")
		# 1. Obtener colecciones desde Netvy
		articulos_netvy = None
		mailings_netvy  = None
		pedidos_netvy   = None
		lineas_netvy    = None

		try:
			self._log_info(f"[Netvy -> Contpaq] Buscando artículos desde fecha: {self.fecha_articulo_netvy}")
			articulos_netvy = self._netvy.getArticles(self.fecha_articulo_netvy)
			if articulos_netvy:
				self._log_info(f"[Netvy -> Contpaq] Artículos fechaHoraHasta recibida: {articulos_netvy.fechaHoraHasta}")
		except Exception as ex:
			self._log_error(f"getArticles Netvy falló: {ex}")

		try:
			self._log_info(f"[Netvy -> Contpaq] Buscando mailings desde fecha: {self.fecha_mailing_netvy}")
			mailings_netvy = self._netvy.getMailings(self.fecha_mailing_netvy)
			if mailings_netvy:
				self._log_info(f"[Netvy -> Contpaq] Mailings fechaHoraHasta recibida: {mailings_netvy.fechaHoraHasta}")
		except Exception as ex:
			self._log_error(f"getMailings Netvy falló: {ex}")

		try:
			self._log_info(f"[Netvy -> Contpaq] Buscando cabeceras de pedido desde fecha: {self.fecha_pedido_venta_cabecera_netvy}")
			pedidos_netvy = self._netvy.getPedidoVentaCabecera(self.fecha_pedido_venta_cabecera_netvy)
			if pedidos_netvy:
				self._log_info(f"[Netvy -> Contpaq] Cabeceras fechaHoraHasta recibida: {pedidos_netvy.fechaHoraHasta}")
		except Exception as ex:
			self._log_error(f"getPedidoVentaCabecera Netvy falló: {ex}")

		try:
			self._log_info(f"[Netvy -> Contpaq] Buscando líneas de pedido desde fecha: {self.fecha_pedido_venta_linea_netvy}")
			lineas_netvy = self._netvy.getSalesOrderLine(self.fecha_pedido_venta_linea_netvy)
			if lineas_netvy:
				self._log_info(f"[Netvy -> Contpaq] Líneas fechaHoraHasta recibida: {lineas_netvy.fechaHoraHasta}")
		except Exception as ex:
			self._log_error(f"getSalesOrderLine Netvy falló: {ex}")

		# 2. Crear artículos en Contpaq
		self._log_info("[Netvy -> Contpaq] Procesando artículos")
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
		self._log_info("[Netvy -> Contpaq] Procesando mailings")
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

		# 4. Crear cabeceras de pedido de venta en Contpaq
		self._log_info("[Netvy -> Contpaq] Procesando cabeceras de pedidos")
		if pedidos_netvy:
			for netvy_ped in pedidos_netvy.creacion:
				if netvy_ped.PedidoVentaCabeceraID is None:
					continue
				if self._sqllite.existe_sincronizacion_por_netvy_id("PedidoVentaCabecera", netvy_ped.PedidoVentaCabeceraID):
					continue
				try:
					contpaq_ped = ContpaqPedidoVentaCabeceraAggregate(
						CIDDOCUMENTO=None,
						CIDDOCUMENTODE=None,
						CCODIGOCONCEPTO="2",        # TODO: mapear desde config cuando esté disponible
						CCODIGOCTEPROV=netvy_ped.Codigo or "",
						CREFERENCIA=netvy_ped.ReferenciaNuestra or "",
					)
					self._contpaq.createSalesOrderHeader(contpaq_ped)
					self._sqllite.crear_sincronizacion("PedidoVentaCabecera", netvy_ped.PedidoVentaCabeceraID, contpaq_ped.CIDDOCUMENTO, self.fecha_pedido_venta_cabecera_netvy)
				except Exception as ex:
					self._log_error(
						f"createSalesOrderHeader Contpaq falló "
						f"(referencia={netvy_ped.ReferenciaNuestra}): {ex}"
					)

		# 5. Crear líneas de pedido de venta en Contpaq
		self._log_info("[Netvy -> Contpaq] Procesando líneas de pedidos")
		if lineas_netvy:
			for netvy_linea in lineas_netvy.creacion:
				if netvy_linea.PedidoVentaLineaID is None:
					continue
				if self._sqllite.existe_sincronizacion_por_netvy_id("PedidoVentaLinea", netvy_linea.PedidoVentaLineaID):
					continue
				cid_documento = self._sqllite.get_contpaq_id_por_netvy_id("PedidoVentaCabecera", netvy_linea.PedidoVentaCabeceraID)
				if cid_documento is None:
					continue
				try:
					contpaq_linea = ContpaqPedidoVentaLineaAggregate(
						CIDMOVIMIENTO=None,
						CNUMEROMOVIMIENTO=None,
						CIDDOCUMENTO=cid_documento,
						CIDPRODUCTO=None,
						CCODIGOPRODUCTO=netvy_linea.Codigo or "",
						CUNIDADES=netvy_linea.Cantidad or 0.0,
						CPRECIO=netvy_linea.PrecioVenta or 0.0,
						CREFERENCIA=netvy_linea.Referencia or "",
					)
					self._contpaq.createSalesOrderLine(contpaq_linea)
					self._sqllite.crear_sincronizacion("PedidoVentaLinea", netvy_linea.PedidoVentaLineaID, contpaq_linea.CIDMOVIMIENTO, self.fecha_pedido_venta_linea_netvy)
				except Exception as ex:
					self._log_error(
						f"createSalesOrderLine Contpaq falló "
						f"(lineaID={netvy_linea.PedidoVentaLineaID}): {ex}"
					)

		# 6. Actualizar fechas de sincronización
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

		if lineas_netvy and lineas_netvy.fechaHoraHasta:
			try:
				fecha = self._normalizar_fecha(lineas_netvy.fechaHoraHasta)
				self._sqllite.actualizar_fecha_sincronizacion("PedidoVentaLinea", "Netvy", fecha)
				self.fecha_pedido_venta_linea_netvy = fecha
			except Exception as ex:
				self._log_error(f"actualizar_fecha_sincronizacion PedidoVentaLinea/Netvy falló: {ex}")

		self._log_info("[Netvy -> Contpaq] Fin de sincronización")

	def _normalizar_fecha(self, fecha):
		"""Convierte cualquier formato de fecha a YYYYMMDDHHMMSSСCC (17 chars) para uso consistente."""
		if not fecha:
			return fecha
		if isinstance(fecha, datetime):
			return fecha.strftime("%Y%m%d%H%M%S") + f"{fecha.microsecond // 1000:03d}"
		s = str(fecha)
		if len(s) == 17:  # Ya en formato correcto YYYYMMDDHHMMSSMMM
			return s
		if len(s) == 14:  # YYYYMMDDHHMMSS — agregar 000 de milisegundos
			return s + "000"
		try:
			dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
			return dt.strftime("%Y%m%d%H%M%S") + f"{dt.microsecond // 1000:03d}"
		except ValueError:
			pass
		# Cualquier otro formato no reconocido: devolver tal cual
		return fecha

	def _log_error(self, mensaje):
		print(f"[ERROR] {mensaje}")
		try:
			win32evtlogutil.ReportEvent(
				appName=_APP_NAME,
				eventID=2,
				eventType=win32evtlog.EVENTLOG_ERROR_TYPE,
				strings=[mensaje],
			)
		except Exception:
			pass

	def _log_info(self, mensaje):
		print(f"[INFO] {mensaje}")
		try:
			win32evtlogutil.ReportEvent(
				appName=_APP_NAME,
				eventID=1,
				eventType=win32evtlog.EVENTLOG_INFORMATION_TYPE,
				strings=[mensaje],
			)
		except Exception:
			pass

	# -------------------------------------------------------------------------
	# Sincronización Contpaq → Netvy
	# -------------------------------------------------------------------------

	def syncNetvy(self):
		self._log_info("[Contpaq -> Netvy] Inicio de sincronización")
		# 1. Obtener colecciones desde Contpaq
		articulos_contpaq = None
		mailings_contpaq  = None

		try:
			self._log_info(f"[Contpaq -> Netvy] Buscando artículos desde fecha: {self.fecha_articulo_contpaq}")
			articulos_contpaq = self._contpaq.getArticles(self.fecha_articulo_contpaq)
			if articulos_contpaq:
				self._log_info(f"[Contpaq -> Netvy] Artículos fechaHoraHasta recibida: {articulos_contpaq.fechaHoraHasta}")
		except Exception as ex:
			self._log_error(f"getArticles Contpaq falló: {ex}")

		try:
			self._log_info(f"[Contpaq -> Netvy] Buscando mailings desde fecha: {self.fecha_mailing_contpaq}")
			mailings_contpaq = self._contpaq.getMailings(self.fecha_mailing_contpaq)
			if mailings_contpaq:
				self._log_info(f"[Contpaq -> Netvy] Mailings fechaHoraHasta recibida: {mailings_contpaq.fechaHoraHasta}")
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
						TipoDocumentoID=init.NetvyTipoDocumentoID,
						TipoPersonaID=init.NetvyTipoPersonaID,
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

		self._log_info("[Contpaq -> Netvy] Fin de sincronización")

