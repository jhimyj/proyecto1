import logging
from s3_helper import generate_presigned_url

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_presigned_urls(directory: str, files: list, expiration: int = 3600) -> list:
    """
    Genera múltiples URLs prefirmadas y las asocia con sus nombres de archivo.
    """
    if not files or not isinstance(files, list):
        raise ValueError("El parámetro 'files' debe ser una lista de archivos no vacía.")

    structured_urls = []

    for file in files:
        try:
            file_name = file.get('name')
            content_type = file.get('content_type')

            if not file_name or not content_type:
                raise ValueError(f"Datos del archivo inválidos: {file}")

            # Generar URL prefirmada
            full_path = f"{directory}/{file_name}"
            url = generate_presigned_url(full_path, content_type, expiration)

            # Agregar a la lista estructurada
            structured_urls.append({
                "name": file_name,
                "url": url
            })

        except Exception as e:
            logger.error(f"Error al procesar el archivo {file}: {e}")
            raise

    return structured_urls
