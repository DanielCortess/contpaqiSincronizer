using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.Constantes
{
    public static class LlavesRegistroWindowsSdk
    {
        // Nombre de la llave de registro de windows utiliza para buscar la ruta del SDK de CONTPAQi Adminpaq.
        public const string Adminpaq = @"SOFTWARE\\Computación en Acción, SA CV\\AdminPAQ";

        // Nombre de la llave de registro de windows utiliza para buscar la ruta del SDK de CONTPAQi Comercial.
        public const string Comercial = @"SOFTWARE\\Computación en Acción, SA CV\\CONTPAQ I COMERCIAL";

        // Nombre de la llave de registro de windows utiliza para buscar la ruta del SDK de CONTPAQi Factura Electronica.
        public const string FacturaElectronica = @"SOFTWARE\\Computación en Acción, SA CV\\CONTPAQ I Facturacion";

        // Nombre del campo en el registro de Windows donde se encuentra la ruta del SDK.
        public const string NombreCampoRutaSdk = "DIRECTORIOBASE";
    }
}
