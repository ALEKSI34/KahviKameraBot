
import tensorflow as tf
from keras import backend as K
from keras.optimizers import Adam
from keras.applications.mobilenet_v3 import MobileNetV3Small, preprocess_input
import random
import pathlib
datadir = pathlib.Path("Imagepool").absolute()
images = len(list(datadir.glob("kahvia*")))
img_height = 224#180
img_width = 224#320
print(str(datadir))

num_classes = 2

if K.image_data_format() == 'channels_first':
  input_shape = (3, 224, 224)
else:
  input_shape = (224, 224, 3)

# model = tf.keras.models.Sequential([
#   tf.keras.layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
#   tf.keras.layers.Conv2D(16, 3, padding='same', activation='relu'),
#   tf.keras.layers.MaxPooling2D(),
#   tf.keras.layers.Conv2D(32, 3, padding='same', activation='relu'),
#   tf.keras.layers.MaxPooling2D(),
#   tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
#   tf.keras.layers.MaxPooling2D(),
#   tf.keras.layers.Flatten(),
#   tf.keras.layers.Dense(128, activation='relu'),
#   tf.keras.layers.Dense(num_classes)
# ])
use_mobilenet = True
if not use_mobilenet:
  model = tf.keras.models.Sequential()

  model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=input_shape))
  model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu'))
  model.add(tf.keras.layers.MaxPooling2D((2, 2)))

  model.add(tf.keras.layers.Conv2D(128, (3, 3), activation='relu'))
  model.add(tf.keras.layers.Conv2D(128, (3, 3), activation='relu'))
  model.add(tf.keras.layers.MaxPooling2D((2, 2)))

  model.add(tf.keras.layers.Conv2D(256, (3, 3), activation='relu'))
  model.add(tf.keras.layers.Conv2D(256, (3, 3), activation='relu'))
  model.add(tf.keras.layers.MaxPooling2D((2, 2)))

  model.add(tf.keras.layers.Flatten())

  #Increasing the number of neurons in the Dense layer
  model.add(tf.keras.layers.Dense(512, activation='relu'))
  model.add(tf.keras.layers.Dropout(0.5))
  model.add(tf.keras.layers.Dropout(0.5))

  #Adding batch normalization layers
  model.add(tf.keras.layers.BatchNormalization())
  model.add(tf.keras.layers.BatchNormalization())
  model.add(tf.keras.layers.BatchNormalization())

  #Final output layer
  model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

  optimizer = Adam(lr=0.01)
  model.compile(optimizer=optimizer,loss="binary_crossentropy", metrics=["accuracy"])
else:
  model = MobileNetV3Small(weights="imagenet", include_top=False, input_shape=(224,224,3))
  x = model.output
  x = tf.keras.layers.GlobalAveragePooling2D()(x)
  predictions = tf.keras.layers.Dense(1, activation='sigmoid')(x)
  model = tf.keras.models.Model(inputs=model.input, outputs=predictions)
  model.compile(optimizer="adam",loss="binary_crossentropy", metrics=["accuracy"])

epochs = 10  # Number of times the entire training dataset is passed through the neural network
batch_size = 32  # Number of samples that will be propagated through the network at once
max_loop = 20

random.seed(123)

class_weights = {0: 0.25,1: 0.7}

for itera in range(1,max_loop+1): # Vaihdellaan datasettiä aina välillä :D
  print(f"Swapping dataset... Loop {itera} of {max_loop}")
  random_seed = random.randint(0,100)
  train_ds = tf.keras.utils.image_dataset_from_directory(datadir, seed=random_seed,validation_split=0.8, subset="training",image_size=(224,224))
  val_ds = tf.keras.utils.image_dataset_from_directory(datadir, seed=random_seed+1,validation_split=0.2,subset="validation",image_size=(224,224))

  train_images, train_labels = next(iter(train_ds))
  val_images, val_labels = next(iter(val_ds))

  history = model.fit(
    train_images, train_labels,
    epochs=epochs,
    batch_size=batch_size,
    class_weight=class_weights,
    validation_data=(val_images, val_labels)
  )

predictions = model.predict(tf.keras.utils.image_dataset_from_directory(datadir, image_size=(224,224)))
print(str(tf.nn.softmax(predictions[0])))

# Load the data and create the model
data = tf.keras.utils.image_dataset_from_directory(datadir)

# Evaluate the model on the data
accuracy = model.evaluate(data)[1]

# Print the accuracy
print("Accuracy:", accuracy)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('kahviAI.tflite', 'wb') as f:
    f.write(tflite_model)