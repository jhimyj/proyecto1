import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def delete_data_file_db(db_name: str, user_operation: str, file: str) -> dict:
    """
    Elimina un archivo asociado a una operación de usuario en DynamoDB.

    Parámetros:
      db_name (str): Nombre de la tabla en DynamoDB.
      user_operation (str): Valor de la clave de partición que identifica la operación de usuario.
      file (str): Valor de la clave de ordenamiento que identifica el archivo a eliminar.

    Retorna:
      dict: Diccionario con el resultado de la operación. Ejemplo:
            {
                "status": "success",
                "message": "Archivo eliminado correctamente.",
                "data": <respuesta_de_DynamoDB>
            }
            o, en caso de error:
            {
                "status": "error",
                "message": "Error al eliminar el archivo.",
                "error": <detalle_del_error>
            }
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(db_name)

    try:
        response = table.delete_item(
            Key={
                'user#operation': user_operation,
                'file': file
            },
            ReturnValues='ALL_OLD'
        )
        logger.info("Archivo eliminado correctamente.")
        return {
            "status": "success",
            "message": "Archivo eliminado correctamente.",
            "data": response
        }
    except ClientError as e:
        logger.error(f"Error al eliminar el archivo: {e}")
        return {
            "status": "error",
            "message": "Error al eliminar el archivo.",
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error inesperado al eliminar el archivo: {e}")
        return {
            "status": "error",
            "message": "Error inesperado al eliminar el archivo.",
            "error": str(e)
        }

