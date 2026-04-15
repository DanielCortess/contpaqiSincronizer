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
    public struct tDireccion
    {
        // Código cliente / proveedor.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodCteProv;

        // Tipo de catálogo.
        public int cTipoCatalogo;

        // Tipo de dirección.
        public int cTipoDireccion;
                
        // Calle.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cNombreCalle;
                
        // Número exterior.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNumeroExtInt)]
        public string cNumeroExterior;
        
        // Número interior.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNumeroExtInt)]
        public string cNumeroInterior;
        
        // Colonia.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cColonia;
        
        // Código postal.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigoPostal)]
        public string cCodigoPostal;
        
        // Telefono 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTelefono)]
        public string cTelefono1;
        
        // Telefono 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTelefono)]
        public string cTelefono2;
        
        // Telefono 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTelefono)]
        public string cTelefono3;
        
        // Telefono 4.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTelefono)]
        public string cTelefono4;
        
        // Correo electrónico.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongEmailWeb)]
        public string cEmail;
        
        // Página web.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongEmailWeb)]
        public string cDireccionWeb;
        
        // Ciudad
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cCiudad;

        //Estado.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cEstado;
                
        // País.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cPais;
                
        // Texto extra.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cTextoExtra;
    }
}
