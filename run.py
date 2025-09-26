from src.main.server import create_app

# Criamos a instância da aplicação chamando a nossa factory
app = create_app()

if __name__ == '__main__':
    # O modo de debug nunca deve ser usado em produção!
    app.run(debug=True, host='0.0.0.0', port=5000)