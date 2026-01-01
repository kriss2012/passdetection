import os
import pickle
import tensorflow as tf
from sklearn.model_selection import train_test_split
from data_utils import load_data, create_tokenizer, preprocess_input, MAX_LEN

# Paths
DATA_PATH = 'data/rockyou.txt'
MODEL_DIR = 'models'

# Ensure directories exist
os.makedirs(MODEL_DIR, exist_ok=True)

# 1. Prepare Data
print("--- Starting Data Prep ---")
# Adjust sample_size based on your RAM. 200k is good for a quick demo.
X_text, y = load_data(DATA_PATH, sample_size=200000)

# 2. Tokenization
print("--- Tokenizing ---")
tokenizer = create_tokenizer(X_text)
X = preprocess_input(tokenizer, X_text)
vocab_size = len(tokenizer.word_index) + 1

# Save Tokenizer for the App
with open(os.path.join(MODEL_DIR, 'tokenizer.pickle'), 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. Build Model (Character-Level LSTM)
print("--- Building Model ---")
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 32, input_length=MAX_LEN),
    tf.keras.layers.Conv1D(64, 5, activation='relu'), # CNN layer to catch patterns like "12345"
    tf.keras.layers.MaxPooling1D(pool_size=4),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(1, activation='sigmoid') # Output: 0-1 probability
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# 4. Train
print("--- Training (This may take a few minutes) ---")
model.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_test, y_test))

# 5. Save Model
model.save(os.path.join(MODEL_DIR, 'model.h5'))
print(f"Success! Model saved to {MODEL_DIR}/model.h5")