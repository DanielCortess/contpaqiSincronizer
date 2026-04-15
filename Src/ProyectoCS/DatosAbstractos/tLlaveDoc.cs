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
    public struct tLlaveDoc
    {
        // Código del concepto del documento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aCodConcepto;

        // Serie del documento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongSerie)]
        public string aSerie;

        // Folio del documento.
        public double aFolio;
    }
}
