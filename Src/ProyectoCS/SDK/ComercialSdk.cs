using ContpaqiConnector.DatosAbstractos;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.SDK
{
    public class ComercialSdk
    {
        // Inicio
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool SetCurrentDirectory(string lpPathName);

        [DllImport("MGWServicios.dll", EntryPoint = "fSetNombrePAQ")]
        public static extern int fSetNombrePAQ(string aSistema);

        [DllImport("MGWServicios.dll", EntryPoint = "fAbreEmpresa")]
        public static extern int fAbreEmpresa(string aDirectorioEmpresa);

        [DllImport("MGWServicios.dll", EntryPoint = "fCierraEmpresa")]
        public static extern void fCierraEmpresa();

        [DllImport("MGWServicios.dll", EntryPoint = "fTerminaSDK")]
        public static extern void fTerminaSDK();

        [DllImport("MGWServicios.dll", EntryPoint = "fError")]
        public static extern void fError(int aNumError, StringBuilder aMensaje, int aLen);

        [DllImport("MGWServicios.dll", EntryPoint = "fInicioSesionSDK")]
        public static extern void fInicioSesionSDK(string aUsuario, string aContrasenia);

        [DllImport("MGWServicios.dll", EntryPoint = "fInicioSesionSDKCONTPAQi")]
        public static extern void fInicioSesionSDKCONTPAQi(string aUsuario, string aContrasenia);

        // Empresa

        [DllImport("MGWServicios.dll", EntryPoint = "fPosPrimerEmpresa")]
        public static extern int fPosPrimerEmpresa(ref int aIdEmpresa, StringBuilder aNombreEmpresa, StringBuilder aDirectorioEmpresa);

        [DllImport("MGWServicios.dll", EntryPoint = "fPosSiguienteEmpresa")]
        public static extern int fPosSiguienteEmpresa(ref int aIdEmpresa, StringBuilder aNombreEmpresa, StringBuilder aDirectorioEmpresa);

        // Cliente / Proveedor
        [DllImport("MGWServicios.dll", EntryPoint = "fBuscaCteProv")]
        public static extern int fBuscaCteProv(string aCodCteProv);

        [DllImport("MGWServicios.dll", EntryPoint = "fEditaCteProv")]
        public static extern int fEditaCteProv();

        [DllImport("MGWServicios.dll", EntryPoint = "fSetDatoCteProv")]
        public static extern int fSetDatoCteProv(string aCampo, string aValor);

        [DllImport("MGWServicios.dll", EntryPoint = "fGuardaCteProv")]
        public static extern int fGuardaCteProv();

        [DllImport("MGWServicios.dll", EntryPoint = "fBuscaIdCteProv")]
        public static extern int fBuscaIdCteProv(int aIdCteProv);

        [DllImport("MGWServicios.dll", EntryPoint = "fPosPrimerCteProv")]
        public static extern int fPosPrimerCteProv();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosSiguienteCteProv")]
        public static extern int fPosSiguienteCteProv();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosEOFCteProv")]
        public static extern int fPosEOFCteProv();

        [DllImport("MGWServicios.dll", EntryPoint = "fAltaCteProv")]
        public static extern int fAltaCteProv(ref int aIdCteProv, ref tCteProv astCteProv);

        [DllImport("MGWServicios.dll", EntryPoint = "fBorraCteProv")]
        public static extern int fBorraCteProv();

        [DllImport("MGWServicios.dll", EntryPoint = "fLeeDatoCteProv")]
        public static extern int fLeeDatoCteProv(string aCampo, StringBuilder aValor, int aLen);

        // Productos
        [DllImport("MGWServicios.dll", EntryPoint = "fBuscaProducto")]
        public static extern int fBuscaProducto(string aCodProducto);

        [DllImport("MGWServicios.dll", EntryPoint = "fEditaProducto")]
        public static extern int fEditaProducto();

        [DllImport("MGWServicios.dll", EntryPoint = "fSetDatoProducto")]
        public static extern int fSetDatoProducto(string aCampo, string aValor);

        [DllImport("MGWServicios.dll", EntryPoint = "fGuardaProducto")]
        public static extern int fGuardaProducto();

        [DllImport("MGWServicios.dll", EntryPoint = "fBuscaIdProducto")]
        public static extern int fBuscaIdProducto(int aIdProducto);

        [DllImport("MGWServicios.dll", EntryPoint = "fPosPrimerProducto")]
        public static extern int fPosPrimerProducto();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosSiguienteProducto")]
        public static extern int fPosSiguienteProducto();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosEOFProducto")]
        public static extern int fPosEOFProducto();

        [DllImport("MGWServicios.dll", EntryPoint = "fAltaProducto")]
        public static extern int fAltaProducto(ref int aIdProducto, ref tProducto astProducto);

        [DllImport("MGWServicios.dll", EntryPoint = "fBorraProducto")]
        public static extern int fBorraProducto();

        [DllImport("MGWServicios.dll", EntryPoint = "fLeeDatoProducto")]
        public static extern int fLeeDatoProducto(string aCampo, StringBuilder aValor, int aLen);

        // Concepto
        [DllImport("MGWServicios.dll", EntryPoint = "fBuscaConceptoDocto")]
        public static extern int fBuscaConceptoDocto(string aCodConcepto);

        [DllImport("MGWServicios.dll", EntryPoint = "fBuscaIdConceptoDocto")]
        public static extern int fBuscaIdConceptoDocto(int aIdConcepto);

        [DllImport("MGWServicios.dll", EntryPoint = "fLeeDatoConceptoDocto")]
        public static extern int fLeeDatoConceptoDocto(string aCampo, StringBuilder aValor, int aLen);

        // Documentos
        [DllImport("MGWServicios.dll", EntryPoint = "fBuscarIdDocumento")]
        public static extern int fBuscarIdDocumento(int aIdDocumento);

        [DllImport("MGWServicios.dll", EntryPoint = "fEditarDocumento")]
        public static extern int fEditarDocumento();

        [DllImport("MGWServicios.dll", EntryPoint = "fSetDatoDocumento")]
        public static extern int fSetDatoDocumento(string aCampo, string aValor);

        [DllImport("MGWServicios.dll", EntryPoint = "fGuardaDocumento")]
        public static extern int fGuardaDocumento();

        [DllImport("MGWServicios.dll", EntryPoint = "fGetDatosCFDI")]
        public static extern int fGetDatosCFDI(StringBuilder aSerieCertEmisor, StringBuilder aFolioFiscalUUID, StringBuilder aSerieCertSAT,
            StringBuilder aFechaHora, StringBuilder aSelloDigCFDI, StringBuilder aSelloSAAT, StringBuilder aCadOrigComplSAT,
            StringBuilder aRegimen, StringBuilder aLugarExpedicion, StringBuilder aMoneda, StringBuilder aFolioFiscalOrig,
            StringBuilder aSerieFolioFiscalOrig, StringBuilder aFechaFolioFiscalOrig, StringBuilder aMontoFolioFiscalOrig);

        [DllImport("MGWServicios.dll", EntryPoint = "fBuscarDocumento")]
        public static extern int fBuscarDocumento(string aCodConcepto, string aSerie, string aFolio);

        [DllImport("MGWServicios.dll", EntryPoint = "fCancelaFiltroDocumento")]
        public static extern int fCancelaFiltroDocumento();

        [DllImport("MGWServicios.dll", EntryPoint = "fSetFiltroDocumento")]
        public static extern int fSetFiltroDocumento(string aFechaInicio, string aFechaFin, string aCodigoConcepto, string aCodigoCteProv);

        [DllImport("MGWServicios.dll", EntryPoint = "fPosPrimerDocumento")]
        public static extern int fPosPrimerDocumento();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosSiguienteDocumento")]
        public static extern int fPosSiguienteDocumento();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosEOF")]
        public static extern int fPosEOF();

        [DllImport("MGWServicios.dll", EntryPoint = "fSiguienteFolio")]
        public static extern int fSiguienteFolio(string aCodigoConcepto, StringBuilder aSerie, ref double aFolio);

        [DllImport("MGWServicios.dll", EntryPoint = "fCancelaDoctoInfo")]
        public static extern int fCancelaDoctoInfo(string aPass);

        [DllImport("MGWServicios.dll", EntryPoint = "fCancelaDocumentoConMotivo")]
        public static extern int fCancelaDocumentoConMotivo(string aMotivoCancelacion, string aUUIDRemplaza);

        [DllImport("MGWServicios.dll", EntryPoint = "fAltaDocumento")]
        public static extern int fAltaDocumento(ref int aIdDocumento, ref tDocumento aDocumento);

        [DllImport("MGWServicios.dll", EntryPoint = "fAltaDocumentoCargoAbono")]
        public static extern int fAltaDocumentoCargoAbono(ref tDocumento aDocumento);

        [DllImport("MGWServicios.dll", EntryPoint = "fLeeDatoDocumento")]
        public static extern int fLeeDatoDocumento(string aCampo, StringBuilder aValor, int aLongitud);

        [DllImport("MGWServicios.dll", EntryPoint = "fBorraDocumento")]
        public static extern int fBorraDocumento();

        [DllImport("MGWServicios.dll", EntryPoint = "fEntregEnDiscoXML")]
        public static extern int fEntregEnDiscoXML(string aCodConcepto, string aSerie, double aFolio, int aFormato, string aFormatoAmig);

        [DllImport("MGWServicios.dll", EntryPoint = "fSaldarDocumento")]
        public static extern int fSaldarDocumento(ref tLlaveDoc aDoctoaPagar, ref tLlaveDoc aDoctoPago, double aImporte, int aIdMoneda,
            string aFecha);

        [DllImport("MGWServicios.dll", EntryPoint = "fEmitirDocumento")]
        public static extern int fEmitirDocumento([MarshalAs(UnmanagedType.LPStr)] string aCodConcepto,
            [MarshalAs(UnmanagedType.LPStr)] string aSerie, double aFolio, [MarshalAs(UnmanagedType.LPStr)] string aPassword,
            [MarshalAs(UnmanagedType.LPStr)] string aArchivoAdicional);

        // Movimiento 

        [DllImport("MGWServicios.dll", EntryPoint = "fBuscarIdMovimiento")]
        public static extern int fBuscarIdMovimiento(int aIdMovimiento);

        [DllImport("MGWServicios.dll", EntryPoint = "fEditarMovimiento")]
        public static extern int fEditarMovimiento();

        [DllImport("MGWServicios.dll", EntryPoint = "fSetDatoMovimiento")]
        public static extern int fSetDatoMovimiento(string aCampo, string aValor);

        [DllImport("MGWServicios.dll", EntryPoint = "fGuardaMovimiento")]
        public static extern int fGuardaMovimiento();

        [DllImport("MGWServicios.dll", EntryPoint = "fCancelaFiltroMovimiento")]
        public static extern int fCancelaFiltroMovimiento();

        [DllImport("MGWServicios.dll", EntryPoint = "fSetFiltroMovimiento")]
        public static extern int fSetFiltroMovimiento(int aIdDocumento);

        [DllImport("MGWServicios.dll", EntryPoint = "fPosPrimerMovimiento")]
        public static extern int fPosPrimerMovimiento();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosSiguienteMovimiento")]
        public static extern int fPosSiguienteMovimiento();

        [DllImport("MGWServicios.dll", EntryPoint = "fPosMovimientoEOF")]
        public static extern int fPosMovimientoEOF();

        [DllImport("MGWServicios.dll", EntryPoint = "fAltaMovimiento")]
        public static extern int fAltaMovimiento(int aIdDocumento, ref int aIdMovimiento, ref tMovimiento astMovimiento);

        [DllImport("MGWServicios.dll", EntryPoint = "fBorraMovimiento")]
        public static extern int fBorraMovimiento(int aIdDocumento, int aIdMovimiento);

        [DllImport("MGWServicios.dll", EntryPoint = "fLeeDatoMovimiento")]
        public static extern int fLeeDatoMovimiento(string aCampo, StringBuilder aValor, int aLen);



    }

}
