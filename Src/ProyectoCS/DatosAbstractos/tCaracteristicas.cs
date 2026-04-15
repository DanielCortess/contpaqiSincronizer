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
    public struct tCaracteristicas
    {
        // Unidades del movimiento.
        public double aUnidades;

        // Valor de la caracteristica 1 del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string aValorCaracteristica1;

        // Valor de la caracteristica 2 del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string aValorCaracteristica2;

        // Valor de la caracteristica 3 del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string aValorCaracteristica3;
    }

}
