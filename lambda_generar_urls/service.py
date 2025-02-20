import logging
import boto3
from .s3_helper import generate_presigned_url

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


def verify_existence_in_bd(bd_name: str, user_id: str, operation: str) -> dict:
    """
    Verifica la existencia de un elemento en la tabla DynamoDB usando 'user_id' y 'operation' como clave primaria.

    Parámetros:
      bd_name (str): Nombre de la tabla en DynamoDB.
      user_id (str): Valor del identificador de usuario (clave de partición).
      operation (str): Valor de la operación (clave de ordenamiento).

    Retorna:
      dict: Diccionario con la información del resultado. Por ejemplo:
            {"exists": True, "item": { ... }} si se encontró el elemento,
            {"exists": False} si no existe,
            {"success": False, "error": "mensaje de error"} en caso de excepción.
    """
    # Inicializa el recurso de DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(bd_name)

    try:
        # Intenta obtener el elemento usando las claves especificadas
        response = table.get_item(
            Key={
                'user_id': user_id,
                'operation': operation
            }
        )
    except Exception as e:
        # En caso de error, se retorna el mensaje de error
        return {"status":"error", "error": str(e)}

    # Verifica si el elemento existe en la respuesta
    if 'Item' in response:
        return {"status":"success","exists": True, "item": response["Item"]}
    else:
        return {"status":"success","exists": False}

