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
    public struct tCteProv
    {
        // Código del Cliente / Proveedor.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoCliente;

        // Razón social.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cRazonSocial;

        // Fecha de alta.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string cFechaAlta;

        // RFC.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongRFC)]
        public string cRFC;

        // CURP.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCURP)]
        public string cCURP;

        // Denominación comercial.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDenComercial)]
        public string cDenComercial;
        
        // Representante legal.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongRepLegal)]
        public string cRepLegal;
        
        // Nombre de la moneda.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongNombre)]
        public string cNombreMoneda;
        
        // Lista de precios.
        public int cListaPreciosCliente;
        
        // Descuento.
        public double cDescuentoMovto;
        
        // Bandera de venta a crédito. 0 – No se permite, 1 – Se permite.
        public int cBanVentaCredito;
        
        // Código del valor de clasificación 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionCliente1;
        
        // Código del valor de clasificación 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionCliente2;
        
        // Código del valor de clasificación 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionCliente3;
        
        // Código del valor de clasificación 4.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionCliente4;
        
        // Código del valor de clasificación 5.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionCliente5;
        
        // Código del valor de clasificación 6.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionCliente6;
        
        // Tipo de cliente. 1. Cliente, 2. Cliente/Proveedor, 3. Proveedor.
        public int cTipoCliente;
        
        // Estado: 0 – Inactivo, 1 – Activo.
        public int cEstatus;
        
        // Fecha de baja.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string cFechaBaja;
        
        // Fecha de última revisión.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongFecha)]
        public string cFechaUltimaRevision;
        
        // Limite de crédito.
        public double cLimiteCreditoCliente;

        // Días de crédito del cliente.
        public int cDiasCreditoCliente;
        
        // Bandera de exceder crédito. 0 – No se permite, 1 – Se permite.
        public int cBanExcederCredito;
        
        // Descuento por pronto pago.
        public double cDescuentoProntoPago;
        
        // Días para pronto pago.
        public int cDiasProntoPago;
        
        // Interes moratorio.
        public double cInteresMoratorio;
        
        // Día de pago.
        public int cDiaPago;
        
        // Días de revisión.
        public int cDiasRevision;
        
        // Mensajeria.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDesCorta)]
        public string cMensajeria;
        
        // Cuenta de mensajeria.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongDescripcion)]
        public string cCuentaMensajeria;
        
        // Dias de embarque del cliente.
        public int cDiasEmbarqueCliente;
        
        // Código del almacén.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoAlmacen;
        
        // Código del agente de venta.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoAgenteVenta;
        
        // Código del agente de cobro.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodigo)]
        public string cCodigoAgenteCobro;
        
        // Restricción de agente.
        public int cRestriccionAgente;
        
        // Impuesto 1.
        public double cImpuesto1;
        
        // Impuesto 2.
        public double cImpuesto2;
        
        // Impuesto 3.
        public double cImpuesto3;
        
        // Retención al cliente 1.
        public double cRetencionCliente1;
        
        // Retención al cliente 2.
        public double cRetencionCliente2;
        
        // Código del valor de clasificación 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionProveedor1;
        
        // Código del valor de clasificación 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionProveedor2;
        
        // Código del valor de clasificación 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionProveedor3;
        
        // Código del valor de clasificación 4.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionProveedor4;
        
        // Código del valor de clasificación 5.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionProveedor5;
        
        // Código del valor de clasificación 6.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongCodValorClasif)]
        public string cCodigoValorClasificacionProveedor6;
        
        // Limite de credito del proveedor.
        public double cLimiteCreditoProveedor;
        
        // Días de credito del proveedor.
        public int cDiasCreditoProveedor;
        
        // Tiempo de entrega.
        public int cTiempoEntrega;
        
        // Días de embarque.
        public int cDiasEmbarqueProveedor;
        
        // Impuesto proveedor 1.
        public double cImpuestoProveedor1;
        
        // Impuesto proveedor 2.
        public double cImpuestoProveedor2;
        
        // Impuesto proveedor 3.
        public double cImpuestoProveedor3;
        
        // Retención proveedor 1.
        public double cRetencionProveedor1;
        
        // Retención proveedor 2.
        public double cRetencionProveedor2;
        
        // Bandera de cálculo de interes moratorio. 0 – No se calculan, 1 – Si se calculan.
        public int cBanInteresMoratorio;
        
        // Texto extra 1.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTextoExtra)]
        public string cTextoExtra1;
        
        // Texto extra 2.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTextoExtra)]
        public string cTextoExtra2;
        
        // Texto extra 3.
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = SdkConstantes.kLongTextoExtra)]
        public string cTextoExtra3;
        
        // Importe extra 1.
        public double cImporteExtra1;
        
        // Importe extra 2.
        public double cImporteExtra2;

        //Importe extra 3.
        public double cImporteExtra3;
        
        // Importe extra 4.
        public double cImporteExtra4;

    }
}
