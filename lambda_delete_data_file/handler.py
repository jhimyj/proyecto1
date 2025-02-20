import logging
import os
from .response import Response
from .service import delete_data_file_db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BD_NAME = os.environ['RESULT_TABLE']  # Cambiar en deploy

def handler_function(event, context):
    """
    Función handler para eliminar un archivo asociado a una operación.
    Se espera que el evento incluya:
      - operation: el nombre de la operación.
      - file: el nombre del archivo a eliminar.
      - El identificador del usuario (sub) se obtiene desde los claims del Authorizer de Cognito.

    Devuelve una respuesta formateada utilizando el objeto Response.
    """
    try:
        # Validar que el cuerpo de la solicitud exista
        parameters = event.get('queryStringParameters',{})
        if not parameters:
            logger.error("No se encontró los parametros de la solicitud.")
            return Response(
                status_code=400,
                message="Los parametros de la solicitud son obligatorios."
            ).to_dict()

        # Extraer el nombre de la operación y validarlo
        name_operation = parameters.get('operation')
        if not name_operation:
            logger.error("El nombre de la operación es obligatorio.")
            return Response(
                status_code=400,
                message="El nombre de la operación es obligatorio."
            ).to_dict()

        # Extraer el nombre del archivo a eliminar y validarlo
        file = parameters.get('file')
        if not file:
            logger.error("El nombre del file es obligatorio.")
            return Response(
                status_code=400,
                message="El nombre del file es obligatorio."
            ).to_dict()

        # Extraer el identificador del usuario (sub) desde los claims del Authorizer de Cognito
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

        # Formar la clave compuesta para la operación
        user_operation = f"{sub_user}#{name_operation}"

        # Llamar al servicio para eliminar el archivo de la base de datos
        response_service_bd = delete_data_file_db(
            db_name=BD_NAME,
            user_operation=user_operation,
            file=file
        )

        # Evaluar la respuesta del servicio
        if response_service_bd.get("status") == "success":
            logger.info("Archivo eliminado correctamente.")

            return Response(
                status_code=200,
                message="Archivo eliminado correctamente."
            ).to_dict()
        else:
            logger.error(f"Error al eliminar el archivo: {response_service_bd.get('message')}")
            return Response(
                status_code=400,
                message=response_service_bd.get("message"),
                body={"error":response_service_bd.get("error")}
            ).to_dict()

    except Exception as e:
        logger.error(f"Error inesperado en el handler: {e}")
        return Response(
            status_code=500,
            message="Error inesperado en el handler.",
            body={"error": str(e)}
        ).to_dict()



