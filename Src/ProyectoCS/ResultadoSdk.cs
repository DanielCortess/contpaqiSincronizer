using ContpaqiConnector.SDK;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector
{
    public class ResultadoSdk
    {
        public const int Exitoso = 0;

        public static string LeerMensajeError(int numeroError)
        {
            var mensaje = new StringBuilder(512);
            ComercialSdk.fError(numeroError, mensaje, 512);
            return mensaje.ToString();
        }
    }
}
