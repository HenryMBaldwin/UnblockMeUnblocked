import json
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense

# Load JSON Data
filename = 'levels/training_data.json'
with open(filename, 'r') as f:
    data = json.load(f)

# Assume that each 'state' in your data is a flattened 6x6x6 tensor, and 'move' is [x1, y1, x2, y2]

# Prepare your input data (X) and target data (Y)
X = np.array([entry['state'] for entry in data])  # Should have shape (num_samples, 216) if flattened
Y = np.array([entry['move'] for entry in data])  # Should have shape (num_samples, 4)

# Reshape X to be in the shape (num_samples, 6, 6, 6) if it's flattened
X = X.reshape(-1, 6, 6, 6) 

# Split data into training and testing (and optionally, validation) sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Define the model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(6, 6, 6)),  # Adjust input_shape accordingly
    Flatten(),
    Dense(64, activation='relu'),
    Dense(4, activation='linear')  # Output layer with linear activation, 4 units for [x1, y1, x2, y2]
])

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
history = model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=10, batch_size=32)

# Evaluate the model
loss = model.evaluate(X_test, Y_test)
print('Test Loss:', loss)

# Save the model if needed
model.save('models/unblock_me_solver')
