import requests

from APP import init
from DOM.LoginToken import LoginToken
from DOM.NetvyArticuloAggregate import NetvyArticuloAggregate
from DOM.NetvyArticuloCollection import NetvyArticuloCollection
from DOM.NetvyMailingAggregate import NetvyMailingAggregate
from DOM.NetvyMailingCollection import NetvyMailingCollection
from DOM.NetvyPedidoVentaCabeceraAggregate import NetvyPedidoVentaCabeceraAggregate
from DOM.NetvyPedidoVentaCabeceraCollection import NetvyPedidoVentaCabeceraCollection


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
		self.codigo_familia = config.get("CODIGOFAMILIA")
		self.codigo_moneda = config.get("CODIGOMONEDA")

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

	def getPedidoVentaCabecera(self, fecha):
		url = f"{self.url_base}/changeRegister/PedidoVentaCabecera/{fecha}"
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
			raise Exception(error_data.get("error", f"Error al obtener pedidos de venta: {response.status_code}"))

		data = response.json()
		creacion = [self._map_pedido_venta_cabecera(item) for item in data.get("creacion", [])]
		modificar = [self._map_pedido_venta_cabecera(item) for item in data.get("modificar", [])]
		borrar = [self._map_pedido_venta_cabecera(item) for item in data.get("borrar", [])]

		return NetvyPedidoVentaCabeceraCollection(
			tabla=data.get("tabla"),
			fechaHoraDesde=data.get("fechaHoraDesde"),
			fechaHoraHasta=data.get("fechaHoraHasta"),
			creacion=creacion,
			modificar=modificar,
			borrar=borrar,
		)

	def _map_pedido_venta_cabecera(self, data):
		return NetvyPedidoVentaCabeceraAggregate(
			PedidoVentaCabeceraID=data.get("PedidoVentaCabeceraID"),
			CustomerID=data.get("CustomerID"),
			EmpresaID=data.get("EmpresaID"),
			FechaHoraUsuario=data.get("FechaHoraUsuario"),
			SeriePedidoID=data.get("SeriePedidoID"),
			Numero=data.get("Numero"),
			Fecha=data.get("Fecha"),
			ReferenciaCliente=data.get("ReferenciaCliente"),
			ClienteID=data.get("ClienteID"),
			NotaGeneral=data.get("NotaGeneral"),
			NotaCliente=data.get("NotaCliente"),
			PedidoPor=data.get("PedidoPor"),
			FechaEntregaPrevistaInterna=data.get("FechaEntregaPrevistaInterna"),
			FechaEntregaPrevistaCliente=data.get("FechaEntregaPrevistaCliente"),
			ContactoID=data.get("ContactoID"),
			MonedaID=data.get("MonedaID"),
			Entregado=data.get("Entregado"),
			Descripcion=data.get("Descripcion"),
			ReferenciaNuestra=data.get("ReferenciaNuestra"),
			PesoNeto=data.get("PesoNeto"),
			PesoBruto=data.get("PesoBruto"),
			Cajas=data.get("Cajas"),
			Palets=data.get("Palets"),
		)

	def getFamilyConfig(self):
		"""
		Obtiene la configuración de familia desde la API de Netvy.
		Primero intenta buscar por CODIGOFAMILIA, si no encuentra, busca sin filtro.
		Si encuentra, guarda el FamiliaID en la variable global init.NetvyFamiliaID
		"""
		if not self.codigo_familia:
			raise ValueError("CODIGOFAMILIA no está configurado en el archivo de configuración")

		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		# Primer intento: con match de CODIGOFAMILIA
		url = f"{self.url_base}/families?limit=1&orderby=FechaHoraUsuario&orientation=asc&match={self.codigo_familia}"
		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			raise Exception(f"Error al obtener configuración de familia (primer intento): {response.status_code}")

		data = response.json()

		# Si la respuesta es un array vacío, reintentar sin el match
		if isinstance(data, list) and len(data) == 0:
			url = f"{self.url_base}/families?limit=1&orderby=FechaHoraUsuario&orientation=asc"
			response = requests.get(url, headers=headers)

			if response.status_code == 401:
				self.refresh_token(init.token)
				headers["Authorization"] = f"Bearer {init.token.token}"
				response = requests.get(url, headers=headers)

			if response.status_code != 200:
				raise Exception(f"Error al obtener configuración de familia (segundo intento): {response.status_code}")

			data = response.json()

		# Si sigue siendo un array vacío, lanzar excepción
		if isinstance(data, list) and len(data) == 0:
			raise Exception("No se encontró configuración de familia en la API de Netvy")

		# Extraer el primer elemento del array y obtener FamiliaID
		if isinstance(data, list):
			familia = data[0]
		else:
			familia = data

		familia_id = familia.get("FamiliaID")
		if familia_id is None:
			raise Exception("FamiliaID no encontrado en la respuesta de la API")

		init.NetvyFamiliaID = familia_id
		return familia_id

	def getCurrencieConfig(self):
		"""
		Obtiene la configuración de moneda desde la API de Netvy.
		Primero intenta buscar por CODIGOMONEDA, si no encuentra, busca sin filtro.
		Si encuentra, guarda el MonedaID en la variable global init.NetvyMonedaID
		"""
		if not self.codigo_moneda:
			raise ValueError("CODIGOMONEDA no está configurado en el archivo de configuración")

		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		# Primer intento: con codigoISO de CODIGOMONEDA
		url = f"{self.url_base}/currencies?limit=1&orderby=FechaHoraUsuario&orientation=asc&codigoISO={self.codigo_moneda}"
		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			raise Exception(f"Error al obtener configuración de moneda (primer intento): {response.status_code}")

		data = response.json()

		# Si la respuesta es un array vacío, reintentar sin el codigoISO
		if isinstance(data, list) and len(data) == 0:
			url = f"{self.url_base}/currencies?limit=1&orderby=FechaHoraUsuario&orientation=asc"
			response = requests.get(url, headers=headers)

			if response.status_code == 401:
				self.refresh_token(init.token)
				headers["Authorization"] = f"Bearer {init.token.token}"
				response = requests.get(url, headers=headers)

			if response.status_code != 200:
				raise Exception(f"Error al obtener configuración de moneda (segundo intento): {response.status_code}")

			data = response.json()

		# Si sigue siendo un array vacío, lanzar excepción
		if isinstance(data, list) and len(data) == 0:
			raise Exception("No se encontró configuración de moneda en la API de Netvy")

		# Extraer el primer elemento del array y obtener MonedaID
		if isinstance(data, list):
			moneda = data[0]
		else:
			moneda = data

		moneda_id = moneda.get("MonedaID")
		if moneda_id is None:
			raise Exception("MonedaID no encontrado en la respuesta de la API")

		init.NetvyMonedaID = moneda_id
		return moneda_id

	def createMailing(self, mailing):
		"""
		Crea un nuevo mailing (cliente/proveedor) en la API de Netvy.
		
		Args:
			mailing (NetvyMailingAggregate): Aggregate del mailing a crear
			
		Returns:
			int: MailingID del mailing creado
		"""
		if init.NetvyMonedaID is None:
			raise ValueError("NetvyMonedaID no está configurado. Ejecute getCurrencieConfig() primero")

		url = f"{self.url_base}/thirdparty"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		body = {
			"ReferenciaCodigo": mailing.ReferenciaCodigo or "",
			"Cif": mailing.Cif or "",
			"Nombre": mailing.Nombre or "",
			"NombreComercial": mailing.NombreComercial or "",
			"Email": mailing.Email or "",
			"Web": mailing.Web or "",
			"Fax": mailing.Fax or "",
			"Telefono": mailing.Telefono or "",
			"MonedaID": init.NetvyMonedaID,
			"NombrePersona": mailing.Nombre or "",
			"esCliente": False,
			"Activo": 1
		}

		response = requests.post(url, json=body, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.post(url, json=body, headers=headers)

		if response.status_code != 201:
			raise Exception(f"Error al crear mailing en la API: {response.status_code} - {response.text}")

		data = response.json()
		mailing_id = data.get("MailingID")

		if mailing_id is None:
			raise Exception("MailingID no encontrado en la respuesta de la API")

		mailing.MailingID = mailing_id
		return mailing_id

	def createArticle(self, articulo):
		"""
		Crea un nuevo artículo en la API de Netvy.
		
		Args:
			articulo (NetvyArticuloAggregate): Aggregate del artículo a crear
			
		Returns:
			int: ArticuloID del artículo creado
		"""
		if init.NetvyFamiliaID is None:
			raise ValueError("NetvyFamiliaID no está configurado. Ejecute getFamilyConfig() primero")

		url = f"{self.url_base}/tables/articles"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		body = {
			"Activo": True,
			"Codigo": articulo.Codigo or "",
			"Nombre": articulo.Nombre or "",
			"FamiliaID": init.NetvyFamiliaID,
			"Descripcion": articulo.Descripcion or ""
		}

		response = requests.post(url, json=body, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.post(url, json=body, headers=headers)

		if response.status_code != 201:
			raise Exception(f"Error al crear artículo en la API: {response.status_code} - {response.text}")

		data = response.json()
		articulo_data = data.get("articulo")

		if articulo_data is None:
			raise Exception("Respuesta de artículo no encontrada en la API")

		articulo_id = articulo_data.get("ArticuloID")

		if articulo_id is None:
			raise Exception("ArticuloID no encontrado en la respuesta de la API")

		articulo.ArticuloID = articulo_id
		return articulo_id
