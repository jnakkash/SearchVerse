from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import hashlib

# Initialize Flask App
app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///licenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'
db = SQLAlchemy(app)

# Database Model
class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(100), nullable=False)
    license_key = db.Column(db.String(255), unique=True, nullable=False)
    license_type = db.Column(db.String(50), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=True)
    activated = db.Column(db.Boolean, default=False)
    device_id = db.Column(db.String(255), nullable=True)

# License Server Class
class LicenseServer:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def generate_license_key(self, product_id, license_type, expiration_days):
        """
        Generate a license key based on product ID, license type, and expiration days.
        """
        expiration_date = (
            (datetime.utcnow() + timedelta(days=expiration_days)).strftime('%Y-%m-%d')
            if expiration_days else "NOEXP"
        )
        raw_data = f"{product_id}:{license_type}:{expiration_date}:{self.secret_key}"
        hashed_key = hashlib.sha256(raw_data.encode()).hexdigest()
        license_key = '-'.join([hashed_key[i:i+5] for i in range(0, len(hashed_key), 5)])
        return license_key, expiration_date

license_server = LicenseServer(app.config['SECRET_KEY'])

# API Endpoints
@app.route('/api/license', methods=['POST'])
def create_license():
    """
    API to create a new license key.
    """
    data = request.json
    product_id = data['product_id']
    license_type = data['license_type']
    expiration_days = data.get('expiration_days', None)

    license_key, expiration_date = license_server.generate_license_key(product_id, license_type, expiration_days)
    new_license = License(
        product_id=product_id,
        license_key=license_key,
        license_type=license_type,
        expiration_date=datetime.strptime(expiration_date, '%Y-%m-%d') if expiration_days else None
    )
    db.session.add(new_license)
    db.session.commit()
    return jsonify({
        "license_key": license_key,
        "expiration_date": expiration_date
    }), 201

@app.route('/api/license/activate', methods=['POST'])
def activate_license():
    """
    API to activate a license key for a specific device.
    """
    data = request.json
    license_key = data['license_key']
    device_id = data['device_id']

    license = License.query.filter_by(license_key=license_key).first()
    if not license:
        return jsonify({"error": "License key not found"}), 404

    if license.activated:
        return jsonify({"error": "License key already activated"}), 400

    license.activated = True
    license.device_id = device_id
    db.session.commit()
    return jsonify({"message": "License activated successfully"}), 200

@app.route('/api/license/validate', methods=['POST'])
def validate_license():
    """
    API to validate a license key for a specific device.
    """
    data = request.json
    license_key = data['license_key']
    device_id = data['device_id']

    license = License.query.filter_by(license_key=license_key, device_id=device_id).first()
    if not license:
        return jsonify({"error": "Invalid license key or device"}), 404

    if license.expiration_date and datetime.utcnow() > license.expiration_date:
        return jsonify({"error": "License key has expired"}), 403

    return jsonify({"message": "License is valid"}), 200

@app.route('/api/license/deactivate', methods=['POST'])
def deactivate_license():
    """
    API to deactivate a license key.
    """
    data = request.json
    license_key = data['license_key']

    license = License.query.filter_by(license_key=license_key).first()
    if not license:
        return jsonify({"error": "License key not found"}), 404

    license.activated = False
    license.device_id = None
    db.session.commit()
    return jsonify({"message": "License deactivated successfully"}), 200

@app.before_request
def before_request():
    pass

# Initialize the Database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

