import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_operacion(user_id: str, operation_name: str, bd_name: str) -> dict:
    """
    Crea una operación en DynamoDB con:
      - Clave de partición: user_id
      - Clave de ordenamiento: operation_name
      - Atributo 'status' establecido en "create"

    :param user_id: Identificador del usuario (clave de partición).
    :param operation_name: Nombre de la operación (clave de ordenamiento).
    :param bd_name: Nombre de la tabla de DynamoDB.
    :return: Diccionario con el resultado de la operación.
             En caso de éxito:
             {
                 "status": "success",
                 "message": "Operación creada exitosamente.",
                 "data": <respuesta_de_DynamoDB>
             }
             En caso de error:
             {
                 "status": "error",
                 "message": "Error al crear la operación.",
                 "error": <detalle_del_error>
             }
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(bd_name)

    try:
        response = table.put_item(
            Item={
                'user_id': user_id,
                'operation': operation_name,
                'version': 1,
                'status': 'create'
            },
            ConditionExpression='attribute_not_exists(operation)'
        )
        logger.info("Operación creada exitosamente.")
        return {
            "status": "success",
            "message": "Operación creada exitosamente.",
            "data": response
        }
    except ClientError as e:
        # Si la condición falla, el ítem ya existe
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            msg = "La operación ya existe."
            logger.error(msg)
            return {
                "status": "error",
                "message": msg,
                "error": str(e)
            }
        else:
            logger.error(f"Error al crear la operación: {e}")
            return {
                "status": "error",
                "message": "Error al crear la operación.",
                "error": str(e)
            }
    except Exception as e:
        logger.error(f"Error inesperado al crear la operación: {e}")
        return {
            "status": "error",
            "message": "Error al crear la operación.",
            "error": str(e)
        }



if __name__ == '__main__':
    result = create_operacion("user1233", "operation_abcdee", "mi_tabla_dynamodb")
    print(result)
