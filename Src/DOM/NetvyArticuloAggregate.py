class NetvyArticuloAggregate:
	def __init__(
		self,
		ArticuloID=None,
		FamiliaID=None,
		SubFamiliaID=None,
		CustomerID=None,
		EmpresaID=None,
		UsuarioID=None,
		FechaHoraUsuario=None,
		FechaHoraModificado=None,
		Nombre=None,
		Activo=None,
		TipoArticuloID=None,
		Codigo=None,
		Observacion=None,
		Descripcion=None,
		CodigoAlternativo=None,
	):
		self.ArticuloID = ArticuloID
		self.FamiliaID = FamiliaID
		self.SubFamiliaID = SubFamiliaID
		self.CustomerID = CustomerID
		self.EmpresaID = EmpresaID
		self.UsuarioID = UsuarioID
		self.FechaHoraUsuario = FechaHoraUsuario
		self.FechaHoraModificado = FechaHoraModificado
		self.Nombre = Nombre
		self.Activo = Activo
		self.TipoArticuloID = TipoArticuloID
		self.Codigo = Codigo
		self.Observacion = Observacion
		self.Descripcion = Descripcion
		self.CodigoAlternativo = CodigoAlternativo