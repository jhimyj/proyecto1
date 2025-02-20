import boto3
import os
import logging
import json
import jwt
import requests
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
connections_table = os.environ['CONNECTIONS_TABLE']
COGNITO_POOL_ID = os.environ['USER_POOL_ID']
COGNITO_REGION = os.environ.get('COGNITO_REGION', 'us-east-1')
COGNITO_APP_CLIENT_ID = os.environ['COGNITO_APP_CLIENT_ID']

def get_cognito_jwks():
    """
    Descarga las claves públicas (JWKS) de Cognito para verificar el token.
    """
    jwks_url = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_POOL_ID}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()


def verify_cognito_token(token):
    """
    Verifica el token JWT de Cognito y retorna el claim "sub".
    """
    # Eliminar el prefijo "Bearer " si existe
    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    # Obtener las claves públicas (JWKS)
    jwks = get_cognito_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get('kid')

    public_key = None
    for key in jwks['keys']:
        if key['kid'] == kid:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            break

    if public_key is None:
        raise Exception("No se encontró la clave pública adecuada en JWKS.")

    # Decodificar y verificar el token
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[unverified_header['alg']],
            audience=COGNITO_APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_POOL_ID}"
        )
        return payload['sub']
    except Exception as e:
        raise Exception(f"Verificación del token falló: {str(e)}")


def connect_handler(event, context):
    """
    Función para el evento de conexión del WebSocket.
    Verifica el token de Cognito, extrae el "sub" y almacena la conexión.
    """
    connection_id = event['requestContext']['connectionId']

    # Extraer el token de los headers (asegúrate de que se envíe en la conexión)
    headers = event.get('headers', {})
    token = headers.get('Authorization')
    if not token:
        logger.error("No se encontró el header Authorization en la conexión.")
        return {'statusCode': 401, 'body': 'Unauthorized'}

    try:
        user_sub = verify_cognito_token(token)
        logger.info(f"Usuario autenticado, sub: {user_sub}")
    except Exception as e:
        logger.error(f"Error al verificar token: {str(e)}")
        return {'statusCode': 401, 'body': 'Unauthorized'}

    # Guardar connectionId y sub (usuario) en DynamoDB
    table = dynamodb.Table(connections_table)
    table.put_item(Item={'user_id': user_sub,'connection_id': connection_id})
    return {'statusCode': 200, 'body': 'Connected'}


def disconnect_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    table = dynamodb.Table(connections_table)

    # Consulta el índice secundario ("Schema2Index") para obtener los items con connection_id igual al recibido
    response = table.query(
        IndexName='connection-user-index',  # Reemplaza con el nombre de tu GSI si es diferente
        KeyConditionExpression=Key('connection_id').eq(connection_id)
    )
    items = response.get('Items', [])

    # Itera por cada item y elimina el registro de la tabla principal usando la clave compuesta (user_id, connection_id)
    for item in items:
        table.delete_item(
            Key={
                'user_id': item['user_id'],
                'connection_id': item['connection_id']
            }
        )

    return {'statusCode': 200, 'body': 'Disconnected'}


def action_handler(event, context):
    message = event.get('body')
    logger.info(f"Mensaje recibido: {message}")
    return {'statusCode': 200, 'body': 'Action processed'}
