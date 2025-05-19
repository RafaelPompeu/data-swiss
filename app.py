from app import create_app
from flask import request

app = create_app()

@app.after_request
def add_header(response):
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
