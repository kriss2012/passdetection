import pandas as pd
import numpy as np
import random
import string
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Configuration
MAX_LEN = 30  # Max password length to analyze
VOCAB_SIZE = 1000  # Character vocabulary size

def load_data(filepath, sample_size=200000):
    """
    Loads weak passwords from rockyou.txt and generates an equal number
    of strong passwords.
    """
    # 1. Load Weak Passwords (Class 0)
    print("Loading weak passwords...")
    
    # FIX: We use 'sep' instead of 'delimiter'.
    # We set it to a dummy sequence "^^^^" that won't appear in the file.
    # This forces pandas to read the whole line as one column.
    read_opts = {
        "sep": "^^^^",         # <--- CHANGED from delimiter="\n"
        "header": None,
        "names": ["password"],
        "quoting": 3,          # CSV.QUOTE_NONE: Fixes error with passwords containing "
        "engine": "python",    # Required for multi-char separators
    }

    try:
        # Try default encoding (utf-8) and modern pandas error handling
        df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip", **read_opts)
    except (UnicodeDecodeError, TypeError, ValueError):
        # Fallback 1: Try Latin-1 (common for rockyou.txt)
        try:
            df = pd.read_csv(filepath, encoding="ISO-8859-1", on_bad_lines="skip", **read_opts)
        except TypeError:
            # Fallback 2: For older Pandas versions (<1.3.0) that don't support 'on_bad_lines'
            df = pd.read_csv(filepath, encoding="ISO-8859-1", error_bad_lines=False, **read_opts)

    # 2. Robust Sampling
    # Ensure we don't try to sample more lines than exist in the file
    real_sample_size = min(sample_size, len(df))
    print(f"Dataset loaded. Sampling {real_sample_size} passwords...")
    
    weak_passwords = df['password'].dropna().astype(str).sample(n=real_sample_size).tolist()
    
    # 3. Generate Strong Passwords (Class 1)
    print("Generating strong passwords...")
    strong_passwords = []
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    
    for _ in range(real_sample_size):
        # Create a random string length 10-20
        pwd_len = random.randint(10, 20)
        strong_passwords.append("".join(random.choice(chars) for _ in range(pwd_len)))

    # 4. Combine
    X_text = weak_passwords + strong_passwords
    y = [0] * len(weak_passwords) + [1] * len(strong_passwords)
    
    return X_text, np.array(y)

def create_tokenizer(texts):
    """Creates a character-level tokenizer"""
    tokenizer = Tokenizer(char_level=True, lower=False) # Case sensitive is important for passwords!
    tokenizer.fit_on_texts(texts)
    return tokenizer

def preprocess_input(tokenizer, texts):
    """Converts strings to padded number sequences"""
    sequences = tokenizer.texts_to_sequences(texts)
    data = pad_sequences(sequences, maxlen=MAX_LEN, padding='post')
    return data