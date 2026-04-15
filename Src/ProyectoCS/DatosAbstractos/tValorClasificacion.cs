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
    public struct tValorClasificacion
    {
        // Clasificación.
        public int cClasificacionDe;

        // Número de la clasificación.
        public int cNumClasificacion;

        // Código del valor de la clasificación.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacion;

        // Valor de la clasificación.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cValorClasificacion;
    }

}
