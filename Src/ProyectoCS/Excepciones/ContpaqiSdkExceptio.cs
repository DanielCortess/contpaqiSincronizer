using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.Excepciones
{
    public class ContpaqiSdkException : Exception
    {
        public ContpaqiSdkException(int codigoErrorSdk)
        {
            CodigoErrorSdk = codigoErrorSdk;
        }

        public ContpaqiSdkException(int codigoErrorSdk, string message) : base(message)
        {
            CodigoErrorSdk = codigoErrorSdk;
            MensajeErrorSdk = message;
        }

        public ContpaqiSdkException(int codigoErrorSdk, string message, Exception innerException) : base(message, innerException)
        {
            CodigoErrorSdk = codigoErrorSdk;
            MensajeErrorSdk = message;
        }

        /// <summary>
        ///     Codigo de error del SDK.
        /// </summary>
        public int CodigoErrorSdk { get; }

        /// <summary>
        ///     Mensaje de error del codigo de error del SDK.
        /// </summary>
        public string MensajeErrorSdk { get; } = string.Empty;

    }
}
