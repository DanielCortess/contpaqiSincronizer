class NetvyAlbaranVentaAggregate:
	def __init__(
		self,
		Serie=None,
		FechaAlbaran=None,
		Almacen=None,
		FechaHoraCreacion=None,
		ProyectoOFID="",
		ClienteFactura=None,
		FormaPago=None,
		Moneda=None,
		Lineas=None,
	):
		self.Serie = Serie
		self.FechaAlbaran = FechaAlbaran
		self.Almacen = Almacen
		self.FechaHoraCreacion = FechaHoraCreacion
		self.ProyectoOFID = ProyectoOFID
		self.ClienteFactura = ClienteFactura if ClienteFactura is not None else {}
		self.FormaPago = FormaPago if FormaPago is not None else []
		self.Moneda = Moneda
		self.Lineas = Lineas if Lineas is not None else []