from keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np

resnet_model = ResNet50(weights='imagenet')

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def analyze_image(file_path):
    try:
        img_array = preprocess_image(file_path)
        predictions = resnet_model.predict(img_array)
        decoded_predictions = decode_predictions(predictions)
        return decoded_predictions[0][0][1]
    except Exception as e:
        print(f"An unexpected error occurred during image analysis: {e}")
    return None
