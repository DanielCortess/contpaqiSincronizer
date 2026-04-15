using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector
{
    public static class LlavesRegistroWindowsSdk
    {
        /// <summary>
        ///     Nombre de la llave de registro de windows utiliza para buscar la ruta del SDK de CONTPAQi Adminpaq.
        /// </summary>
        public const string Adminpaq = @"SOFTWARE\\Computación en Acción, SA CV\\AdminPAQ";

        /// <summary>
        ///     Nombre de la llave de registro de windows utiliza para buscar la ruta del SDK de CONTPAQi Comercial.
        /// </summary>
        public const string Comercial = @"SOFTWARE\\Computación en Acción, SA CV\\CONTPAQ I COMERCIAL";

        /// <summary>
        ///     Nombre de la llave de registro de windows utiliza para buscar la ruta del SDK de CONTPAQi Factura Electronica.
        /// </summary>
        public const string FacturaElectronica = @"SOFTWARE\\Computación en Acción, SA CV\\CONTPAQ I Facturacion";

        /// <summary>
        ///     Nombre del campo en el registro de Windows donde se encuentra la ruta del SDK.
        /// </summary>
        public const string NombreCampoRutaSdk = "DIRECTORIOBASE";

    }

}
