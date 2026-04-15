using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector
{
    /// <summary>
    ///     Formatos de fecha utilizados por el SDK.
    /// </summary>
    public static class FormatosFechaSdk
    {
        /// <summary>
        ///     Formato para leer fechas del SDK de Comercial.
        /// </summary>
        public const string Comercial = "MM/dd/yyyy HH:mm:ss:fff";

        /// <summary>
        ///     Formato para leer fechas del SDK de Factura Electronica.
        /// </summary>
        public const string FacturaElectronica = "M/d/yyyy HH:mm:ss:fff";

        /// <summary>
        ///     Formato para asignar fechas con el SDK.
        /// </summary>
        public const string Fecha = "MM/dd/yyyy";
    }
}
