import requests

from APP import init
from DOM.LoginToken import LoginToken
from DOM.NetvyArticuloAggregate import NetvyArticuloAggregate
from DOM.NetvyArticuloCollection import NetvyArticuloCollection
from DOM.NetvyMailingAggregate import NetvyMailingAggregate
from DOM.NetvyMailingCollection import NetvyMailingCollection


class ApiNetvyRepository:

	def __init__(self, config):
		if not isinstance(config, dict):
			raise ValueError("config debe ser un diccionario con las llaves URLBASE, USER, PASSWORD, LICENSE")

		self.url_base = config.get("URLBASE")
		if self.url_base and not self.url_base.startswith("http://") and not self.url_base.startswith("https://"):
			self.url_base = f"http://{self.url_base}"
		self.user = config.get("USER")
		self.password = config.get("PASSWORD")
		self.license = config.get("LICENSE")

		if not all([self.url_base, self.user, self.password, self.license]):
			raise ValueError("config debe incluir las llaves URLBASE, USER, PASSWORD, LICENSE")

	def login(self):
		url = f"{self.url_base}/login"
		body = {
			"user": self.user,
			"pass": self.password,
		}
		headers = {
			"license": self.license,
		}

		response = requests.post(url, json=body, headers=headers)

		if response.status_code != 200:
			error_data = response.json()
			raise Exception(error_data.get("error", f"Error de login: {response.status_code}"))

		data = response.json()
		login_token = LoginToken(
			usuarioID=data.get("usuarioID"),
			empresaID=data.get("empresaID"),
			isAdmin=data.get("isAdmin"),
			idiomaID=data.get("idiomaID"),
			customerID=data.get("customerID"),
			sessionID=data.get("sessionID"),
			refreshToken=data.get("refreshToken"),
			token=data.get("token"),
		)
		init.token = login_token
		return login_token

	def refresh_token(self, token):
		url = f"{self.url_base}/refresh"
		headers = {
			"Authorization": f"Bearer {token.token}",
		}

		response = requests.post(url, headers=headers)

		if response.status_code != 200:
			error_data = response.json()
			raise Exception(error_data.get("message", f"Error al refrescar token: {response.status_code}"))

		data = response.json()
		token.token = data.get("token")
		token.refreshToken = data.get("refreshToken")
		init.token = token

	def getArticles(self, fecha):
		url = f"{self.url_base}/changeRegister/articulo/{fecha}"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			error_data = response.json()
			raise Exception(error_data.get("error", f"Error al obtener artículos: {response.status_code}"))

		data = response.json()
		creacion = [self._map_articulo(item) for item in data.get("creacion", [])]
		modificar = [self._map_articulo(item) for item in data.get("modificar", [])]
		borrar = [self._map_articulo(item) for item in data.get("borrar", [])]

		return NetvyArticuloCollection(
			tabla=data.get("tabla"),
			fechaHoraDesde=data.get("fechaHoraDesde"),
			fechaHoraHasta=data.get("fechaHoraHasta"),
			creacion=creacion,
			modificar=modificar,
			borrar=borrar,
		)

	def _map_articulo(self, data):
		return NetvyArticuloAggregate(
			ArticuloID=data.get("ArticuloID"),
			FamiliaID=data.get("FamiliaID"),
			SubFamiliaID=data.get("SubFamiliaID"),
			CustomerID=data.get("CustomerID"),
			EmpresaID=data.get("EmpresaID"),
			UsuarioID=data.get("UsuarioID"),
			FechaHoraUsuario=data.get("FechaHoraUsuario"),
			Nombre=data.get("Nombre"),
			Activo=data.get("Activo"),
			TipoArticuloID=data.get("TipoArticuloID"),
			Codigo=data.get("Codigo"),
			Observacion=data.get("Observacion"),
			Descripcion=data.get("Descripcion"),
			CodigoAlternativo=data.get("CodigoAlternativo"),
		)

	def getMailings(self, fecha):
		url = f"{self.url_base}/changeRegister/mailing/{fecha}"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			error_data = response.json()
			raise Exception(error_data.get("error", f"Error al obtener mailings: {response.status_code}"))

		data = response.json()
		creacion = [self._map_mailing(item) for item in data.get("creacion", [])]
		modificar = [self._map_mailing(item) for item in data.get("modificar", [])]
		borrar = [self._map_mailing(item) for item in data.get("borrar", [])]

		return NetvyMailingCollection(
			tabla=data.get("tabla"),
			fechaHoraDesde=data.get("fechaHoraDesde"),
			fechaHoraHasta=data.get("fechaHoraHasta"),
			creacion=creacion,
			modificar=modificar,
			borrar=borrar,
		)

	def _map_mailing(self, data):
		return NetvyMailingAggregate(
			MailingID=data.get("MailingID"),
			EmpresaID=data.get("EmpresaID"),
			Nombre=data.get("Nombre"),
			Direccion=data.get("Direccion"),
			Telefono=data.get("Telefono"),
			Fax=data.get("Fax"),
			Email=data.get("Email"),
			Web=data.get("Web"),
			Cif=data.get("Cif"),
			Directorio=data.get("Directorio"),
			CustomerID=data.get("CustomerID"),
			FechaHoraAlta=data.get("FechaHoraAlta"),
			FechaBaja=data.get("FechaBaja"),
			Observacion=data.get("Observacion"),
			TipoMailID=data.get("TipoMailID"),
			FechaHoraUsuario=data.get("FechaHoraUsuario"),
			ReferenciaCodigo=data.get("ReferenciaCodigo"),
			Activo=data.get("Activo"),
			Latitud=data.get("Latitud"),
			Longitud=data.get("Longitud"),
			NombreComercial=data.get("NombreComercial"),
			Notas=data.get("Notas"),
		)
