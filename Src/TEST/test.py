import json
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1]

if str(SRC_PATH) not in sys.path:
	sys.path.insert(0, str(SRC_PATH))

from APP import init
from INF.SQLLiteRepository import SQLLiteRepository
from INF.ApiNetvyRepository import ApiNetvyRepository
from INF.SDKContpaqRepository import SDKContpaqRepository
from DOM.NetvyMailingAggregate import NetvyMailingAggregate
from DOM.NetvyArticuloAggregate import NetvyArticuloAggregate
from DOM.ContpaqArticuloAggregate import ContpaqArticuloAggregate
from DOM.ContpaqMailingAggregate import ContpaqMailingAggregate
from DOM.ContpaqPedidoVentaCabeceraAggregate import ContpaqPedidoVentaCabeceraAggregate
from DOM.ContpaqPedidoVentaLineaAggregate import ContpaqPedidoVentaLineaAggregate
from APP.SyncContpaqController import SyncContpaqController


class test(unittest.TestCase):
	def testSQLLiteINIT(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		sql_lite_config = config["SQLLITE"]
		db_absolute_path = (SRC_PATH / sql_lite_config["DBPATH"]).resolve()

		repository = SQLLiteRepository(sql_lite_config)
		repository.init()

		self.assertTrue(db_absolute_path.exists())

	def testLogin(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		result = repository.login()

		self.assertIsNotNone(result.token)
		self.assertIsNotNone(result.refreshToken)

	def testRefreshToken(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		token = repository.login()
		repository.refresh_token(token)

		self.assertIsNotNone(token.token)
		self.assertIsNotNone(token.refreshToken)

	def testGetArticles(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		result = repository.getArticles("19990101000000")

		self.assertIsNotNone(result)

	def testGetMailings(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		result = repository.getMailings("19990101000000")

		self.assertIsNotNone(result)

	def testGetPedidoVentaCabecera(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		result = repository.getPedidoVentaCabecera("19990101000000")

		self.assertIsNotNone(result)

	def testGetPedidoVentaLinea(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		result = repository.getSalesOrderLine("19990101000000")

		self.assertIsNotNone(result)

	def testSDKContpaqRepositoryInit(self):
		"""Test de inicialización de SDKContpaqRepository con configuración de SQL Server"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])
		self.assertIsNotNone(repository)
		self.assertIsNotNone(repository.server)
		self.assertIsNotNone(repository.database)

	def testSDKContpaqGetArticles(self):
		"""Test getArticles trae información de productos desde una fecha"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])
		result = repository.getArticles("19990101000000")

		self.assertIsNotNone(result)
		self.assertEqual(result.tabla, "dbo.admProductos")
		self.assertIsNotNone(result.fechaHoraDesde)
		self.assertIsNotNone(result.fechaHoraHasta)
		self.assertIsInstance(result.creacion_modificar_borrar, list)

	def testSDKContpaqGetMailings(self):
		"""Test getMailings trae información de clientes desde una fecha"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])
		result = repository.getMailings("19990101000000")

		self.assertIsNotNone(result)
		self.assertEqual(result.tabla, "dbo.admClientes")
		self.assertIsNotNone(result.fechaHoraDesde)
		self.assertIsNotNone(result.fechaHoraHasta)
		self.assertIsInstance(result.creacion_modificar_borrar, list)

	def testGetFamilyConfig(self):
		"""Test getFamilyConfig obtiene la configuración de familia y la guarda en variable global"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		familia_id = repository.getFamilyConfig()

		self.assertIsNotNone(familia_id)
		self.assertEqual(init.NetvyFamiliaID, familia_id)
		self.assertIsInstance(familia_id, int)

	def testGetCurrencieConfig(self):
		"""Test getCurrencieConfig obtiene la configuración de moneda y la guarda en variable global"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		moneda_id = repository.getCurrencieConfig()

		self.assertIsNotNone(moneda_id)
		self.assertEqual(init.NetvyMonedaID, moneda_id)
		self.assertIsInstance(moneda_id, int)

	def testCreateMailing(self):
		"""Test createMailing crea un nuevo mailing en la API"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		repository.getCurrencieConfig()

		# Crear un nuevo mailing de prueba
		mailing = NetvyMailingAggregate(
			ReferenciaCodigo="TEST_MAILING_002",
			Cif="TEST_CIF_002",
			Nombre="Cliente de Prueba",
			NombreComercial="Cliente Prueba SA",
			Email="test@example.com",
			Web="http://example.com",
			Fax="1234567890",
			Telefono="9876543210"
		)

		mailing_id = repository.createMailing(mailing)

		self.assertIsNotNone(mailing_id)
		self.assertEqual(mailing.MailingID, mailing_id)
		self.assertIsInstance(mailing_id, int)

	def testCreateArticle(self):
		"""Test createArticle crea un nuevo artículo en la API"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		repository.getFamilyConfig()

		# Crear un nuevo artículo de prueba
		articulo = NetvyArticuloAggregate(
			Codigo="ARTICULO_TEST_002",
			Nombre="Artículo de Prueba",
			Descripcion="Descripción del artículo de prueba",
			Activo=True
		)

		articulo_id = repository.createArticle(articulo)

		self.assertIsNotNone(articulo_id)
		self.assertEqual(articulo.ArticuloID, articulo_id)
		self.assertIsInstance(articulo_id, int)

	def testSDKContpaqCreateArticle(self):
		"""Test createArticle crea un artículo en Contpaqi usando el SDK nativo"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])

		codigo = f"TST_A_{datetime.now().strftime('%H%M%S')}"
		articulo = ContpaqArticuloAggregate(
			CIDPRODUCTO=None,
			CCODIGOPRODUCTO=codigo,
			CNOMBREPRODUCTO="Artículo SDK Prueba",
			CTIPOPRODUCTO=1,
			CFECHAALTAPRODUCTO=None,
			CFECHABAJA=None,
			CTIMESTAMP=None
		)

		nuevo_id = repository.createArticle(articulo)

		self.assertIsNotNone(nuevo_id)
		self.assertIsInstance(nuevo_id, int)
		self.assertGreater(nuevo_id, 0)
		self.assertEqual(articulo.CIDPRODUCTO, nuevo_id)

	def testSDKContpaqCreateMailing(self):
		"""Test createMailing crea un cliente en Contpaqi usando el SDK nativo"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])

		codigo = f"TST_C_{datetime.now().strftime('%H%M%S')}"
		mailing = ContpaqMailingAggregate(
			CIDCLIENTEPROVEEDOR=None,
			CCODIGOCLIENTE=codigo,
			CRAZONSOCIAL="Cliente SDK Prueba SA",
			CFECHAALTA=None,
			CRFC="TSC010101AAA",
			CTIMESTAMP=None
		)

		nuevo_id = repository.createMailing(mailing)

		self.assertIsNotNone(nuevo_id)
		self.assertIsInstance(nuevo_id, int)
		self.assertGreater(nuevo_id, 0)
		self.assertEqual(mailing.CIDCLIENTEPROVEEDOR, nuevo_id)


	def testSDKContpaqCreateSalesOrderHeader(self):
		"""Test createSalesOrderHeader crea un pedido de venta en Contpaqi usando el SDK nativo"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])

		pedido = ContpaqPedidoVentaCabeceraAggregate(
			CIDDOCUMENTO=None,
			CIDDOCUMENTODE=None,
			CCODIGOCONCEPTO="2",
			CCODIGOCTEPROV="12345",
			CREFERENCIA="TEST-SDK-PEDIDO",
		)

		doc_id = repository.createSalesOrderHeader(pedido)

		self.assertIsNotNone(doc_id)
		self.assertIsInstance(doc_id, int)
		self.assertGreater(doc_id, 0)
		self.assertEqual(pedido.CIDDOCUMENTO, doc_id)

	def testSDKContpaqCreateSalesOrderLine(self):
		"""Test createSalesOrderLine crea un movimiento en un pedido de venta existente"""
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = SDKContpaqRepository(config["CONTPAQ"])

		pedido = ContpaqPedidoVentaCabeceraAggregate(
			CIDDOCUMENTO=None,
			CIDDOCUMENTODE=None,
			CCODIGOCONCEPTO="2",
			CCODIGOCTEPROV="12345",
			CREFERENCIA="TEST-SDK-PEDIDO-LINEA",
		)

		doc_id = repository.createSalesOrderHeader(pedido)

		linea = ContpaqPedidoVentaLineaAggregate(
			CIDMOVIMIENTO=None,
			CNUMEROMOVIMIENTO=None,
			CIDDOCUMENTO=doc_id,
			CIDPRODUCTO=None,
			CCODIGOPRODUCTO="12345P",
			CUNIDADES=1.0,
			CPRECIO=100.0,
			CREFERENCIA="TEST-SDK-PEDIDO-LINEA",
		)

		mov_id = repository.createSalesOrderLine(linea)

		self.assertIsNotNone(mov_id)
		self.assertIsInstance(mov_id, int)
		self.assertGreater(mov_id, 0)
		self.assertEqual(linea.CIDMOVIMIENTO, mov_id)

	def testRun(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		controller = SyncContpaqController(config)
		controller.init()
		while True:
			controller._sincronizar()
			time.sleep(controller._interval)


if __name__ == "__main__":
	tester = test()
	tester.testRun()
