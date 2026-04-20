class ContpaqPedidoVentaCabeceraAggregate:

	def __init__(
		self,
		# Campos de salida (se asignan al crear)
		CIDMOVIMIENTO,
		CIDDOCUMENTO,
		CNUMEROMOVIMIENTO,
		CIDDOCUMENTODE,
		CIDPRODUCTO,
		# Campos de entrada para crear el documento
		CCODIGOCONCEPTO,
		CCODIGOCTEPROV,
		CCODIGOPRODUCTO,
		CUNIDADES,
		CPRECIO,
		CFECHA=None,
		CSERIE="",
		CFOLIO=0.0,
		CNUMMONEDA=1,
		CTIPOCAMBIO=1.0,
		CREFERENCIA="",
		COBSERVACIONES="",
		CCODALMACEN="1",
	):
		# Campos de salida asignados por el SDK al crear
		self.CIDMOVIMIENTO = CIDMOVIMIENTO
		self.CIDDOCUMENTO = CIDDOCUMENTO
		self.CNUMEROMOVIMIENTO = CNUMEROMOVIMIENTO
		self.CIDDOCUMENTODE = CIDDOCUMENTODE
		self.CIDPRODUCTO = CIDPRODUCTO

		# Campos necesarios para crear el documento en Contpaqi
		self.CCODIGOCONCEPTO = CCODIGOCONCEPTO   # Código del concepto (ej: "PEDI")
		self.CCODIGOCTEPROV = CCODIGOCTEPROV     # Código del cliente
		self.CFECHA = CFECHA                     # Fecha MM/DD/YYYY (None = hoy)
		self.CSERIE = CSERIE                     # Serie del documento
		self.CFOLIO = CFOLIO                     # Folio (0 = siguiente automático)
		self.CNUMMONEDA = CNUMMONEDA             # Número de moneda (1 = MXN)
		self.CTIPOCAMBIO = CTIPOCAMBIO           # Tipo de cambio
		self.CREFERENCIA = CREFERENCIA           # Referencia del documento
		self.COBSERVACIONES = COBSERVACIONES     # Observaciones del documento

		# Campos para crear el movimiento dentro del documento
		self.CCODIGOPRODUCTO = CCODIGOPRODUCTO   # Código del producto
		self.CUNIDADES = CUNIDADES               # Cantidad
		self.CPRECIO = CPRECIO                   # Precio unitario
		self.CCODALMACEN = CCODALMACEN           # Código del almacén (default "1")
