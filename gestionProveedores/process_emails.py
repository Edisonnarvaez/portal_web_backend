import os
import zipfile
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from imapclient import IMAPClient
import pyzmail
from lxml import etree
from django.conf import settings
from gestionProveedores.models.factura import Factura
from gestionProveedores.models import Correo, ArchivoAdjunto
from tercero.models import Terceros, Departamento, Municipio, TipoTercero, Pais
import traceback

EMAIL_HOST = 'imap.gmail.com'
EMAIL_USER = 'tics@redmedicronips.com.co'
EMAIL_PASS = 'oqca trws yeck ecev'

NAMESPACES = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1'
}


NAMESPACES = {
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1'
}


def process_emails():
    with IMAPClient(EMAIL_HOST, ssl=True) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.select_folder('INBOX', readonly=True)
        messages = server.search(['ALL'])

        for uid in messages:
            if Correo.objects.filter(uid=uid).exists():
                print(f"Correo con UID {uid} ya existe. Saltando...")
                continue

            raw = server.fetch([uid], ['RFC822'])[uid][b'RFC822']
            message = pyzmail.PyzMessage.factory(raw)

            subject = message.get_subject()
            from_email = message.get_addresses('from')[0][1]
            body = ""

            if message.text_part:
                body = message.text_part.get_payload().decode(message.text_part.charset or 'utf-8')
            elif message.html_part:
                body = message.html_part.get_payload().decode(message.html_part.charset or 'utf-8')

            correo_obj = Correo.objects.create(
                subject=subject,
                from_email=from_email,
                date_received=timezone.now(),
                raw_message=body,
                uid=uid
            )

            archivos_nombres = []

            for part in message.mailparts:
                filename = part.filename
                if not filename:
                    continue

                archivos_nombres.append(filename)
                payload = part.get_payload()
                save_dir = os.path.join(settings.MEDIA_ROOT, 'facturas_electronicas')
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, filename)

                if not os.path.exists(file_path):
                    with open(file_path, 'wb') as f:
                        f.write(payload)
                        if correo_obj and correo_obj.id:
                            ArchivoAdjunto.objects.create(
                            correo=correo_obj,
                            nombre_archivo=filename,
                            archivo=f'facturas_electronicas/{filename}'
                        )
                        else:
                         print(f"No se creó ArchivoAdjunto porque Correo es None o sin ID.")

                    print(f"Archivo {filename} guardado en {file_path}.")
                else:
                    print(f"Archivo {filename} ya existe. Saltando guardado.")

                if filename.lower().endswith('.zip'):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        for member in zip_ref.namelist():
                            extracted_path = os.path.join(save_dir, member)

                            if not os.path.exists(extracted_path):
                                zip_ref.extract(member, save_dir)
                                print(f"Archivo {member} extraído en {save_dir}.")
                            else:
                                print(f"Archivo {member} ya existe. Saltando extracción.")

                            if member.lower().endswith(".xml"):
                                data = process_xml(extracted_path)
                                print("DATA EXTRAIDA:", data)
                                if data:
                                    if data.get('tercero'):
                                        save_tercero(data['tercero'])
                                    save_factura(data, subject, from_email)
                                else:
                                    print(f"No se extrajo información de {member}")


                elif filename.lower().endswith('.xml'):
                    data = process_xml(file_path)
                    print("DATA EXTRAIDA:", data)
                    if data:
                         save_factura(data, subject, from_email)
                         if data.get('tercero'):
                            save_tercero(data['tercero'])
                    else:
                        print(f"No se extrajo información de {filename}")

            correo_obj.archivos = ", ".join(archivos_nombres)
            correo_obj.save()


