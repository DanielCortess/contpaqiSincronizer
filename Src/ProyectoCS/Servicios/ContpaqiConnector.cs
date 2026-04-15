using ContpaqiConnector.DatosAbstractos;
using ContpaqiConnector.Interfaces;
using ContpaqiConnector.Modelo;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;

namespace ContpaqiConnector.Servicios
{
    [ComVisible(true)]
    [Guid("D7AF3257-BFA4-4AEF-A262-10CD1FDA7951")]
    [ClassInterface(ClassInterfaceType.None)]
    public class ContpaqiConnector : IContpaqiConnector
    {
        // Cliente
        public int CrearCliente(string codigo, string razonSocial, string rfc)
        {
            try
            {
                IniciarEmpresa();

                var cliente = new ClienteSdk
                {
                    Codigo = codigo,
                    RazonSocial = razonSocial,
                    Rfc = rfc,
                    Tipo = 1
                };

                return ClienteSdk.CrearCliente(cliente);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return 0;
            }
            finally
            {
                Cerrar();
            }
        }

        public void ActualizaCliente(string codigo, string razonSocia, string rfc)
        {
            try
            {
                IniciarEmpresa();

                ClienteSdk cliente = ClienteSdk.BuscarClientePorCodigo(codigo);

                cliente.RazonSocial = razonSocia;
                cliente.Rfc = rfc;

                ClienteSdk.ActualizarCliente(cliente);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            finally
            {
                Cerrar();
            }
        }

        public void EliminarCliente(string codigo)
        {
            try
            {
                IniciarEmpresa();

                ClienteSdk cliente = ClienteSdk.BuscarClientePorCodigo(codigo);

                ClienteSdk.EliminarCliente(cliente);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            finally
            {
                Cerrar();
            }
        }

        public string BuscarClientePorCodigo(string codigo)
        {
            try
            {
                IniciarEmpresa();

                ClienteSdk cliente = ClienteSdk.BuscarClientePorCodigo(codigo);

                return cliente == null ? "" : cliente.ToString();
            }
            finally
            {
                Cerrar();
            }
        }

        public string BuscarClientePorId(int id)
        {
            try
            {
                IniciarEmpresa();

                ClienteSdk cliente = ClienteSdk.BuscarClientePorId(id);

                return cliente == null ? "" : cliente.ToString();
            }
            finally
            {
                Cerrar();
            }
        }

        public string BuscarClientes()
        {
            try
            {
                IniciarEmpresa();

                var clientes = ClienteSdk.BuscarClientes();

                return string.Join(Environment.NewLine, clientes.Select(c => c.ToString()));
            }
            finally
            {
                Cerrar();
            }
        }

        // Producto
        public int CrearProducto(string codigo, string nombre)
        {
            try
            {
                IniciarEmpresa();

                var producto = new ProductoSdk 
                { 
                    Codigo = codigo, 
                    Nombre = nombre, 
                    Tipo = 1 
                };

                return ProductoSdk.CrearProducto(producto);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return 0;
            }
            finally
            {
                Cerrar();
            }
        }

        public void ActualizaProducto(string codigo, string nombre)
        {
            try
            {
                IniciarEmpresa();

                ProductoSdk producto = ProductoSdk.BuscarProductoPorCodigo(codigo);

                producto.Nombre = nombre;

                ProductoSdk.ActualizarProducto(producto);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            finally
            {
                Cerrar();
            }
        }

        public void EliminarProducto(string codigo)
        {
            try
            {
                IniciarEmpresa();

                ProductoSdk producto = ProductoSdk.BuscarProductoPorCodigo(codigo);

                ProductoSdk.EliminarProducto(producto);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
            finally
            {
                Cerrar();
            }
        }

        public string BuscarProductoPorCodigo(string codigo)
        {
            try
            {
                IniciarEmpresa();

                ProductoSdk producto = ProductoSdk.BuscarProductoPorCodigo(codigo);

                return producto == null ? "" : producto.ToString();
            }
            finally
            {
                Cerrar();
            }
        }

        public string BuscarProductoPorId(int id)
        {
            try
            {
                IniciarEmpresa();

                ProductoSdk producto = ProductoSdk.BuscarProductoPorId(id);

                return producto == null ? "" : producto.ToString();
            }
            finally
            {
                Cerrar();
            }
        }

        public string BuscarProductos()
        {
            try
            {
                IniciarEmpresa();

                var productos = ProductoSdk.BuscarProductos();

                return string.Join(Environment.NewLine, productos.Select(c => c.ToString()));
            }
            finally
            {
                Cerrar();
            }
        }

        // Documentos
        public int CrearDocumento(string conceptoCodigo,string clienteCodigo,string referencia,string observaciones)
        {
            try
            {
                IniciarEmpresa();

                ConceptoSdk concepto = ConceptoSdk.BuscarConceptoPorCodigo(conceptoCodigo);
                ClienteSdk cliente = ClienteSdk.BuscarClientePorCodigo(clienteCodigo);

                tLlaveDoc folio = DocumentoSdk.BuscarSiguienteSerieYFolio(concepto.Codigo);

                var documento = new DocumentoSdk
                {
                    ConceptoId = concepto.Id,
                    Fecha = DateTime.Today,
                    Serie = folio.aSerie,
                    Folio = folio.aFolio,
                    ClienteId = cliente.Id,
                    Referencia = referencia,
                    Observaciones = observaciones
                };

                return DocumentoSdk.CrearDocumento(documento);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return 0;
            }
            finally
            {
                Cerrar();
            }
        }

        public int CrearFactura(string conceptoCodigo, string clienteCodigo, string referencia, string observaciones)
        {
            int documentoId = CrearDocumento(
                conceptoCodigo,
                clienteCodigo,
                referencia,
                observaciones
            );

            return documentoId;
        }

        public int CrearPedido(string conceptoCodigo, string clienteCodigo, string referencia, string observaciones)
        {
            int documentoId = CrearDocumento(
                conceptoCodigo,
                clienteCodigo,
                referencia,
                observaciones
            );

            return documentoId;
        }
        public int CrearCompra(string conceptoCodigo, string proveedorCodigo, string referencia, string observaciones)
        {
            return CrearDocumento(
                conceptoCodigo,
                proveedorCodigo,
                referencia,
                observaciones
            );
        }

        public int CrearAbono(string conceptoCodigo, string clienteCodigo, double total, string referencia, string observaciones)
        {
            try
            {
                IniciarEmpresa();

                ConceptoSdk concepto = ConceptoSdk.BuscarConceptoPorCodigo(conceptoCodigo);
                ClienteSdk cliente = ClienteSdk.BuscarClientePorCodigo(clienteCodigo);

                tLlaveDoc folio = DocumentoSdk.BuscarSiguienteSerieYFolio(concepto.Codigo);

                var documento = new DocumentoSdk
                {
                    ConceptoId = concepto.Id,
                    Fecha = DateTime.Today,
                    Serie = folio.aSerie,
                    Folio = folio.aFolio,
                    ClienteId = cliente.Id,
                    Referencia = referencia,
                    Observaciones = observaciones,
                    Total = total
                };

                return DocumentoSdk.CrearDocumentoCargoAbono(documento);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return 0;
            }
            finally
            {
                Cerrar();
            }
        }

        // Movimientos

        public int AgregarMovimiento(int documentoId, string productoCodigo, double unidades, double precio, string referencia, string observaciones)
        {
            try
            {
                IniciarEmpresa();

                ProductoSdk producto = ProductoSdk.BuscarProductoPorCodigo(productoCodigo);

                var movimiento = new MovimientoSdk
                {
                    DocumentoId = documentoId,
                    ProductoId = producto.Id,
                    Unidades = unidades,
                    Precio = precio,
                    Referencia = referencia,
                    Observaciones = observaciones
                };

                return MovimientoSdk.CrearMovimiento(movimiento);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
                return 0;
            }
            finally
            {
                Cerrar();
            }
        }

        // Global
        private void IniciarEmpresa()
        {
            ConexionSdk.IniciarSdk("SUPERVISOR", "");

            var empresa = EmpresaSdk.BuscarEmpresas().First(e => e.Id == 2);

            ConexionSdk.AbrirEmpresa(empresa.Ruta);
        }

        private void Cerrar()
        {
            ConexionSdk.CerrarEmpresa();
            ConexionSdk.TerminarSdk();
        }




        // Iniciar 
        //// 1. Inicializar el SDK
        //ConexionSdk.IniciarSdk("SUPERVISOR", "");

        //// Buscar empresas
        //List<EmpresaSdk> empresaList = EmpresaSdk.BuscarEmpresas();

        //// Mostrar el listado de empresas
        //foreach (EmpresaSdk empresaSdk in empresaList.OrderBy(e => e.Nombre))
        //    Console.WriteLine($"Id:{empresaSdk.Id} Nombre:{empresaSdk.Nombre} Ruta:{empresaSdk.Ruta}");

        //// Selecciona una empresa del listado. Ingresa el Id:
        //string empresaKey = "2";
        //int empresaId = int.Parse(empresaKey ?? throw new InvalidOperationException());
        //EmpresaSdk empresaSeleccionada = empresaList.First(e => e.Id == empresaId);

        //// Abriendo empresa
        //ConexionSdk.AbrirEmpresa(empresaSeleccionada.Ruta);

    }
}

