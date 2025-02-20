import json
import logging
import os
from .response import Response
from .service import get_db_data,convert_decimal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BD_NAME = os.environ['RESULT_TABLE']#cambiae en deploy


def handler_function(event, context):
    """
    Función handler para obtener la columna 'data' de una operación.
    Se espera que el evento incluya:
      - operacion: el nombre de la operación.
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

        user_operation = f"{sub_user}#{name_operation}"
        # Consultar la columna 'data' utilizando la función get_db_data
        response_service_bd = get_db_data(db_name=BD_NAME, user_operation=user_operation, file=file)

        # Evaluar la respuesta de get_db_data y retornar la respuesta formateada
        if response_service_bd.get("status") == "success":
            logger.info("Data encontrada exitosamente.")
            data_converted = convert_decimal(response_service_bd.get("data"))
            return Response(
                status_code=200,
                body=data_converted
            ).to_dict()
        else:
            # Puede ser que la operación no exista o que la columna 'data' no se encuentre en el registro
            logger.info(f"No se pudo obtener la data: {response_service_bd.get('message')}")
            return Response(
                status_code=404,
                message=response_service_bd.get("message")
            ).to_dict()

    except Exception as e:
        logger.error(f"Error inesperado en el handler: {e}")
        return Response(
            status_code=500,
            message="Error inesperado en el handler.",
            body={"error":str(e)}
        ).to_dict()



if __name__ == "__main__":
    # test_event = {
    #     "body": {
    #         "operation": "operacion1",
    #         "file":"E_UTEC.pdf"
    #     },
    #     "requestContext": {
    #         "authorizer": {
    #             "claims": {
    #                 "sub": "usuario1"
    #             }
    #         }
    #     },
    #     "Records": [{
    #         "s3": {
    #             "bucket": {"name": "mi-bucket-financiero"},
    #             "object": {"key": "doc1.docx"}
    #         }
    #     }]
    # }
    # response = handler_function(test_event, None)
    # print(response)

    print(json.loads(None))

