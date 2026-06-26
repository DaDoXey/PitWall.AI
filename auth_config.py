import os

ENVIRONMENT = os.getenv("STREAMLIT_ENV", "dev")

AUTH_STRATEGY = {
    "dev": {
        "type": "mock",
        "mock_user": "test@example.com",
        "mock_name": "Demo Pilot",
    },
    "prod": {
        "type": "oauth",
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
    },
}


def get_auth_method():
    return AUTH_STRATEGY.get(ENVIRONMENT, AUTH_STRATEGY["dev"])


def is_oauth_configured() -> bool:
    """
    True solo se le credenziali Google OAuth sono presenti.
    Finché è False, il bottone "Accedi con Google" resta predisposto ma non attivo.
    """
    return bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"))
