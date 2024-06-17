import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
    TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
    TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'
    DYNAMIC_PRICING_BASE = 50  # Base price for parking
