class ContpaqAlbaranVentaCollection:
	def __init__(
		self,
		tabla=None,
		fechaHoraDesde=None,
		fechaHoraHasta=None,
		creacion=None,
	):
		self.tabla = tabla
		self.fechaHoraDesde = fechaHoraDesde
		self.fechaHoraHasta = fechaHoraHasta
		self.creacion = creacion if creacion is not None else []