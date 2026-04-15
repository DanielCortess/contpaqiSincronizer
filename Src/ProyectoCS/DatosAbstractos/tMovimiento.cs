using ContpaqiConnector.Constantes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.DatosAbstractos
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi, Pack = 4)]
    public struct tMovimiento
    {
        // Consecutivo del movimiento.
        public int aConsecutivo;

        // Unidades del movimiento.
        public double aUnidades;

        // Precio del movimiento (para doctos. de venta ).
        public double aPrecio;

        // Costo del movimiento (para doctos. de compra).
        public double aCosto;

        // Códogo del producto o servicio.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodProdSer;

        // Código del Almacén.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodAlmacen;

        // Referencia del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongReferencia)]
        public string aReferencia;

        // Código de la clasificación.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodClasificacion;
    }
}
