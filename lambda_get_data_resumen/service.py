import boto3
import logging
from botocore.exceptions import ClientError
from decimal import Decimal
# Configuración básica del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_db_data(db_name: str, user_id: str, operation: str) -> dict:
    """
    Obtiene el valor de la columna 'data' de un elemento en DynamoDB.

    Parámetros:
      db_name (str): Nombre de la tabla de DynamoDB.
      user_id (str): Valor de la clave de partición.
      operation (str): Valor de la clave de ordenamiento.

    Retorna:
      dict: Diccionario con el resultado de la operación. Ejemplo:
            En caso de éxito:
              {
                  "status": "success",
                  "message": "Data encontrada exitosamente.",
                  "data": <valor_de_data>
              }
            En caso de que el elemento o la columna 'data' no existan:
              {
                  "status": "error",
                  "message": "Elemento no encontrado."  // o "Columna 'data' no existe en el elemento."
              }
            En caso de error:
              {
                  "status": "error",
                  "message": "Error al obtener la data.",
                  "error": <detalle_del_error>
              }
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(db_name)

    try:
        response = table.get_item(
            Key={
                'user_id': user_id,
                'operation': operation
            }
        )

        # Verifica si se encontró el elemento
        if 'Item' not in response:
            logger.warning("Elemento no encontrado.")
            return {
                "status": "error",
                "message": "Elemento no encontrado."
            }

        item = response['Item']

        # Verifica si el elemento contiene la columna 'data'
        if 'data' not in item:
            logger.warning("Columna 'data' no existe en el elemento.")
            return {
                "status": "error",
                "message": "Columna 'data' no existe en el elemento."
            }

        # Retorna el valor de la columna 'data'
        logger.info("Data encontrada exitosamente.")
        return {
            "status": "success",
            "message": "Data encontrada exitosamente.",
            "data": item['data']
        }

    except ClientError as e:
        logger.error(f"Error al obtener la data: {e}")
        return {
            "status": "error",
            "message": "Error al obtener la data.",
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error inesperado al obtener la data: {e}")
        return {
            "status": "error",
            "message": "Error inesperado al obtener la data.",
            "error": str(e)
        }


def convert_decimal(obj):
    """
    Función recursiva que convierte objetos Decimal a float,
    en listas y diccionarios.
    """
    if isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj