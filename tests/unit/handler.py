import json
from src.lambdas.lambda_generar_urls.handler import handler_generate_urls

# Tipos MIME permitidos
TIPOS_PERMITIDOS = {'image/png', 'image/jpeg', 'image/jpg', 'application/pdf'}


# Simula un evento de entrada con un body adecuado
test_event = {
    "body": {
        "directory": "mi-directorio",
        "files": [{"name":"iamgen_secreta_prima_de_alda","content_type":"image/jpeg"}]
    }
}

# Puedes usar None para el contexto si no lo requieres
test_context = None

if __name__ == "__main__":

    response = handler_generate_urls(test_event, test_context)
    print(json.dumps(response, indent=4, ensure_ascii=False))
