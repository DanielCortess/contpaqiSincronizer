class NetvyMailingCollection:
	def __init__(
		self,
		tabla=None,
		fechaHoraDesde=None,
		fechaHoraHasta=None,
		creacion=None,
		modificar=None,
		borrar=None,
	):
		self.tabla = tabla
		self.fechaHoraDesde = fechaHoraDesde
		self.fechaHoraHasta = fechaHoraHasta
		self.creacion = creacion if creacion is not None else []
		self.modificar = modificar if modificar is not None else []
		self.borrar = borrar if borrar is not None else []