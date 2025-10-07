import os
import zipfile
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from gestionProveedores.models import Correo, ArchivoAdjunto
from gestionProveedores.process_emails import process_emails, EMAIL_HOST, EMAIL_USER, EMAIL_PASS
from imapclient import IMAPClient
import pyzmail

def descargar_archivo(request, correo_id, filename):
    process_emails()

    save_dir = os.path.join(settings.MEDIA_ROOT, 'facturas_electronicas')
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    # Si el archivo no existe, lo bajo del correo
    if not os.path.exists(file_path):
        correo = get_object_or_404(Correo, id=correo_id)

        with IMAPClient(EMAIL_HOST, ssl=True) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.select_folder('INBOX', readonly=True)

            raw_message = server.fetch([correo.uid], ['RFC822'])[correo.uid][b'RFC822']
            message = pyzmail.PyzMessage.factory(raw_message)

            for part in message.mailparts:
                if part.filename == filename:
                    payload = part.get_payload()
                    with open(file_path, 'wb') as f:
                        f.write(payload)
                    break

        if filename.lower().endswith('.zip') and os.path.exists(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(save_dir)

    if not os.path.exists(file_path):
        raise Http404("Archivo no encontrado.")

    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
