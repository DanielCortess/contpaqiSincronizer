import time
import threading
from datetime import datetime
import win32evtlog
import win32evtlogutil

from APP import init
from INF.SQLLiteRepository import SQLLiteRepository
from INF.SQLLiteStockRepository import SQLLiteStockRepository
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
		self._stock_sync_thread = None
		self._stock_sync_lock = threading.Lock()
		self._articulos_actualizar_netvy = []
		self._mailings_actualizar_netvy = []
		self._articulos_actualizar_contpaq = []
		self._mailings_actualizar_contpaq = []
		self._pending_sync_dates = {}

		self._sqllite       = SQLLiteRepository(config["SQLLITE"])
		self._sqllite_stock = SQLLiteStockRepository(config["SQLLITE_STOCK"])
		self._netvy         = ApiNetvyRepository(config["NETVY"])
		self._contpaq       = SDKContpaqRepository(config["CONTPAQ"])

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
		# self._netvy.getConfigTipoDocumentoID()
		# self._netvy.getConfigTipoPersonaID()

		# 2. Inicializar SQLite (crea el archivo y las tablas si no existen)
		self._sqllite.init()
		self._sqllite_stock.init()

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
		self._articulos_actualizar_netvy = []
		self._mailings_actualizar_netvy = []
		self._articulos_actualizar_contpaq = []
		self._mailings_actualizar_contpaq = []
		self._pending_sync_dates = {}
		self.syncNetvy()
		self.syncContpaq()
		self.cleanUpdates()
		self.syncNetvyUpdates()
		self.syncContpaqUpdates()
		self.updateSyncDates()
		fin = datetime.now()
		duracion = (fin - inicio).total_seconds()
		self._log_info(f"=== Iteración {self._iteracion} finalizada: {fin.isoformat()} (duración {duracion:.2f}s) ===")

	# -------------------------------------------------------------------------
	# Sincronización Netvy → Contpaq
	# -------------------------------------------------------------------------

	def syncContpaq(self):
		self._log_info("[Netvy -> Contpaq] Inicio de sincronización")
		articulos_actualizar_contpaq = self._articulos_actualizar_contpaq
		mailings_actualizar_contpaq = self._mailings_actualizar_contpaq
		articulos_actualizar_contpaq_ids = set()
		mailings_actualizar_contpaq_ids = set()
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
					self._agregar_articulo_actualizar_contpaq_si_aplica(
						netvy_art,
						articulos_actualizar_contpaq,
						articulos_actualizar_contpaq_ids,
					)
					continue
				try:
					contpaq_art = ContpaqArticuloAggregate(
						CCODIGOPRODUCTO=netvy_art.Codigo,
						CNOMBREPRODUCTO=netvy_art.Nombre,
						CTIPOPRODUCTO=1,
					)
					self._contpaq.createArticle(contpaq_art)
					self._sqllite.crear_sincronizacion("Articulo", netvy_art.ArticuloID, contpaq_art.CIDPRODUCTO, self.fecha_articulo_netvy)
					self._sqllite.crear_historico("Articulo", netvy_art.ArticuloID, contpaq_art.CIDPRODUCTO, self.fecha_articulo_netvy, 0, "C", "Se creó con éxito")
				except Exception as ex:
					self._log_error(
						f"createArticle Contpaq falló "
						f"(codigo={netvy_art.Codigo}): {ex}"
					)
					self._sqllite.crear_historico("Articulo", netvy_art.ArticuloID, 0, self.fecha_articulo_netvy, 0, "C", str(ex))

			for netvy_art in articulos_netvy.modificar:
				if netvy_art.ArticuloID is None:
					continue
				self._agregar_articulo_actualizar_contpaq_si_aplica(
					netvy_art,
					articulos_actualizar_contpaq,
					articulos_actualizar_contpaq_ids,
				)

		# 3. Crear mailings en Contpaq
		self._log_info("[Netvy -> Contpaq] Procesando mailings")
		if mailings_netvy:
			for netvy_mail in mailings_netvy.creacion:
				if netvy_mail.MailingID is None:
					continue
				if self._sqllite.existe_sincronizacion_por_netvy_id("Mailing", netvy_mail.MailingID):
					self._agregar_mailing_actualizar_contpaq_si_aplica(
						netvy_mail,
						mailings_actualizar_contpaq,
						mailings_actualizar_contpaq_ids,
					)
					continue
				try:
					contpaq_mail = ContpaqMailingAggregate(
						CCODIGOCLIENTE=netvy_mail.ReferenciaCodigo,
						CRAZONSOCIAL=netvy_mail.Nombre,
						CRFC=netvy_mail.Cif,
					)
					self._contpaq.createMailing(contpaq_mail)
					self._sqllite.crear_sincronizacion("Mailing", netvy_mail.MailingID, contpaq_mail.CIDCLIENTEPROVEEDOR, self.fecha_mailing_netvy)
					self._sqllite.crear_historico("Mailing", netvy_mail.MailingID, contpaq_mail.CIDCLIENTEPROVEEDOR, self.fecha_mailing_netvy, 0, "C", "Se creó con éxito")
				except Exception as ex:
					self._log_error(
						f"createMailing Contpaq falló "
						f"(codigo={netvy_mail.ReferenciaCodigo}): {ex}"
					)
					self._sqllite.crear_historico("Mailing", netvy_mail.MailingID, 0, self.fecha_mailing_netvy, 0, "C", str(ex))

			for netvy_mail in mailings_netvy.modificar:
				if netvy_mail.MailingID is None:
					continue
				self._agregar_mailing_actualizar_contpaq_si_aplica(
					netvy_mail,
					mailings_actualizar_contpaq,
					mailings_actualizar_contpaq_ids,
				)

		self._log_info(
			f"[Netvy -> Contpaq] Pendientes de actualización detectados: "
			f"Articulos={len(articulos_actualizar_contpaq)}, Mailings={len(mailings_actualizar_contpaq)}"
		)

		if articulos_netvy and articulos_netvy.fechaHoraHasta:
			self._pending_sync_dates[("Articulo", "Netvy", "fecha_articulo_netvy")] = articulos_netvy.fechaHoraHasta
		if mailings_netvy and mailings_netvy.fechaHoraHasta:
			self._pending_sync_dates[("Mailing", "Netvy", "fecha_mailing_netvy")] = mailings_netvy.fechaHoraHasta
		if pedidos_netvy and pedidos_netvy.fechaHoraHasta:
			self._pending_sync_dates[("PedidoVentaCabecera", "Netvy", "fecha_pedido_venta_cabecera_netvy")] = pedidos_netvy.fechaHoraHasta
		if lineas_netvy and lineas_netvy.fechaHoraHasta:
			self._pending_sync_dates[("PedidoVentaLinea", "Netvy", "fecha_pedido_venta_linea_netvy")] = lineas_netvy.fechaHoraHasta

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
					self._sqllite.crear_historico("PedidoVentaCabecera", netvy_ped.PedidoVentaCabeceraID, contpaq_ped.CIDDOCUMENTO, self.fecha_pedido_venta_cabecera_netvy, 0, "C", "Se creó con éxito")
				except Exception as ex:
					self._log_error(
						f"createSalesOrderHeader Contpaq falló "
						f"(referencia={netvy_ped.ReferenciaNuestra}): {ex}"
					)
					self._sqllite.crear_historico("PedidoVentaCabecera", netvy_ped.PedidoVentaCabeceraID, 0, self.fecha_pedido_venta_cabecera_netvy, 0, "C", str(ex))

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
					self._sqllite.crear_historico("PedidoVentaLinea", netvy_linea.PedidoVentaLineaID, contpaq_linea.CIDMOVIMIENTO, self.fecha_pedido_venta_linea_netvy, 0, "C", "Se creó con éxito")
				except Exception as ex:
					self._log_error(
						f"createSalesOrderLine Contpaq falló "
						f"(lineaID={netvy_linea.PedidoVentaLineaID}): {ex}"
					)
					self._sqllite.crear_historico("PedidoVentaLinea", netvy_linea.PedidoVentaLineaID, 0, self.fecha_pedido_venta_linea_netvy, 0, "C", str(ex))

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
		articulos_actualizar_netvy = self._articulos_actualizar_netvy
		mailings_actualizar_netvy = self._mailings_actualizar_netvy
		articulos_actualizar_netvy_ids = set()
		mailings_actualizar_netvy_ids = set()
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
					self._agregar_articulo_actualizar_netvy_si_aplica(
						contpaq_art,
						articulos_actualizar_netvy,
						articulos_actualizar_netvy_ids,
					)
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
					self._sqllite.crear_historico("Articulo", netvy_art.ArticuloID, contpaq_art.CIDPRODUCTO, self.fecha_articulo_contpaq, 1, "C", "Se creó con éxito")
				except Exception as ex:
					self._log_error(
						f"createArticle Netvy falló "
						f"(codigo={contpaq_art.CCODIGOPRODUCTO}): {ex}"
					)
					self._sqllite.crear_historico("Articulo", 0, contpaq_art.CIDPRODUCTO, self.fecha_articulo_contpaq, 1, "C", str(ex))

		# 3. Crear mailings en Netvy
		if mailings_contpaq:
			for contpaq_mail in mailings_contpaq.creacion_modificar_borrar:
				if contpaq_mail.CIDCLIENTEPROVEEDOR is None:
					continue
				if self._sqllite.existe_sincronizacion_por_contpaq_id("Mailing", contpaq_mail.CIDCLIENTEPROVEEDOR):
					self._agregar_mailing_actualizar_netvy_si_aplica(
						contpaq_mail,
						mailings_actualizar_netvy,
						mailings_actualizar_netvy_ids,
					)
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
					self._sqllite.crear_historico("Mailing", netvy_mail.MailingID, contpaq_mail.CIDCLIENTEPROVEEDOR, self.fecha_mailing_contpaq, 1, "C", "Se creó con éxito")
				except Exception as ex:
					self._log_error(
						f"createMailing Netvy falló "
						f"(codigo={contpaq_mail.CCODIGOCLIENTE}): {ex}"
					)
					self._sqllite.crear_historico("Mailing", 0, contpaq_mail.CIDCLIENTEPROVEEDOR, self.fecha_mailing_contpaq, 1, "C", str(ex))

		self._log_info(
			f"[Contpaq -> Netvy] Pendientes de actualización detectados: "
			f"Articulos={len(articulos_actualizar_netvy)}, Mailings={len(mailings_actualizar_netvy)}"
		)

		if articulos_contpaq and articulos_contpaq.fechaHoraHasta:
			self._pending_sync_dates[("Articulo", "Contpaq", "fecha_articulo_contpaq")] = articulos_contpaq.fechaHoraHasta
		if mailings_contpaq and mailings_contpaq.fechaHoraHasta:
			self._pending_sync_dates[("Mailing", "Contpaq", "fecha_mailing_contpaq")] = mailings_contpaq.fechaHoraHasta

		# 4. Lanzar sincronización de stock logístico en hilo independiente
		self._iniciar_hilo_stock_logistico()

		self._log_info("[Contpaq -> Netvy] Fin de sincronización")

	def _iniciar_hilo_stock_logistico(self):
		with self._stock_sync_lock:
			if self._stock_sync_thread and self._stock_sync_thread.is_alive():
				self._log_info("[Contpaq -> Netvy] Sincronización de stock ya está en ejecución. Se omite nuevo hilo.")
				return

			self._stock_sync_thread = threading.Thread(
				target=self._sincronizar_stock_logistico,
				name="StockSyncThread",
				daemon=True,
			)
			self._stock_sync_thread.start()
			self._log_info("[Contpaq -> Netvy] Hilo de sincronización de stock iniciado.")

	def _sincronizar_stock_logistico(self):
		self._log_info("[Contpaq -> Netvy] Inicio de sincronización de stock logístico")
		try:
			try:
				articulos_logistica = self._sqllite.getLogisticArticles()
			except Exception as ex:
				self._log_error(f"getLogisticArticles SQLite falló: {ex}")
				return

			if not articulos_logistica or not articulos_logistica.creacion_modificar_borrar:
				return

			candidatos_con_cambio = []
			for articulo_logistica in articulos_logistica.creacion_modificar_borrar:
				try:
					self._contpaq.getLogisticArticleStock(articulo_logistica)
					tiene_cambio = self._sqllite_stock.getStockChange(articulo_logistica)
					if tiene_cambio:
						candidatos_con_cambio.append(articulo_logistica)
				except Exception as ex:
					self._log_error(
						f"Sincronización de stock falló durante lectura/comparación "
						f"(NetvyArticuloID={articulo_logistica.NetvyArticuloID}, ContpaqArticuloID={articulo_logistica.ContpaqArticuloID}): {ex}"
					)

			articulos_logistica.creacion_modificar_borrar = candidatos_con_cambio

			for articulo_logistica in articulos_logistica.creacion_modificar_borrar:
				try:
					self._netvy.updateLogisticArticle(articulo_logistica)
					self._sqllite_stock.createUpdateLogisticArticle(articulo_logistica)
				except Exception as ex:
					self._log_error(
						f"updateLogisticArticle Netvy falló "
						f"(NetvyArticuloID={articulo_logistica.NetvyArticuloID}, ContpaqArticuloID={articulo_logistica.ContpaqArticuloID}): {ex}"
					)
		finally:
			self._log_info("[Contpaq -> Netvy] Fin de sincronización de stock logístico")

	def _son_equivalentes_articulos(self, contpaq_art, netvy_art):
		return (
			(contpaq_art.CCODIGOPRODUCTO or "") == (netvy_art.Codigo or "")
			and (contpaq_art.CNOMBREPRODUCTO or "") == (netvy_art.Nombre or "")
		)

	def _son_equivalentes_mailings(self, contpaq_mail, netvy_mail):
		return (
			(contpaq_mail.CCODIGOCLIENTE or "") == (netvy_mail.ReferenciaCodigo or "")
			and (contpaq_mail.CRAZONSOCIAL or "") == (netvy_mail.Nombre or "")
			and (contpaq_mail.CRFC or "") == (netvy_mail.Cif or "")
		)

	def _agregar_articulo_actualizar_netvy_si_aplica(self, contpaq_art, destino, ids_set):
		if contpaq_art.CIDPRODUCTO in ids_set:
			return

		netvy_id = self._sqllite.get_netvy_id_por_contpaq_id("Articulo", contpaq_art.CIDPRODUCTO)
		if netvy_id is None:
			return

		try:
			netvy_art = self._netvy.getArticleByID(netvy_id)
			if self._son_equivalentes_articulos(contpaq_art, netvy_art):
				return
			destino.append(
				{
					"contpaq": contpaq_art,
					"netvy_id": netvy_id,
				}
			)
			ids_set.add(contpaq_art.CIDPRODUCTO)
		except Exception as ex:
			self._log_error(
				f"Comparación para actualización de artículo (Contpaq->Netvy) falló "
				f"(ContpaqID={contpaq_art.CIDPRODUCTO}, NetvyID={netvy_id}): {ex}"
			)

	def _agregar_mailing_actualizar_netvy_si_aplica(self, contpaq_mail, destino, ids_set):
		if contpaq_mail.CIDCLIENTEPROVEEDOR in ids_set:
			return

		netvy_id = self._sqllite.get_netvy_id_por_contpaq_id("Mailing", contpaq_mail.CIDCLIENTEPROVEEDOR)
		if netvy_id is None:
			return

		try:
			netvy_mail = self._netvy.getMailingByID(netvy_id)
			if self._son_equivalentes_mailings(contpaq_mail, netvy_mail):
				return
			destino.append(
				{
					"contpaq": contpaq_mail,
					"netvy_id": netvy_id,
				}
			)
			ids_set.add(contpaq_mail.CIDCLIENTEPROVEEDOR)
		except Exception as ex:
			self._log_error(
				f"Comparación para actualización de mailing (Contpaq->Netvy) falló "
				f"(ContpaqID={contpaq_mail.CIDCLIENTEPROVEEDOR}, NetvyID={netvy_id}): {ex}"
			)

	def _agregar_articulo_actualizar_contpaq_si_aplica(self, netvy_art, destino, ids_set):
		if netvy_art.ArticuloID in ids_set:
			return

		contpaq_id = self._sqllite.get_contpaq_id_por_netvy_id("Articulo", netvy_art.ArticuloID)
		if contpaq_id is None:
			return

		try:
			contpaq_art = self._contpaq.getArticleByID(contpaq_id)
			if self._son_equivalentes_articulos(contpaq_art, netvy_art):
				return
			destino.append(
				{
					"netvy": netvy_art,
					"contpaq_id": contpaq_id,
				}
			)
			ids_set.add(netvy_art.ArticuloID)
		except Exception as ex:
			self._log_error(
				f"Comparación para actualización de artículo (Netvy->Contpaq) falló "
				f"(NetvyID={netvy_art.ArticuloID}, ContpaqID={contpaq_id}): {ex}"
			)

	def _agregar_mailing_actualizar_contpaq_si_aplica(self, netvy_mail, destino, ids_set):
		if netvy_mail.MailingID in ids_set:
			return

		contpaq_id = self._sqllite.get_contpaq_id_por_netvy_id("Mailing", netvy_mail.MailingID)
		if contpaq_id is None:
			return

		try:
			contpaq_mail = self._contpaq.getMailingByID(contpaq_id)
			if self._son_equivalentes_mailings(contpaq_mail, netvy_mail):
				return
			destino.append(
				{
					"netvy": netvy_mail,
					"contpaq_id": contpaq_id,
				}
			)
			ids_set.add(netvy_mail.MailingID)
		except Exception as ex:
			self._log_error(
				f"Comparación para actualización de mailing (Netvy->Contpaq) falló "
				f"(NetvyID={netvy_mail.MailingID}, ContpaqID={contpaq_id}): {ex}"
			)

	def _to_datetime_safe(self, fecha):
		if fecha is None:
			return datetime.min
		if isinstance(fecha, datetime):
			return fecha.replace(tzinfo=None)
		s = str(fecha).strip()
		if not s:
			return datetime.min
		try:
			dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
			return dt.replace(tzinfo=None)
		except ValueError:
			pass
		if len(s) == 17 and s.isdigit():
			try:
				dt = datetime.strptime(s[:14], "%Y%m%d%H%M%S")
				return dt.replace(microsecond=int(s[14:17]) * 1000)
			except ValueError:
				pass
		if len(s) == 14 and s.isdigit():
			try:
				return datetime.strptime(s, "%Y%m%d%H%M%S")
			except ValueError:
				pass
		if len(s) == 8 and s.isdigit():
			try:
				return datetime.strptime(s, "%Y%m%d")
			except ValueError:
				pass
		try:
			return datetime.strptime(s, "%m/%d/%Y %H:%M:%S.%f")
		except ValueError:
			return datetime.min

	def cleanUpdates(self):
		removed_articulos_netvy = 0
		removed_articulos_contpaq = 0
		removed_mailings_netvy = 0
		removed_mailings_contpaq = 0

		art_net_map = {}
		for item in self._articulos_actualizar_netvy:
			contpaq_art = item.get("contpaq")
			if not contpaq_art:
				continue
			key = (item.get("netvy_id"), contpaq_art.CIDPRODUCTO)
			art_net_map[key] = item

		art_con_map = {}
		for item in self._articulos_actualizar_contpaq:
			netvy_art = item.get("netvy")
			if not netvy_art:
				continue
			key = (netvy_art.ArticuloID, item.get("contpaq_id"))
			art_con_map[key] = item

		for key in set(art_net_map.keys()) & set(art_con_map.keys()):
			net_item = art_net_map[key]
			con_item = art_con_map[key]
			fecha_netvy = self._to_datetime_safe(
				con_item["netvy"].FechaHoraModificado or con_item["netvy"].FechaHoraUsuario
			)
			fecha_contpaq = self._to_datetime_safe(net_item["contpaq"].CTIMESTAMP)

			if fecha_netvy > fecha_contpaq:
				if net_item in self._articulos_actualizar_netvy:
					self._articulos_actualizar_netvy.remove(net_item)
					removed_articulos_netvy += 1
			elif fecha_contpaq > fecha_netvy:
				if con_item in self._articulos_actualizar_contpaq:
					self._articulos_actualizar_contpaq.remove(con_item)
					removed_articulos_contpaq += 1
			else:
				if net_item in self._articulos_actualizar_netvy:
					self._articulos_actualizar_netvy.remove(net_item)
					removed_articulos_netvy += 1
				if con_item in self._articulos_actualizar_contpaq:
					self._articulos_actualizar_contpaq.remove(con_item)
					removed_articulos_contpaq += 1

		mail_net_map = {}
		for item in self._mailings_actualizar_netvy:
			contpaq_mail = item.get("contpaq")
			if not contpaq_mail:
				continue
			key = (item.get("netvy_id"), contpaq_mail.CIDCLIENTEPROVEEDOR)
			mail_net_map[key] = item

		mail_con_map = {}
		for item in self._mailings_actualizar_contpaq:
			netvy_mail = item.get("netvy")
			if not netvy_mail:
				continue
			key = (netvy_mail.MailingID, item.get("contpaq_id"))
			mail_con_map[key] = item

		for key in set(mail_net_map.keys()) & set(mail_con_map.keys()):
			net_item = mail_net_map[key]
			con_item = mail_con_map[key]
			fecha_netvy = self._to_datetime_safe(
				con_item["netvy"].FechaHoraModificado or con_item["netvy"].FechaHoraUsuario
			)
			fecha_contpaq = self._to_datetime_safe(net_item["contpaq"].CTIMESTAMP)

			if fecha_netvy > fecha_contpaq:
				if net_item in self._mailings_actualizar_netvy:
					self._mailings_actualizar_netvy.remove(net_item)
					removed_mailings_netvy += 1
			elif fecha_contpaq > fecha_netvy:
				if con_item in self._mailings_actualizar_contpaq:
					self._mailings_actualizar_contpaq.remove(con_item)
					removed_mailings_contpaq += 1
			else:
				if net_item in self._mailings_actualizar_netvy:
					self._mailings_actualizar_netvy.remove(net_item)
					removed_mailings_netvy += 1
				if con_item in self._mailings_actualizar_contpaq:
					self._mailings_actualizar_contpaq.remove(con_item)
					removed_mailings_contpaq += 1

		self._log_info(
			f"[Sync] cleanUpdates aplicado. Eliminados => "
			f"Articulos(Netvy:{removed_articulos_netvy}, Contpaq:{removed_articulos_contpaq}) "
			f"Mailings(Netvy:{removed_mailings_netvy}, Contpaq:{removed_mailings_contpaq})"
		)

	def syncNetvyUpdates(self):
		self._log_info("[Contpaq -> Netvy] Inicio de actualización")
		fecha_base = self.fecha_articulo_contpaq
		if self._articulos_actualizar_netvy:
			for item in self._articulos_actualizar_netvy:
				contpaq_art = item.get("contpaq")
				netvy_id = item.get("netvy_id")
				if contpaq_art is None or contpaq_art.CIDPRODUCTO is None:
					continue

				if netvy_id is None:
					netvy_id = self._sqllite.get_netvy_id_por_contpaq_id("Articulo", contpaq_art.CIDPRODUCTO)
				if netvy_id is None:
					continue

				fecha_historico = self._normalizar_fecha(fecha_base or datetime.now())
				try:
					netvy_art = NetvyArticuloAggregate(
						ArticuloID=netvy_id,
						Codigo=contpaq_art.CCODIGOPRODUCTO,
						Nombre=contpaq_art.CNOMBREPRODUCTO,
					)
					self._netvy.updateArticle(netvy_art)
					fecha_sync = fecha_historico
					self._sqllite.actualizar_fecha_ultima_sincronizacion(
						"Articulo",
						netvy_id,
						contpaq_art.CIDPRODUCTO,
						fecha_sync,
					)
					self._sqllite.crear_historico(
						"Articulo",
						netvy_id,
						contpaq_art.CIDPRODUCTO,
						fecha_sync,
						1,
						"A",
						"Actualizado con exito",
					)
				except Exception as ex:
					self._log_error(
						f"updateArticle Netvy falló "
						f"(NetvyID={netvy_id}, ContpaqID={contpaq_art.CIDPRODUCTO}): {ex}"
					)
					self._sqllite.crear_historico(
						"Articulo",
						netvy_id or 0,
						contpaq_art.CIDPRODUCTO or 0,
						fecha_historico,
						1,
						"A",
						str(ex),
					)

		fecha_base_mail = self.fecha_mailing_contpaq
		if self._mailings_actualizar_netvy:
			for item in self._mailings_actualizar_netvy:
				contpaq_mail = item.get("contpaq")
				netvy_id = item.get("netvy_id")
				if contpaq_mail is None or contpaq_mail.CIDCLIENTEPROVEEDOR is None:
					continue

				if netvy_id is None:
					netvy_id = self._sqllite.get_netvy_id_por_contpaq_id("Mailing", contpaq_mail.CIDCLIENTEPROVEEDOR)
				if netvy_id is None:
					continue

				fecha_historico = self._normalizar_fecha(fecha_base_mail or datetime.now())
				try:
					netvy_mail = NetvyMailingAggregate(
						MailingID=netvy_id,
						ReferenciaCodigo=contpaq_mail.CCODIGOCLIENTE,
						Nombre=contpaq_mail.CRAZONSOCIAL,
						Cif=contpaq_mail.CRFC,
					)
					self._netvy.updateMailing(netvy_mail)
					fecha_sync = fecha_historico
					self._sqllite.actualizar_fecha_ultima_sincronizacion(
						"Mailing",
						netvy_id,
						contpaq_mail.CIDCLIENTEPROVEEDOR,
						fecha_sync,
					)
					self._sqllite.crear_historico(
						"Mailing",
						netvy_id,
						contpaq_mail.CIDCLIENTEPROVEEDOR,
						fecha_sync,
						1,
						"A",
						"Actualizado con exito",
					)
				except Exception as ex:
					self._log_error(
						f"updateMailing Netvy falló "
						f"(NetvyID={netvy_id}, ContpaqID={contpaq_mail.CIDCLIENTEPROVEEDOR}): {ex}"
					)
					self._sqllite.crear_historico(
						"Mailing",
						netvy_id or 0,
						contpaq_mail.CIDCLIENTEPROVEEDOR or 0,
						fecha_historico,
						1,
						"A",
						str(ex),
					)

		self._log_info("[Contpaq -> Netvy] Fin de actualización")

	def syncContpaqUpdates(self):
		self._log_info("[Netvy -> Contpaq] Inicio de actualización")
		fecha_base = self.fecha_articulo_netvy
		if self._articulos_actualizar_contpaq:
			for item in self._articulos_actualizar_contpaq:
				netvy_art = item.get("netvy")
				contpaq_id = item.get("contpaq_id")
				if netvy_art is None or netvy_art.ArticuloID is None:
					continue

				if contpaq_id is None:
					contpaq_id = self._sqllite.get_contpaq_id_por_netvy_id("Articulo", netvy_art.ArticuloID)
				if contpaq_id is None:
					continue

				fecha_historico = self._normalizar_fecha(fecha_base or datetime.now())
				try:
					contpaq_art = ContpaqArticuloAggregate(
						CIDPRODUCTO=contpaq_id,
						CCODIGOPRODUCTO=netvy_art.Codigo,
						CNOMBREPRODUCTO=netvy_art.Nombre,
					)
					self._contpaq.updateArticle(contpaq_art)
					fecha_sync = fecha_historico
					self._sqllite.actualizar_fecha_ultima_sincronizacion(
						"Articulo",
						netvy_art.ArticuloID,
						contpaq_id,
						fecha_sync,
					)
					self._sqllite.crear_historico(
						"Articulo",
						netvy_art.ArticuloID,
						contpaq_id,
						fecha_sync,
						0,
						"A",
						"Actualizado con exito",
					)
				except Exception as ex:
					self._log_error(
						f"updateArticle Contpaq falló "
						f"(NetvyID={netvy_art.ArticuloID}, ContpaqID={contpaq_id}): {ex}"
					)
					self._sqllite.crear_historico(
						"Articulo",
						netvy_art.ArticuloID or 0,
						contpaq_id or 0,
						fecha_historico,
						0,
						"A",
						str(ex),
					)

		fecha_base_mail = self.fecha_mailing_netvy
		if self._mailings_actualizar_contpaq:
			for item in self._mailings_actualizar_contpaq:
				netvy_mail = item.get("netvy")
				contpaq_id = item.get("contpaq_id")
				if netvy_mail is None or netvy_mail.MailingID is None:
					continue

				if contpaq_id is None:
					contpaq_id = self._sqllite.get_contpaq_id_por_netvy_id("Mailing", netvy_mail.MailingID)
				if contpaq_id is None:
					continue

				fecha_historico = self._normalizar_fecha(fecha_base_mail or datetime.now())
				try:
					contpaq_mail = ContpaqMailingAggregate(
						CIDCLIENTEPROVEEDOR=contpaq_id,
						CCODIGOCLIENTE=netvy_mail.ReferenciaCodigo,
						CRAZONSOCIAL=netvy_mail.Nombre,
						CRFC=netvy_mail.Cif,
					)
					self._contpaq.updateMailing(contpaq_mail)
					fecha_sync = fecha_historico
					self._sqllite.actualizar_fecha_ultima_sincronizacion(
						"Mailing",
						netvy_mail.MailingID,
						contpaq_id,
						fecha_sync,
					)
					self._sqllite.crear_historico(
						"Mailing",
						netvy_mail.MailingID,
						contpaq_id,
						fecha_sync,
						0,
						"A",
						"Actualizado con exito",
					)
				except Exception as ex:
					self._log_error(
						f"updateMailing Contpaq falló "
						f"(NetvyID={netvy_mail.MailingID}, ContpaqID={contpaq_id}): {ex}"
					)
					self._sqllite.crear_historico(
						"Mailing",
						netvy_mail.MailingID or 0,
						contpaq_id or 0,
						fecha_historico,
						0,
						"A",
						str(ex),
					)

		self._log_info("[Netvy -> Contpaq] Fin de actualización")

	def updateSyncDates(self):
		self._log_info("[Sync] Inicio de actualización de fechas de sincronización")

		for (tabla, programa, fecha_attr), fecha in self._pending_sync_dates.items():
			if not fecha:
				continue
			try:
				fecha_normalizada = self._normalizar_fecha(fecha)
				self._sqllite.actualizar_fecha_sincronizacion(tabla, programa, fecha_normalizada)
				setattr(self, fecha_attr, fecha_normalizada)
			except Exception as ex:
				self._log_error(
					f"actualizar_fecha_sincronizacion {tabla}/{programa} falló: {ex}"
				)

		self._log_info("[Sync] Fin de actualización de fechas de sincronización")

