from app import create_app
from flask import request

# Cria a instância do aplicativo usando a factory
app = create_app()

# Adiciona controle de cache para arquivos estáticos
@app.after_request
def add_header(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

# Executa o servidor de desenvolvimento se o script for chamado diretamente
if __name__ == '__main__':
    # debug=True é útil para desenvolvimento, mas desative em produção
    # host='0.0.0.0' torna o servidor acessível na rede local
    app.run(debug=True, host='0.0.0.0')
