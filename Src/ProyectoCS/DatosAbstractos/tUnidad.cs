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
    public struct tUnidad
    {
        // Nombre de la unidad.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cNombreUnidad;

        // Abreviatura.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongAbreviatura)]
        public string cAbreviatura;

        // Valor de despliegue.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongAbreviatura)]
        public string cDespliegue;
    }
}
