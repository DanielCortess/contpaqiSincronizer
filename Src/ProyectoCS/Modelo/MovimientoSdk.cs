using ContpaqiConnector.Constantes;
using ContpaqiConnector.DatosAbstractos;
using ContpaqiConnector.Extensiones;
using ContpaqiConnector.SDK;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.Modelo
{

    // Tabla admMovimientos – Tabla de Movimientos
    public sealed class MovimientoSdk
    {
        // Campo CIDDOCUMENTO - Identificador del documento dueño del movimiento.
        public int DocumentoId { get; set; }

        // Campo CIDMOVIMIENTO - Identificador del movimiento.
        public int Id { get; set; }

        // Campo COBSERVAMOV - Observaciones del movimiento.
        public string Observaciones { get; set; }

        // Campo CPRECIO - Precio del producto.
        public double Precio { get; set; }

        // Campo CIDPRODUCTO - Identificador del producto del movimiento
        public int ProductoId { get; set; }

        // Campo CREFERENCIA - Referencia del movimiento.
        public string Referencia { get; set; }

        // Campo CTOTAL - Importe del total del movimiento.
        public double Total { get; set; }

        // Campo CUNIDADES - Cantidad de unidad base del movimiento.
        public double Unidades { get; set; }

        // Actualiza los datos de un movimiento.
        // <param name="movimiento">Movimiento con los datos a actualizar.</param>
        public static void ActualizarMovimiento(MovimientoSdk movimiento)
        {
            // Buscar el movimiento
            // Si el movimiento existe el SDK se posiciona en el registro
            ComercialSdk.fBuscarIdMovimiento(movimiento.Id).TirarSiEsError();

            // Activar el modo de edición
            ComercialSdk.fEditarMovimiento().TirarSiEsError();

            // Actualizar los campos del registro donde el SDK esta posicionado
            ComercialSdk.fSetDatoMovimiento("COBSERVAMOV", movimiento.Observaciones).TirarSiEsError();

            // Guardar los cambios realizados al registro
            ComercialSdk.fGuardaMovimiento().TirarSiEsError();
        }

        // Busca un movimiento por id.
        // <param name="movimientoId">El id del movimiento a buscar.</param>
        // <returns>Un movimiento con sus datos asignados.</returns>
        public static MovimientoSdk BuscarMovimientoPorId(int movimientoId)
        {
            // Buscar el movimiento por id
            // Si el movimientos existe el SDK se posiciona en el registro
            ComercialSdk.fBuscarIdMovimiento(movimientoId).TirarSiEsError();

            // Leer los datos del registro donde el SDK esta posicionado
            return LeerDatosMovimiento();
        }

        // Busca movimientos por filtro.
        // <param name="documentoId">El id del documento utilizado para filtrar.</param>
        // <returns>Lista de movimientos del documento.</returns>
        public static List<MovimientoSdk> BuscarMovimientosPorFiltro(int documentoId)
        {
            var movimientosList = new List<MovimientoSdk>();

            // Cancelar filtro
            ComercialSdk.fCancelaFiltroMovimiento().TirarSiEsError();

            // Filtrar movimientos
            ComercialSdk.fSetFiltroMovimiento(documentoId).TirarSiEsError();

            // Posicionar el SDK en el primer registro
            ComercialSdk.fPosPrimerMovimiento().TirarSiEsError();

            // Leer los datos del registro donde el SDK esta posicionado
            movimientosList.Add(LeerDatosMovimiento());

            // Crear un loop y posicionar el SDK en el siguiente registro
            while (ComercialSdk.fPosSiguienteMovimiento() == SdkConstantes.CodigoExito)
            {
                // Leer los datos del registro donde el SDK esta posicionado
                movimientosList.Add(LeerDatosMovimiento());

                // Checar si el SDK esta posicionado en el ultimo registro
                // Si el SDK esta posicionado en el ultimo registro salir del loop
                if (ComercialSdk.fPosMovimientoEOF() == 1) break;
            }

            // Cancelar filtro
            ComercialSdk.fCancelaFiltroMovimiento().TirarSiEsError();

            return movimientosList;
        }

        // Crea un nuevo movimiento.
        // <param name="movimiento">Movimiento a crear.</param>
        // <returns></returns>
        public static int CrearMovimiento(MovimientoSdk movimiento)
        {
            ProductoSdk producto = ProductoSdk.BuscarProductoPorId(movimiento.ProductoId);

            // Instanciar un movimiento con la estructura tMovimiento del SDK
            var nuevoMovimiento = new tMovimiento
            {
                aCodProdSer = producto.Codigo,
                aUnidades = movimiento.Unidades,
                aPrecio = movimiento.Precio,
                aReferencia = movimiento.Referencia,
                aCodAlmacen = "1"
            };

            // Declarar una variable donde se asignara el id del movimiento nuevo
            var nuevoMovimientoId = 0;

            // Crear movimiento nuevo
            ComercialSdk.fAltaMovimiento(movimiento.DocumentoId, ref nuevoMovimientoId, ref nuevoMovimiento).TirarSiEsError();

            movimiento.Id = nuevoMovimientoId;

            // Editar los datos extras que no son parte de la estructura tMovimiento
            ActualizarMovimiento(movimiento);

            return nuevoMovimientoId;
        }

        // Eliminar un movimiento.
        // <param name="movimiento">El movimiento a eliminar.</param>
        public static void EliminarMovimiento(MovimientoSdk movimiento)
        {
            // Buscar el movimiento
            // Si el movimiento existe el SDK se posiciona en el registro
            ComercialSdk.fBuscarIdMovimiento(movimiento.Id).TirarSiEsError();

            // Eliminar movimiento
            ComercialSdk.fBorraMovimiento(movimiento.DocumentoId, movimiento.Id).TirarSiEsError();
        }

        // Lee los datos del movimiento donde el SDK esta posicionado.
        // <returns>Regresa un movimiento con los sus datos asignados.</returns>
        private static MovimientoSdk LeerDatosMovimiento()
        {
            // Declarar variables a leer de la base de datos
            var idBd = new StringBuilder(3000);
            var documentoIdBd = new StringBuilder(3000);
            var productoIdBd = new StringBuilder(3000);
            var unidadesBd = new StringBuilder(3000);
            var precioBd = new StringBuilder(3000);
            var referenciaBd = new StringBuilder(3000);
            var observacionesBd = new StringBuilder(3000);
            var totalBd = new StringBuilder(3000);

            // Leer los datos del registro donde el SDK esta posicionado
            ComercialSdk.fLeeDatoMovimiento("CIDMOVIMIENTO", idBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("CIDDOCUMENTO", documentoIdBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("CIDPRODUCTO", productoIdBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("CUNIDADES", unidadesBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("CPRECIO", precioBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("CREFERENCIA", referenciaBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("COBSERVAMOV", observacionesBd, 3000).TirarSiEsError();
            ComercialSdk.fLeeDatoMovimiento("CTOTAL", totalBd, 3000).TirarSiEsError();

            // Instanciar un movimiento y asignar los datos de la base de datos
            return new MovimientoSdk
            {
                Id = int.Parse(idBd.ToString()),
                DocumentoId = int.Parse(documentoIdBd.ToString()),
                ProductoId = int.Parse(productoIdBd.ToString()),
                Unidades = double.Parse(unidadesBd.ToString()),
                Precio = double.Parse(precioBd.ToString()),
                Referencia = referenciaBd.ToString(),
                Observaciones = observacionesBd.ToString(),
                Total = double.Parse(totalBd.ToString())
            };
        }

        public override string ToString()
        {
            return $"{Id} - {ProductoSdk.BuscarProductoPorId(ProductoId).Nombre} - {Unidades} - {Precio} - {Total:C}";
        }
    }
}
