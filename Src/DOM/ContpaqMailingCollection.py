class ContpaqMailingCollection:
	def __init__(
		self,
		tabla=None,
		fechaHoraDesde=None,
		fechaHoraHasta=None,
		creacion_modificar_borrar=None
	):
		self.tabla = tabla
		self.fechaHoraDesde = fechaHoraDesde
		self.fechaHoraHasta = fechaHoraHasta
		self.creacion_modificar_borrar = creacion_modificar_borrar if creacion_modificar_borrar is not None else []