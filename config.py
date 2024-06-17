import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    TWILIO_ACCOUNT_SID = 'AC723ff75eb26c998305921ba3386d4806'
    TWILIO_AUTH_TOKEN = '4ec7108c543ae4a211f584379b2e9bd8'
    TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'
    DYNAMIC_PRICING_BASE = 50  # Base price for parking
