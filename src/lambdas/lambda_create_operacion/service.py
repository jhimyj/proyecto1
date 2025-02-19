import boto3
import logging


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
    try:
        # Obtener el recurso DynamoDB y la tabla correspondiente
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(bd_name)

        # Insertar el item en la tabla
        response = table.put_item(
            Item={
                'user_id': user_id,
                'operation_name': operation_name,
                'status': 'created'
            }
        )
        logger.info("Operación creada exitosamente.")
        return {
            "status": "success",
            "message": "Operación creada exitosamente.",
            "data": response
        }
    except Exception as e:
        logger.error(f"Error al crear la operación: {e}")
        return {
            "status": "error",
            "message": "Error al crear la operación.",
            "error": str(e)
        }

# Ejemplo de uso:
if __name__ == '__main__':
    result = create_operacion("user123", "operation_abc", "mi_tabla_dynamodb")
    print(result)
