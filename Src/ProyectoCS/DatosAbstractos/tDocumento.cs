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
    public struct tDocumento
    {
        // Folio del documento.
        public double aFolio;

        // Moneda del documento. 1 = Pesos MN, 2 = Moneda extranjera.
        public int aNumMoneda;

        // Tipo de cambio del documento.
        public double aTipoCambio;

        // Importe del documento. Sólo se usa en documentos de cargo/abono.
        public double aImporte;

        // No tiene uso, valor por omisión = 0 (cero).
        public double aDescuentoDoc1;

        // No tiene uso, valor por omisión = 0 (cero).
        public double aDescuentoDoc2;

        // Valor mayor a 5 que indica una aplicación diferente a los PAQ's.
        public int aSistemaOrigen;

        // Código del concepto del documento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodConcepto;

        // Serie del documento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongSerie)]
        public string aSerie;

        // Fecha del documento. Formato mm/dd/aaaa Las “/” diagonales son parte del formato.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string aFecha;

        // Código del Cliente/Proveedor.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodigoCteProv;

        // Código del Agente.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodigoAgente;

        // Referencia del Documento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongReferencia)]
        public string aReferencia;

        // No tiene uso, valor por omisión = 0 (cero).
        public int aAfecta;

        // Importes de gastos para las compras.
        public double aGasto1;

        // Importes de gastos para las compras.
        public double aGasto2;

        // Importes de gastos para las compras.
        public double aGasto3;
    }
}
