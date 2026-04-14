import requests

from APP import init
from INF.DOM.LoginToken import LoginToken


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