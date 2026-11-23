# apps/common/utils/credentials.py
import os

class CredentialsUtil:

    @staticmethod
    def get_odata_credentials():
        username = os.getenv("ODATA_USERNAME")
        password = os.getenv("ODATA_PASSWORD")

        if not username or not password:
            raise ValueError("Las credenciales OData no están configuradas")

        return {
            "username": username,
            "password": password
        }