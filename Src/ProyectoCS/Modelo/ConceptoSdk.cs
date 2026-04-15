using ContpaqiConnector.Extensiones;
using ContpaqiConnector.SDK;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ContpaqiConnector.Modelo
{
    public class ConceptoSdk
    {
        // Campo CCODIGOCONCEPTO - Código del concepto.
        public string Codigo { get; set; }

        // Campo CIDCONCEPTODOCUMENTO - Identificador del concepto de documento.
        public int Id { get; set; }

        // Campo CNOMBRECONCEPTO - Nombre del concepto.
        public string Nombre { get; set; }

        public static ConceptoSdk BuscarConceptoPorCodigo(string conceptoCodigo)
        {
            ComercialSdk.fBuscaConceptoDocto(conceptoCodigo).TirarSiEsError();

            return LeerDatosConcepto();
        }

        public static ConceptoSdk BuscarConceptoPorId(int conceptoId)
        {
            ComercialSdk.fBuscaIdConceptoDocto(conceptoId).TirarSiEsError();

            return LeerDatosConcepto();
        }

        private static ConceptoSdk LeerDatosConcepto()
        {
            var idBd = new StringBuilder(3000);
            var codigoBd = new StringBuilder(3000);
            var nombreBd = new StringBuilder(3000);

            ComercialSdk.fLeeDatoConceptoDocto("CIDCONCEPTODOCUMENTO", idBd, 3000);
            ComercialSdk.fLeeDatoConceptoDocto("CCODIGOCONCEPTO", codigoBd, 3000);
            ComercialSdk.fLeeDatoConceptoDocto("CNOMBRECONCEPTO", nombreBd, 3000);

            return new ConceptoSdk { Id = int.Parse(idBd.ToString()), Codigo = codigoBd.ToString(), Nombre = nombreBd.ToString() };
        }

    }
}
