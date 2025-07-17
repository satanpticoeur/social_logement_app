import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-tres-difficile-a-deviner'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PAYDUNYA_MASTER_KEY = os.environ.get('PAYDUNYA_MASTER_KEY')
    PAYDUNYA_PRIVATE_KEY = os.environ.get('PAYDUNYA_PRIVATE_KEY')
    PAYDUNYA_PUBLIC_KEY = os.environ.get('PAYDUNYA_PUBLIC_KEY')
    PAYDUNYA_TOKEN = os.environ.get('PAYDUNYA_TOKEN')

    # PAYDUNYA_BASE_URL = "https://app.paydunya.com/api/v1/checkout-invoice/create"
    # PAYDUNYA_CONFIRM_URL = "https://app.paydunya.com/api/v1/checkout-invoice/confirm/"
    # PAYDUNYA_VERIFY_URL = "https://app.paydunya.com/api/v1/checkout-invoice/verify/"

    # production keys:
    # PAYDUNYA_BASE_URL = "https://api.paydunya.com/v1/checkout-invoice/create"
    # PAYDUNYA_CONFIRM_URL = "https://api.paydunya.com/v1/checkout-invoice/confirm/"
    # PAYDUNYA_VERIFY_URL = "https://api.paydunya.com/v1/checkout-invoice/verify/"

    PAYDUNYA_CALLBACK_URL = os.environ.get('PAYDUNYA_CALLBACK_URL', 'https://ad4931843ff6.ngrok-free.app/api/locataire/paydunya/callback')
    PAYDUNYA_RETURN_URL = os.environ.get('PAYDUNYA_RETURN_URL', 'https://ad4931843ff6.ngrok-free.app/api/locataire/mes-paiements/success')
    PAYDUNYA_CANCEL_URL = os.environ.get('PAYDUNYA_CANCEL_URL', 'https://ad4931843ff6.ngrok-free.app/api/locataire/mes-paiements/cancel')

    # PAYDUNYA_MODE = 'test' # ou 'live'
