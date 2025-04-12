from flask import Flask
from flask_cors import CORS
#from tracks.nessie import nessie_bp
from tracks.mock_transactions import mock_bp


app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can access it

# Register blueprint
# app.register_blueprint(nessie_bp, url_prefix='/api')
app.register_blueprint(mock_bp, url_prefix='/api') # account for the fake stuff


if __name__ == '__main__':
    app.run(port=3001, debug=True)
