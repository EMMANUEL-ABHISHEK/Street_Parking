import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','gif','.mp4'}
    TWILIO_ACCOUNT_SID = 'AC5cba72708abdd92ed2395f79bab00e60'
    TWILIO_AUTH_TOKEN = '4cbdbf2463fe2e26aa13af2af1c6832f'
    TWILIO_PHONE_NUMBER = '+12512903725'
    DYNAMIC_PRICING_BASE = 50  # Base price for parking
