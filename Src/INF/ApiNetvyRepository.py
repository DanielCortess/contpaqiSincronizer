import requests

from APP import init
from DOM.LoginToken import LoginToken
from DOM.NetvyArticuloAggregate import NetvyArticuloAggregate
from DOM.NetvyArticuloCollection import NetvyArticuloCollection
from DOM.NetvyMailingAggregate import NetvyMailingAggregate
from DOM.NetvyMailingCollection import NetvyMailingCollection
from DOM.NetvyPedidoVentaCabeceraAggregate import NetvyPedidoVentaCabeceraAggregate
from DOM.NetvyPedidoVentaCabeceraCollection import NetvyPedidoVentaCabeceraCollection
from DOM.NetvyPedidoVentaLineaAggregate import NetvyPedidoVentaLineaAggregate
from DOM.NetvyPedidoVentaLineaCollection import NetvyPedidoVentaLineaCollection


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
		# self.tipo_documento = config.get("TIPODOCUMENTO")
		# self.tipo_persona_mex = config.get("TIPOPERSONAMEX")

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
			FechaHoraModificado=data.get("FechaHoraModificado"),
			Nombre=data.get("Nombre"),
			Activo=data.get("Activo"),
			TipoArticuloID=data.get("TipoArticuloID"),
			Codigo=data.get("Codigo"),
			Observacion=data.get("Observacion"),
			Descripcion=data.get("Descripcion"),
			CodigoAlternativo=data.get("CodigoAlternativo"),
		)

	def getArticleByID(self, articulo_id):
		url = f"{self.url_base}/article?articuloid={articulo_id}"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			try:
				error_data = response.json()
				error_msg = error_data.get("error", error_data.get("message", response.text))
			except Exception:
				error_msg = response.text
			raise Exception(f"Error al obtener artículo por ID: {response.status_code} - {error_msg}")

		data = response.json()
		if isinstance(data, list) and len(data) > 0:
			return self._map_articulo(data[0])

		return NetvyArticuloAggregate()

	def _normalize_mailing_item(self, item):
		return {
			"MailingID": item.get("MailingID", item.get("mailingID")),
			"EmpresaID": item.get("EmpresaID", item.get("empresaID")),
			"Nombre": item.get("Nombre", item.get("nombre")),
			"Direccion": item.get("Direccion", item.get("direccion")),
			"Telefono": item.get("Telefono", item.get("telefono")),
			"Fax": item.get("Fax", item.get("fax")),
			"Email": item.get("Email", item.get("email")),
			"Web": item.get("Web", item.get("web")),
			"Cif": item.get("Cif", item.get("cif")),
			"Directorio": item.get("Directorio", item.get("directorio")),
			"CustomerID": item.get("CustomerID", item.get("customerID")),
			"FechaHoraAlta": item.get("FechaHoraAlta", item.get("fechaHoraAlta")),
			"FechaBaja": item.get("FechaBaja", item.get("fechaBaja")),
			"Observacion": item.get("Observacion", item.get("observacion")),
			"TipoMailID": item.get("TipoMailID", item.get("tipoMailID")),
			"FechaHoraUsuario": item.get("FechaHoraUsuario", item.get("fechaHoraUsuario")),
			"FechaHoraModificado": item.get("FechaHoraModificado", item.get("fechaHoraModificado")),
			"ReferenciaCodigo": item.get("ReferenciaCodigo", item.get("referenciaCodigo")),
			"Activo": item.get("Activo", item.get("activo")),
			"Latitud": item.get("Latitud", item.get("latitud")),
			"Longitud": item.get("Longitud", item.get("longitud")),
			"NombreComercial": item.get("NombreComercial", item.get("nombreComercial")),
			"Notas": item.get("Notas", item.get("notas")),
		}

	def getMailingByID(self, mailing_id):
		url = f"{self.url_base}/thirdparty?MailingID={mailing_id}"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			try:
				error_data = response.json()
				error_msg = error_data.get("error", error_data.get("message", response.text))
			except Exception:
				error_msg = response.text
			raise Exception(f"Error al obtener mailing por ID: {response.status_code} - {error_msg}")

		data = response.json()
		if isinstance(data, list) and len(data) > 0:
			normalized = self._normalize_mailing_item(data[0])
			return self._map_mailing(normalized)

		return NetvyMailingAggregate()

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
			FechaHoraModificado=data.get("FechaHoraModificado"),
			ReferenciaCodigo=data.get("ReferenciaCodigo"),
			Activo=data.get("Activo"),
			Latitud=data.get("Latitud"),
			Longitud=data.get("Longitud"),
			NombreComercial=data.get("NombreComercial"),
			Notas=data.get("Notas"),
		)

	def getPedidoVentaCabecera(self, fecha):
		url = f"{self.url_base}/changeRegister/pedidoventacabecera/{fecha}"
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
			FechaHoraModificado=data.get("FechaHoraModificado"),
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
			Codigo=data.get("Codigo"),
		)

	def getSalesOrderLine(self, fecha):
		url = f"{self.url_base}/changeRegister/pedidoventalinea/{fecha}"
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
			raise Exception(error_data.get("error", f"Error al obtener líneas de pedido de venta: {response.status_code}"))

		data = response.json()
		creacion = [self._map_pedido_venta_linea(item) for item in data.get("creacion", [])]
		modificar = [self._map_pedido_venta_linea(item) for item in data.get("modificar", [])]
		borrar = [self._map_pedido_venta_linea(item) for item in data.get("borrar", [])]

		return NetvyPedidoVentaLineaCollection(
			tabla=data.get("tabla"),
			fechaHoraDesde=data.get("fechaHoraDesde"),
			fechaHoraHasta=data.get("fechaHoraHasta"),
			creacion=creacion,
			modificar=modificar,
			borrar=borrar,
		)

	def _map_pedido_venta_linea(self, data):
		return NetvyPedidoVentaLineaAggregate(
			PedidoVentaLineaID=data.get("PedidoVentaLineaID"),
			CustomerID=data.get("CustomerID"),
			EmpresaID=data.get("EmpresaID"),
			UsuarioID=data.get("UsuarioID"),
			FechaHoraUsuario=data.get("FechaHoraUsuario"),
			Linea=data.get("Linea"),
			TipoLinea=data.get("TipoLinea"),
			ArticuloID=data.get("ArticuloID"),
			Nombre=data.get("Nombre"),
			Descripcion=data.get("Descripcion"),
			Cantidad=data.get("Cantidad"),
			PrecioVenta=data.get("PrecioVenta"),
			Dto1=data.get("Dto1"),
			Dto2=data.get("Dto2"),
			Dto3=data.get("Dto3"),
			ImporteVenta=data.get("ImporteVenta"),
			PrecioCoste=data.get("PrecioCoste"),
			Referencia=data.get("Referencia"),
			NotaInterna=data.get("NotaInterna"),
			NotaCliente=data.get("NotaCliente"),
			PedidoVentaCabeceraID=data.get("PedidoVentaCabeceraID"),
			FechaEntregaPrevistaCliente=data.get("FechaEntregaPrevistaCliente"),
			FechaEntregaPrevistaInterna=data.get("FechaEntregaPrevistaInterna"),
			CantidadOriginal=data.get("CantidadOriginal"),
			CantidadEntregada=data.get("CantidadEntregada"),
			Entregado=data.get("Entregado"),
			PorcentajeIVA=data.get("PorcentajeIVA"),
			PorcentajeRecargo=data.get("PorcentajeRecargo"),
			OfertaLineaID=data.get("OfertaLineaID"),
			FechaHoraModificado=data.get("FechaHoraModificado"),
			Codigo=data.get("Codigo"),
			CodigoAlternativo=data.get("CodigoAlternativo"),
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

	def getConfigTipoDocumentoID(self):
		if not self.tipo_documento:
			raise ValueError("TIPODOCUMENTO no está configurado en el archivo de configuración")

		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		url = f"{self.url_base}/generaltypes?key=TIPODOCUMENTO&match={self.tipo_documento}"
		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			raise Exception(f"Error al obtener TipoDocumentoID: {response.status_code}")

		data = response.json()
		if not isinstance(data, list) or len(data) == 0:
			raise Exception(f"No se encontró TipoDocumento con clave TIPODOCUMENTO y valor '{self.tipo_documento}'")

		tabla_general_id = data[0].get("TablaGeneralID")
		if tabla_general_id is None:
			raise Exception("TablaGeneralID no encontrado en la respuesta de TipoDocumento")

		init.NetvyTipoDocumentoID = tabla_general_id
		return tabla_general_id

	def getConfigTipoPersonaID(self):
		if not self.tipo_persona_mex:
			raise ValueError("TIPOPERSONAMEX no está configurado en el archivo de configuración")

		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		url = f"{self.url_base}/generaltypes?key=TIPOPERSONAMEX&match={self.tipo_persona_mex}"
		response = requests.get(url, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.get(url, headers=headers)

		if response.status_code != 200:
			raise Exception(f"Error al obtener TipoPersonaID: {response.status_code}")

		data = response.json()
		if not isinstance(data, list) or len(data) == 0:
			raise Exception(f"No se encontró TipoPersona con clave TIPOPERSONAMEX y valor '{self.tipo_persona_mex}'")

		tabla_general_id = data[0].get("TablaGeneralID")
		if tabla_general_id is None:
			raise Exception("TablaGeneralID no encontrado en la respuesta de TipoPersona")

		init.NetvyTipoPersonaID = tabla_general_id
		return tabla_general_id

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
			"clavetipomailingid":"cliente",
			"esCliente": True,
			"Activo": 1,
			"cliente":
			{
				"ClienteID":""  
			}
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

	def updateArticle(self, articulo):
		"""
		Actualiza un artículo existente en la API de Netvy.

		Args:
			articulo (NetvyArticuloAggregate): Aggregate con ArticuloID, Codigo y Nombre.

		Returns:
			bool: True si la actualización fue exitosa (HTTP 204).
		"""
		if articulo is None:
			raise ValueError("articulo es obligatorio")

		if articulo.ArticuloID is None:
			raise ValueError("ArticuloID es obligatorio")

		url = f"{self.url_base}/articulo/{articulo.ArticuloID}"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		body = {
			"ArticuloID": articulo.ArticuloID,
			"Codigo": articulo.Codigo or "",
			"Nombre": articulo.Nombre or "",
		}

		response = requests.patch(url, json=body, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.patch(url, json=body, headers=headers)

		if response.status_code != 204:
			raise Exception(
				f"Error al actualizar artículo en la API: "
				f"{response.status_code} - {response.text}"
			)

		return True

	def updateMailing(self, mailing):
		"""
		Actualiza un mailing existente en la API de Netvy.

		Args:
			mailing (NetvyMailingAggregate): Aggregate con MailingID y datos del body.

		Returns:
			bool: True si la actualización fue exitosa (HTTP 200).
		"""
		if mailing is None:
			raise ValueError("mailing es obligatorio")

		if mailing.MailingID is None:
			raise ValueError("MailingID es obligatorio")

		if init.NetvyMonedaID is None:
			raise ValueError("NetvyMonedaID no está configurado. Ejecute getCurrencieConfig() primero")

		url = f"{self.url_base}/thirdparty/{mailing.MailingID}"
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
			"esCliente": True,
			"Activo": 1,
			"cliente": {
				"clienteid": 0,
			},
		}

		response = requests.patch(url, json=body, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.patch(url, json=body, headers=headers)

		if response.status_code != 200:
			raise Exception(
				f"Error al actualizar mailing en la API: "
				f"{response.status_code} - {response.text}"
			)

		return True

	def updateLogisticArticle(self, articulo_logistica):
		"""
		Actualiza el stock logístico de un artículo en la API de Netvy.

		Args:
			articulo_logistica (ArticuloLogisticaAggregate): Aggregate con
				NetvyArticuloID y StockActual.

		Returns:
			bool: True si la actualización fue exitosa (HTTP 204).
		"""
		if articulo_logistica is None:
			raise ValueError("articulo_logistica es obligatorio")

		if articulo_logistica.NetvyArticuloID is None:
			raise ValueError("NetvyArticuloID es obligatorio")

		if articulo_logistica.StockActual is None:
			raise ValueError("StockActual es obligatorio")

		url = f"{self.url_base}/articulologisticaStock"
		headers = {
			"Authorization": f"Bearer {init.token.token}",
		}

		body = {
			"ArticuloID": articulo_logistica.NetvyArticuloID,
			"StockActual": articulo_logistica.StockActual,
		}

		response = requests.patch(url, json=body, headers=headers)

		if response.status_code == 401:
			self.refresh_token(init.token)
			headers["Authorization"] = f"Bearer {init.token.token}"
			response = requests.patch(url, json=body, headers=headers)

		if response.status_code != 204:
			raise Exception(
				f"Error al actualizar stock logístico del artículo en la API: "
				f"{response.status_code} - {response.text}"
			)

		return True
