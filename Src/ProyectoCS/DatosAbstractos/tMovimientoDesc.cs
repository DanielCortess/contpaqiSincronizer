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
    public struct tMovimientoDesc
    {
        // Consecutivo del movimiento.
        public int aConsecutivo;
        
        // Unidades del movimiento.
        public double aUnidades;
        
        // Precio del movimiento (para doctos. de venta).
        public double aPrecio;
        
        // Costo del movimiento (para doctos. de compra).
        public double aCosto;
        
        // Porcentaje del Descuento 1.
        public double aPorcDescto1;
        
        // Importe del Descuento 1.
        public double aImporteDescto1;
        
        // Porcentaje del Descuento 2.
        public double aPorcDescto2;
        
        // Importe del Descuento 2.
        public double aImporteDescto2;
        
        // Porcentaje del Descuento 3.
        public double aPorcDescto3;
        
        // Importe del Descuento 3.
        public double aImporteDescto3;
        
        // Porcentaje del Descuento 4.
        public double aPorcDescto4;
        
        // Importe del Descuento 4.
        public double aImporteDescto4;
        
        // Porcentaje del Descuento 5.
        public double aPorcDescto5;
        
        // Importe del Descuento 5.
        public double aImporteDescto5;
        
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
