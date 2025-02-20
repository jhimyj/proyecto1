import logging
import json
import os
from .service import generate_presigned_urls,verify_existence_in_bd

from .response import Response

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

BD_NAME = os.environ['SUMMARY_TABLE']
def handler_function(event, context):
    """
    Lambda para generar URLs prefirmadas para archivos en S3.
    """
    try:
        logger.info("Evento recibido: %s", event)
        sub_user = (
            event.get('requestContext', {})
            .get('authorizer', {})
            .get('claims', {})
            .get('sub')
        )
        if not sub_user:
            logger.error("El identificador del usuario (sub) no se encontró en los claims.")
            return Response(
                status_code=400,
                message="El identificador del usuario es obligatorio."
            ).to_dict()

        # Validar el cuerpo del evento
        body = event.get('body')
        if not body:
            logger.error("No se encontró el cuerpo de la solicitud.")
            return Response(
                status_code=400,
                message="El cuerpo de la solicitud es obligatorio."
            ).to_dict()

        if not isinstance(body, dict):
            body = json.loads(body)
        if not body:
            logger.error("No se encontró el cuerpo de la solicitud.")
            return Response(
                status_code=400,
                message="El cuerpo de la solicitud es obligatorio."
            ).to_dict()
        # Extraer parámetros del cuerpo
        operation = body.get('operation', '').strip()
        files = body.get('files', [])

        if not operation:
            logger.error("El parámetro 'operation' es obligatorio.")
            return Response(
                status_code=400,
                message="El parámetro 'operation' es obligatorio."
            ).to_dict()

        if not isinstance(files, list) or not files:
            logger.error("El parámetro 'files' debe ser una lista no vacía.")
            return Response(
                status_code=400,
                message="El parámetro 'files' debe ser una lista de archivos válida."
            ).to_dict()

        verify_existence = verify_existence_in_bd(bd_name=BD_NAME,user_id=sub_user,operation=operation)
        if verify_existence["status"] == "error" or not verify_existence["exists"]:
            if verify_existence["status"] == "error":
                return Response(status_code=500,
                                message="Ocurrio un error en el servido").to_dict()
            return Response(status_code=404, message="Operacion no encontrado.").to_dict()

        # Generar URLs prefirmadas
        directory=  f"{sub_user}/{operation}"

        try:
            list_urls = generate_presigned_urls(directory=directory, files=files)
            logger.info("URLs prefirmadas generadas correctamente.")
            return Response(
                status_code=200,
                body=list_urls
            ).to_dict()
        except Exception as e:
            logger.error(f"Error al generar las URLs prefirmadas: {e}", exc_info=True)
            return Response(
                status_code=500,
                message="Error al generar las URLs prefirmadas."
            ).to_dict()

    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return Response(
            status_code=500,
            message="Ocurrió un error interno del servidor."
        ).to_dict()



