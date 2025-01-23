import logging
from service import generate_presigned_urls
from response import Response

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler_generate_urls(event, context):
    """
    Lambda para generar URLs prefirmadas para archivos en S3.
    """
    try:
        logger.info("Evento recibido: %s", event)

        # Validar el cuerpo del evento
        body = event.get('body')
        if not body:
            logger.error("No se encontró el cuerpo de la solicitud.")
            return Response(
                status_code=400,
                message="El cuerpo de la solicitud es obligatorio."
            ).to_dict()

        # Extraer parámetros del cuerpo
        directory = body.get('directory', '').strip()
        files = body.get('files', [])

        if not directory:
            logger.error("El parámetro 'directory' es obligatorio.")
            return Response(
                status_code=400,
                message="El parámetro 'directory' es obligatorio."
            ).to_dict()

        if not isinstance(files, list) or not files:
            logger.error("El parámetro 'files' debe ser una lista no vacía.")
            return Response(
                status_code=400,
                message="El parámetro 'files' debe ser una lista de archivos válida."
            ).to_dict()

        # Generar URLs prefirmadas
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