def process_xml(file_path):
    try:
        tree = etree.parse(file_path)
        get = lambda xpath: tree.findtext(xpath, '', namespaces=NAMESPACES)

        razon_proveedor = get('.//cac:AccountingSupplierParty//cac:PartyName/cbc:Name')
        razon_adquiriente = get('.//cac:AccountingCustomerParty//cac:PartyName/cbc:Name')
        prefix = get('.//sts:AuthorizedInvoices/sts:Prefix')
        id_factura = get('.//cbc:ID')

        tipo_contribuyente = get('.//cac:AccountingSupplierParty/cbc:AdditionalAccountID')
        
        tipo_tercero = None
        if tipo_contribuyente == '1':
            tipo_tercero = 'Persona Jurídica'
        elif tipo_contribuyente == '2':
            tipo_tercero = 'Persona Natural'

        if id_factura and prefix and id_factura.startswith(prefix):
            num_autorizacion = f"{prefix}-{id_factura[len(prefix):]}"
        elif id_factura:
            num_autorizacion = id_factura
        else:
            num_autorizacion = get('.//cbc:UUID') or ''

        valor = get('.//cac:LegalMonetaryTotal/cbc:LineExtensionAmount')
        fecha_emision = get('.//cbc:IssueDate')

        print("RAZON PROVEEDOR:", razon_proveedor)
        print("RAZON ADQUIRIENTE:", razon_adquiriente)
        print("NUM AUTORIZACION:", num_autorizacion)
        print("VALOR:", valor)
        print("FECHA EMISION:", fecha_emision)

        fecha = None
        if fecha_emision:
            fecha = datetime.strptime(fecha_emision, '%Y-%m-%d').date()

        tercero_data = {
            'razon_social': razon_proveedor,
            'nit': get('.//cac:AccountingSupplierParty//cac:PartyLegalEntity/cbc:CompanyID'),
            'email': get('.//cac:AccountingSupplierParty//cac:Contact/cbc:ElectronicMail'),
            'telefono': get('.//cac:AccountingSupplierParty//cac:Contact/cbc:Telephone'),
            'direccion': get('.//cac:AccountingSupplierParty//cac:PhysicalLocation//cbc:Line'),
            'ciudad': get('.//cac:AccountingSupplierParty//cac:PhysicalLocation//cbc:CityName'),
            'departamento': get('.//cac:AccountingSupplierParty//cac:PhysicalLocation//cbc:CountrySubentity'),
            'pais': get('.//cac:AccountingSupplierParty//cac:PhysicalLocation//cac:Address//cac:Country/cbc:Name'),
            'tipo_tercero': tipo_tercero 
        }

        return {
            'factura_id_factura_electronica': num_autorizacion or '',
            'factura_numero_autorizacion': num_autorizacion or '',
            'factura_razon_social_proveedor': razon_proveedor or '',
            'factura_razon_social_adquiriente': razon_adquiriente or '',
            'factura_valor': float(valor) if valor else 0.0,
            'factura_fecha': fecha,
            'factura_concepto': '',
            'tercero': tercero_data
        }

    except Exception as e:
        print(f"Error procesando XML {file_path}: {e}")
        return None


@transaction.atomic
def save_factura(data, subject, from_email):
    try:
        Factura.objects.create(
            factura_id_factura_electronica=data.get('factura_id_factura_electronica', ''),
            factura_numero_autorizacion=data.get('factura_numero_autorizacion', ''),
            factura_razon_social_proveedor=data.get('factura_razon_social_proveedor', ''),
            factura_razon_social_adquiriente=data.get('factura_razon_social_adquiriente', ''),
            factura_valor=data.get('factura_valor', 0.0),
            factura_fecha=data.get('factura_fecha', timezone.now().date()),
            factura_concepto=data.get('factura_concepto') or f"Correo de {from_email} - Asunto: {subject}",
            factura_etapa="INGRESADO",
            factura_estado_factura_id=1
        )
        print("✅ Factura creada OK")
    except Exception:
        traceback.print_exc()
@transaction.atomic
@transaction.atomic
def save_tercero(data):
    try:
        if not data['nit']:
            print("Tercero sin NIT, no se crea.")
            return

        if Terceros.objects.filter(tercero_codigo=data['nit']).exists():
            print("Tercero ya existe, no se crea.")
            return

        departamento = Departamento.objects.filter(departamento_nombre__iexact=data.get('departamento', '')).first()
        municipio = Municipio.objects.filter(municipio_nombre__iexact=data.get('ciudad', '')).first()
        pais = Pais.objects.filter(pais_nombre__iexact=data.get('pais', '')).first()

        tipo_tercero = None
        if data.get('tipo_tercero'):
            tipo_tercero = TipoTercero.objects.filter(nombre__iexact=data['tipo_tercero']).first()
            print(f"🔍 Tipo de tercero encontrado: {tipo_tercero}")

        Terceros.objects.create(
            tercero_codigo=data['nit'],
            tercero_nombre_completo=data.get('razon_social', ''),
            tercero_razon_social=data.get('razon_social', ''),
            tercero_direccion=data.get('direccion', ''),
            tercero_telefono=data.get('telefono', ''),
            tercero_email=data.get('email', ''),
            tercero_pais=pais,
            tercero_departamento=departamento,
            tercero_municipio=municipio,
            tercero_proveedor=True,
            tercero_tipo=tipo_tercero,  
            tercero_estado=True,
        )
        print("✅ Tercero creado OK")

    except Exception as e:
        print(f"Error creando tercero: {e}")
