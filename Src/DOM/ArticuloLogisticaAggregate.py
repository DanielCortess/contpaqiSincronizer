class ArticuloLogisticaAggregate:
	def __init__(
		self,
		NetvyArticuloID=None,
		ContpaqArticuloID=None,
		StockActual=None,
	):
		self.NetvyArticuloID = NetvyArticuloID
		self.ContpaqArticuloID = ContpaqArticuloID
		self.StockActual = StockActual
