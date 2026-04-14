class LoginToken:
	def __init__(
		self,
		usuarioID=None,
		empresaID=None,
		isAdmin=None,
		idiomaID=None,
		customerID=None,
		sessionID=None,
		refreshToken=None,
		token=None,
	):
		self.usuarioID = usuarioID
		self.empresaID = empresaID
		self.isAdmin = isAdmin
		self.idiomaID = idiomaID
		self.customerID = customerID
		self.sessionID = sessionID
		self.refreshToken = refreshToken
		self.token = token