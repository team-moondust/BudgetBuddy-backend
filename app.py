from flask import Flask
from flask_cors import CORS
from routes.nessie import nessie_bp

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can access it

# Register blueprint
app.register_blueprint(nessie_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(port=3001, debug=True)
