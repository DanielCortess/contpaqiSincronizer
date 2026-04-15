import json
import sys
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parents[1]

if str(SRC_PATH) not in sys.path:
	sys.path.insert(0, str(SRC_PATH))

from APP import init
from INF.SQLLiteRepository import SQLLiteRepository
from INF.ApiNetvyRepository import ApiNetvyRepository
from INF.SDKContpaqRepository import SDKContpaqRepository


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
		result = repository.getArticles("19990101")

		self.assertIsNotNone(result)

	def testGetMailings(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		result = repository.getMailings("19990101")

		self.assertIsNotNone(result)

	def testGetPedidoVentaCabecera(self):
		config_path = SRC_PATH / "conf.json"

		with config_path.open("r", encoding="utf-8") as config_file:
			config = json.load(config_file)

		repository = ApiNetvyRepository(config["NETVY"])
		repository.login()
		result = repository.getPedidoVentaCabecera("19990101")

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
		result = repository.getArticles("19990101")

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
		result = repository.getMailings("19990101")

		self.assertIsNotNone(result)
		self.assertEqual(result.tabla, "dbo.admClientes")
		self.assertIsNotNone(result.fechaHoraDesde)
		self.assertIsNotNone(result.fechaHoraHasta)
		self.assertIsInstance(result.creacion_modificar_borrar, list)


if __name__ == "__main__":
	unittest.main()
