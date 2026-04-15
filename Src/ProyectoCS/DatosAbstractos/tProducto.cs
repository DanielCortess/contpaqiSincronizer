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
    public struct tProducto
    {
        // Código del producto.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoProducto;

        // Nombre del producto.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cNombreProducto;

        // Descripción del producto.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombreProducto)]
        public string cDescripcionProducto;

        // 1- Producto, 2 - Paquete, 3 - Servicio
        public int cTipoProducto;

        // Fecha de alta del producto.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string cFechaAltaProducto;

        // Fecha de baja del producto.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string cFechaBaja;

        // 0 - Baja Lógica, 1 – Alta
        public int cStatusProducto;

        // Control de exixtencia.
        public int cControlExistencia;

        // 1. Costo Promedio Base a Entradas, Costo Promedio Base a Entradas Almacen Último costo, 2. UEPS, 3. PEPS, 4. Costo
        // específico, 5. Costo Estandar.
        public int cMetodoCosteo;

        // Código de la unidad base.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoUnidadBase;

        // Código de la unidad no convertible.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoUnidadNoConvertible;

        // Lista de precios 1.
        public double cPrecio1;

        // Lista de precios 2.
        public double cPrecio2;

        // Lista de precios 3.
        public double cPrecio3;

        // Lista de precios 4.
        public double cPrecio4;

        // Lista de precios 5.
        public double cPrecio5;

        // Lista de precios 6.
        public double cPrecio6;

        // Lista de precios 7.
        public double cPrecio7;

        // Lista de precios 8.
        public double cPrecio8;

        // Lista de precios 9.
        public double cPrecio9;

        // Lista de precios 10.
        public double cPrecio10;

        // Impuesto 1.
        public double cImpuesto1;

        // Impuesto 2.
        public double cImpuesto2;

        // Impuesto 3.
        public double cImpuesto3;

        // Retención 1.
        public double cRetencion1;

        // Retención 1.
        public double cRetencion2;

        // Nombre de la caracteristica 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cNombreCaracteristica1;

        // Nombre de la caracteristica 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cNombreCaracteristica2;

        // Nombre de la caracteristica 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cNombreCaracteristica3;

        // Código del valor de la clasificación 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion1;

        // Código del valor de la clasificación 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion2;

        // Código del valor de la clasificación 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion3;

        // Código del valor de la clasificación 4.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion4;

        // Código del valor de la clasificación 5.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion5;

        // Código del valor de la clasificación 6.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion6;

        // Texto extra 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTextoExtra)]
        public string cTextoExtra1;

        // Texto extra 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTextoExtra)]
        public string cTextoExtra2;

        // Texto extra 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTextoExtra)]
        public string cTextoExtra3;

        // Fecha extra.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string cFechaExtra;

        // Importe Extra 1.
        public double cImporteExtra1;

        // Importe Extra 2.
        public double cImporteExtra2;

        // Importe Extra 3.
        public double cImporteExtra3;

        // Importe Extra 4.
        public double cImporteExtra4;
    }
}
