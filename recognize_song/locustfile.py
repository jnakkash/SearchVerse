from locust import HttpUser, task, between
import random

class LicenseSystemUser(HttpUser):
    wait_time = between(1, 3)  # Simulates delay between user actions

    @task
    def activate_license(self):
        license_key = "TEST_LICENSE_KEY"
        device_id = f"DEVICE_{random.randint(1, 1000)}"
        self.client.post("/api/license/activate", json={"license_key": license_key, "device_id": device_id})

    @task
    def validate_license(self):
        license_key = "TEST_LICENSE_KEY"
        device_id = "DEVICE12345"
        self.client.post("/api/license/validate", json={"license_key": license_key, "device_id": device_id})
