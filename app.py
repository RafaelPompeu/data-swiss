from app import create_app

# Cria a instância do aplicativo usando a factory
app = create_app()

# Executa o servidor de desenvolvimento se o script for chamado diretamente
if __name__ == '__main__':
    # debug=True é útil para desenvolvimento, mas desative em produção
    # host='0.0.0.0' torna o servidor acessível na rede local
    app.run(debug=True, host='0.0.0.0')
