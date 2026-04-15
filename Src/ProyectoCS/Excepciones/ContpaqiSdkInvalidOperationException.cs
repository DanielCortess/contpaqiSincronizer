using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.Excepciones
{
    public class ContpaqiSdkInvalidOperationException : ContpaqiSdkException
    {
        public ContpaqiSdkInvalidOperationException() : base(0)
        {
        }

        public ContpaqiSdkInvalidOperationException(string message) : base(0, message)
        {
        }

        public ContpaqiSdkInvalidOperationException(string message, Exception innerException) : base(0, message, innerException)
        {
        }
    }
}
