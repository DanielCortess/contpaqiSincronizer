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
    public struct tSeriesCapas
    {
        // Unidades del movimiento.
        public double aUnidades;
        
        // Tipo de cambio del movimiento.
        public double aTipoCambio;
        
        // Series del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string aSeries;
        
        // Pedimento del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string aPedimento;
        
        // Agencia aduanal del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string aAgencia;
        
        // Fecha de pedimento del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string aFechaPedimento;
        
        // Número de lote del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string aNumeroLote;
        
        // Fecha de fabricación del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string aFechaFabricacion;
        
        // Fecha de Caducidad del movimiento.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string aFechaCaducidad;
    }
}
