import unittest
import hashlib
from datetime import datetime, timedelta
from test_license_system import LicenseServer, app, db, License  # Import your main app code

class TestLicenseSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.secret_key = "TEST_SECRET_KEY"
        cls.license_server = LicenseServer(cls.secret_key)
        cls.app = app.test_client()  # Create a Flask test client

    def setUp(self):
        with app.app_context():
            db.create_all()  # Set up a test database

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database after each test

    def test_generate_license_key(self):
        product_id = "TEST_PRODUCT"
        license_type = "PRO"
        expiration_days = 30
        license_key, expiration_date = self.license_server.generate_license_key(product_id, license_type, expiration_days)

        self.assertTrue(len(license_key) > 0)
        self.assertIn('-', license_key)
        self.assertEqual(expiration_date, (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d'))

    def test_activate_license(self):
        product_id = "TEST_PRODUCT"
        license_type = "PRO"
        duration_days = 30
        license_key, _ = self.license_server.generate_license_key(product_id, license_type, duration_days)

        # Add the license to the database
        new_license = License(product_id=product_id, license_key=license_key, license_type=license_type)
        db.session.add(new_license)
        db.session.commit()

        # Activate the license
        device_id = "DEVICE12345"
        response = self.app.post('/api/license/activate', json={"license_key": license_key, "device_id": device_id})
        self.assertEqual(response.status_code, 200)

    def test_validate_license(self):
        product_id = "TEST_PRODUCT"
        license_type = "PRO"
        duration_days = 30
        license_key, _ = self.license_server.generate_license_key(product_id, license_type, duration_days)

        # Add and activate the license
        new_license = License(product_id=product_id, license_key=license_key, license_type=license_type, activated=True, device_id="DEVICE12345")
        db.session.add(new_license)
        db.session.commit()

        # Validate the license
        response = self.app.post('/api/license/validate', json={"license_key": license_key, "device_id": "DEVICE12345"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("License is valid", response.json["message"])

    def test_invalid_license(self):
        response = self.app.post('/api/license/validate', json={"license_key": "INVALID_KEY", "device_id": "DEVICE12345"})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
