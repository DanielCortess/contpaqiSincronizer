class ContpaqArticuloLogisticaCollection:
	def __init__(
		self,
		creacion_modificar_borrar=None,
	):
		self.creacion_modificar_borrar = creacion_modificar_borrar if creacion_modificar_borrar is not None else []
