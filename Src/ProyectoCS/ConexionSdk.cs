using ContpaqiConnector.Excepciones;
using ContpaqiConnector.Extensiones;
using ContpaqiConnector.SDK;
using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector
{
    public class ConexionSdk
    {
        // Abre la empresa de trabajo.
        // <param name="rutaEmpresa">Ruta del directorio de la empresa.</param>
        public static void AbrirEmpresa(string rutaEmpresa)
        {
            ComercialSdk.fAbreEmpresa(rutaEmpresa).TirarSiEsError();
        }

        // Busca el directorio donde se encuentra el SDK en el registro de Windows.
        // <param name="nombreLlaveRegistro">La llave del registro de Windows.</param>
        // <returns>La ruta del directorio donde se encuentra el SDK.</returns>
        private static string BuscarDirectorioDelSdk(string nombreLlaveRegistro)
        {
            // Buscar registro de windows
            RegistryKey registryKey = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry32);

            // Buscar la llave de CONTPAQi
            RegistryKey keySitema = registryKey.OpenSubKey(nombreLlaveRegistro, false);

            if (keySitema is null)
                // No se encontró la llave
                throw new ContpaqiSdkInvalidOperationException($"No se encontró la llave del registro {nombreLlaveRegistro}");

            // Leer el valor del campo DIRECTORIOBASE donde se encuentra la ruta del SDK
            object directorioBaseKey = keySitema.GetValue(LlavesRegistroWindowsSdk.NombreCampoRutaSdk);

            if (directorioBaseKey is null)
            {
                throw new ContpaqiSdkInvalidOperationException(
                    $"No se encontró el valor del campo {LlavesRegistroWindowsSdk.NombreCampoRutaSdk} del registro {nombreLlaveRegistro}");
            }

            return directorioBaseKey.ToString();
        }

        // Cierra la empresa de trabajo.
        public static void CerrarEmpresa()
        {
            ComercialSdk.fCierraEmpresa();
        }

        // Establece el directorio de trabajo en el directorio donde se encuentra el SDK.
        private static void EstablecerElDirectorioDeTrabajo()
        {
            // Buscar el directorio donde se encuentra el SDK
            string rutaSdk = BuscarDirectorioDelSdk(LlavesRegistroWindowsSdk.Comercial);

            // Establecer el directorio de trabajo en el directorio donde se encuentra el SDK
            Directory.SetCurrentDirectory(rutaSdk);
        }

        // Inicia la conexión con el sistema y muestra una ventana de autenticación donde el usuario podrá ingresar su nombre
        // de usuario y contraseña.
        public static void IniciarSdk()
        {
            // Establecer el directorio de trabajo en el directorio donde se encuentra el SDK
            EstablecerElDirectorioDeTrabajo();

            // Iniciar conexión
            ComercialSdk.fSetNombrePAQ(NombresPaqSdk.Comercial).TirarSiEsError();
        }

        // Inicia la conexión con el sistema e ingresa el usuario y contraseña programáticamente para que no se muestre la
        // ventana de autenticación de Comercial.
        // <param name="nombreUsuario">Nombre de usuario del sistema de Comercial.</param>
        // <param name="contrasena">Contraseña del sistema de Comercial.</param>
        public static void IniciarSdk(string nombreUsuario, string contrasena)
        {
            // Establecer el directorio de trabajo en el directorio donde se encuentra el SDK
            EstablecerElDirectorioDeTrabajo();

            // Ingresar programáticamente el usuario y contraseña del sistema de Comercial
            ComercialSdk.fInicioSesionSDK(nombreUsuario, contrasena);

            // Iniciar conexión
            ComercialSdk.fSetNombrePAQ(NombresPaqSdk.Comercial).TirarSiEsError();
        }

        // Inicia la conexión con el sistema e ingresa el usuario y contraseña programáticamente para que no se muestre la
        // ventana de autenticación de Comercial y Contabilidad.
        // <param name="nombreUsuarioComercial">Nombre de usuario del sistema de Comercial.</param>
        // <param name="contrasenaComercial">Contraseña del sistema de Comercial.</param>
        // <param name="nombreUsuarioContabilidad">Nombre de usuario del sistema de Contabilidad.</param>
        // <param name="contrasenaContabilidad">Contraseña del sistema de Contabilidad.</param>
        public static void IniciarSdk(string nombreUsuarioComercial, string contrasenaComercial, string nombreUsuarioContabilidad,
            string contrasenaContabilidad)
        {
            // Iniciar conexión con el sistema
            IniciarSdk(nombreUsuarioComercial, contrasenaComercial);

            // Ingresar programáticamente el usuario y contraseña del sistema de Contabilidad
            ComercialSdk.fInicioSesionSDKCONTPAQi(nombreUsuarioContabilidad, contrasenaContabilidad);
        }

        // Termina la conexión con el sistema y libera recursos.
        public static void TerminarSdk()
        {
            ComercialSdk.fTerminaSDK();
        }
    }
}
