from keras.models import load_model
from PIL import Image
from keras_preprocessing.image import load_img, img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions
from keras.applications.vgg16 import VGG16
import numpy as np

from keras.models import load_model

model = load_model('model_saved.h5')

image = load_img('coffee_archive/train/1.jpeg', target_size=(224, 224))
#TODO testaa millä kuvan koolla saisi pelkästään pannut näkymään. Varmaan ois nopeempi runaamaan sitten
#image.show()

img = np.array(image)
img = img / 255.0
img = img.reshape(1, 224, 224, 3)
label = model.predict(img)
print("(0 - Ei kahvia , 1- Kahvia): ", label[0][0])