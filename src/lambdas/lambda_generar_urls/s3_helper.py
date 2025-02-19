import boto3
import os
import logging
from botocore.config import Config

# Configuración de logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajustar la configuración para S3 Transfer Acceleration
s3_config = Config(s3={'use_accelerate_endpoint': True})

# Inicialización de cliente S3 y variables de entorno
s3_client = boto3.client('s3', config=s3_config)
bucket_name = os.getenv('S3_BUCKET_NAME')

# Tipos MIME permitidos
TIPOS_PERMITIDOS = {'image/png', 'image/jpeg', 'image/jpg', 'application/pdf'}

def generate_presigned_url(file_name: str, content_type: str, expiration: int = 3600) -> str:
    """
    Genera una URL prefirmada para subir un archivo a S3 usando Transfer Acceleration.

    :param file_name: Nombre del archivo en S3.
    :param content_type: Tipo MIME del archivo.
    :param expiration: Tiempo de expiración en segundos (default: 3600).
    :return: URL prefirmada como string.
    :raises ValueError: Si el tipo MIME no está permitido o los parámetros son inválidos.
    :raises RuntimeError: Si ocurre un error al generar la URL prefirmada.
    """
    # Validación rápida de parámetros
    if not file_name or not isinstance(file_name, str):
        logger.error("El parámetro 'file_name' es obligatorio y debe ser una cadena.")
        raise ValueError("El nombre del archivo ('file_name') es obligatorio y debe ser una cadena.")

    if content_type not in TIPOS_PERMITIDOS:
        logger.warning(f"Tipo MIME no permitido: {content_type}")
        raise ValueError(f"Tipo MIME '{content_type}' no permitido. Tipos permitidos: {TIPOS_PERMITIDOS}")

    try:
        # Generar URL prefirmada usando S3 Transfer Acceleration
        logger.info(f"Generando URL prefirmada (acelerada) para '{file_name}' con tipo '{content_type}'.")
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_name,
                'ContentType': content_type,
            },
            ExpiresIn=expiration
        )
        logger.info(f"URL prefirmada generada exitosamente: {url}")
        return url

    except boto3.exceptions.Boto3Error as e:
        logger.error(f"Error al comunicarse con S3: {e}")
        raise RuntimeError("Error al generar la URL prefirmada, verifique los detalles del cliente S3.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise RuntimeError("Ocurrió un error inesperado al generar la URL prefirmada.")
