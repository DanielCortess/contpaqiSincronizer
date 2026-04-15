using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.DatosAbstractos
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi, Pack = 4)]
    public struct tTipoProducto
    {
        // Tipo de dato abstracto: tSeriesCapas.
        public tSeriesCapas aSeriesCapas;

        // Tipo de dato abstracto: Caracteristicas.
        public tCaracteristicas aCaracteristicas;
    }
}
