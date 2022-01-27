"""
Requirements:
    pip install tensorflow
"""
import tensorflow as tf
from tensorflow.keras import datasets, layers, models


def main():
    (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()

    import torch
    output = torch.nn.functional.interpolate(torch.Tensor(train_images), size=(50000, 128, 128, 3), mode='nearest')

    # Normalize pixel values to be between 0 and 1
    train_images, test_images = train_images / 255.0, test_images / 255.0

    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))

    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(10))

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    history = model.fit(train_images, train_labels, epochs=1000,
                        validation_data=(test_images, test_labels))

    test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/debug/tensorflow_training_example.py
    """
    main()
