import logging
import os
from src.common.response import Response
from .service import create_operacion

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Nombre de la tabla de DynamoDB u otra configuración de base de datos.
bd_name = os.getenv('BD_NAME')


def handler_function(event, context):
    """
    Función handler para crear una operación. Se espera que el evento incluya:
      - name: el nombre de la operación.
      - El identificador del usuario (sub) se obtiene desde los claims del Authorizer de Cognito.

    Devuelve una respuesta formateada utilizando el objeto Response.
    """
    try:
        # Validar que el cuerpo de la solicitud exista
        body = event.get('body')
        if not body:
            logger.error("No se encontró el cuerpo de la solicitud.")
            return Response(
                status_code=400,
                message="El cuerpo de la solicitud es obligatorio."
            ).to_dict()

        # Extraer el nombre de la operación y validar
        name_operation = body.get('name')
        if not name_operation:
            logger.error("El nombre de la operación es obligatorio.")
            return Response(
                status_code=400,
                message="El nombre de la operación es obligatorio."
            ).to_dict()

        # Extraer el identificador del usuario (sub) desde los claims del Authorizer
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

        # Crear la operación en la base de datos (DynamoDB, por ejemplo)
        service_create_response = create_operacion(name_operation, sub_user, bd_name)
        if service_create_response.get("status") != "success":
            error_message = service_create_response.get("message", "Error desconocido al crear la operación.")
            logger.error(f"Error al crear la operación: {error_message}")
            error = service_create_response.get("error", "Error desconocido al crear la operación.")
            return Response(
                status_code=500,
                message=error_message,
                body = {"error":error }
            ).to_dict()

        logger.info(service_create_response.get("message", "Operación creada."))
        # Respuesta exitosa
        return Response(
            status_code=200,
            body=service_create_response
        ).to_dict()

    except Exception as e:
        logger.error(f"Error inesperado en handler_function: {e}")
        return Response(
            status_code=500,
            message="Ocurrió un error interno del servidor.",
            body={"error": str(e)}
        ).to_dict()


# Ejemplo de uso para pruebas locales:
if __name__ == "__main__":
    test_event = {
        "body": {
            "name": "operation_abc"
        },
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "user123"
                }
            }
        },
        "Records": [{
            "s3": {
                "bucket": {"name": "mi-bucket-financiero"},
                "object": {"key": "doc1.docx"}
            }
        }]
    }
    response = handler_function(test_event, None)
    print(response)
