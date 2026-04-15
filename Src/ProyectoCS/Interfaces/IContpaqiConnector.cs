using System.Runtime.InteropServices;

namespace ContpaqiConnector.Interfaces
{
    [ComVisible(true)]
    [Guid("E928EE9F-4FC5-4281-A6AD-83C858A81795")]
    [InterfaceType(ComInterfaceType.InterfaceIsDual)]
    public interface IContpaqiConnector
    {
        // Cliente
        int CrearCliente(string codigo, string razonSocial, string rfc);
        void ActualizaCliente(string codigo, string razonSocia, string rfc);
        void EliminarCliente(string codigo);

        string BuscarClientePorCodigo(string codigo);
        string BuscarClientePorId(int id);
        string BuscarClientes();

        // Producto
        int CrearProducto(string codigo, string nombre);
        void ActualizaProducto(string codigo, string nombre);
        void EliminarProducto(string codigo);
        string BuscarProductoPorCodigo(string codigo);
        string BuscarProductoPorId(int id);
        string BuscarProductos();

        // Documentos
        int CrearDocumento(
            string conceptoCodigo,
            string clienteCodigo,
            string referencia,
            string observaciones
        );

        int CrearFactura(
            string conceptoCodigo,
            string clienteCodigo,
            string referencia,
            string observaciones
        );

        int CrearPedido(
            string conceptoCodigo,
            string clienteCodigo,
            string referencia,
            string observaciones
        );

        int CrearCompra(
            string conceptoCodigo,
            string proveedorCodigo,
            string referencia,
            string observaciones
        );

        int CrearAbono(
            string conceptoCodigo,
            string clienteCodigo,
            double total,
            string referencia,
            string observaciones
        );

        // Movimientos
        int AgregarMovimiento(
            int documentoId,
            string productoCodigo,
            double unidades,
            double precio,
            string referencia,
            string observaciones
        );
    }
}

