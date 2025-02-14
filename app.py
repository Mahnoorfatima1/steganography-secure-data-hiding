from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from PIL import Image
import wave
import os
import hashlib
import cv2
import numpy as np
from typing import Optional

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'wav', 'mp4'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def encrypt_message(message: str, password: str) -> bytes:
    key = hashlib.sha256(password.encode()).digest()
    encrypted = bytearray()
    for i, c in enumerate(message.encode()):
        encrypted.append(c ^ key[i % len(key)])
    return bytes(encrypted)

def decrypt_message(encrypted: bytes, password: str) -> Optional[str]:
    try:
        key = hashlib.sha256(password.encode()).digest()
        decrypted = bytearray()
        for i, c in enumerate(encrypted):
            decrypted.append(c ^ key[i % len(key)])
        return decrypted.decode()
    except:
        return None

def encode_image(filename: str, data: bytes):
    img = Image.open(filename)
    
    # Convert image to RGB mode if it's not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    width, height = img.size
    pixels = list(img.getdata())

    # Convert data to bits
    bits = ''.join([format(b, '08b') for b in data])

    if len(bits) > len(pixels) * 3:  # 3 channels (RGB)
        raise ValueError("Data too large for this image")

    # Modify least significant bits
    new_pixels = []
    bit_idx = 0

    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3):  # RGB channels
            if bit_idx < len(bits):
                new_pixel[i] = (new_pixel[i] & ~1) | int(bits[bit_idx])
                bit_idx += 1
        new_pixels.append(tuple(new_pixel))

    # Save modified image as PNG (lossless format)
    new_img = Image.new('RGB', img.size)
    new_img.putdata(new_pixels)
    return new_img
def decode_image(filename: str) -> bytes:
    img = Image.open(filename)
    
    # Convert image to RGB mode if it's not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    pixels = list(img.getdata())

    # Extract bits from least significant bits
    bits = ''
    for pixel in pixels:
        for i in range(3):  # RGB channels
            bits += str(pixel[i] & 1)

    # Convert bits to bytes
    bytes_data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) == 8:
            bytes_data.append(int(byte, 2))

    return bytes(bytes_data)
def encode_audio(filename: str, data: bytes):
    with wave.open(filename, 'rb') as wav:
        # Store audio parameters
        params = wav.getparams()
        frames = bytearray(wav.readframes(wav.getnframes()))

        # Convert data to bits
        bits = ''.join([format(b, '08b') for b in data])

        if len(bits) > len(frames):
            raise ValueError("Data too large for this audio file")

        # Modify least significant bits
        for i in range(len(bits)):
            frames[i] = (frames[i] & ~1) | int(bits[i])

        # Save modified audio
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], "encoded_" + os.path.basename(filename))
        with wave.open(output_path, 'wb') as new_wav:
            new_wav.setparams(params)  # Use stored parameters
            new_wav.writeframes(frames)

        return output_path

def decode_audio(filename: str) -> bytes:
    with wave.open(filename, 'rb') as wav:
        frames = bytearray(wav.readframes(wav.getnframes()))

        # Extract bits from least significant bits
        bits = ''.join([str(frame & 1) for frame in frames])

        # Convert bits to bytes
        bytes_data = bytearray()
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            if len(byte) == 8:
                bytes_data.append(int(byte, 2))

        return bytes(bytes_data)
def encode_video(filename: str, data: bytes):
    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Convert data to bits
    bits = ''.join([format(b, '08b') for b in data])
    bit_idx = 0

    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Modify the first frame only
        if bit_idx < len(bits):
            # Ensure we handle RGB and RGBA separately
            for i in range(height):
               for j in range(width):
                 for k in range(3):  # RGB channels (or 4 if RGBA)
                   if bit_idx < len(bits):
                      pixel_value = frame[i, j, k]
                      new_pixel_value = (pixel_value & ~1) | int(bits[bit_idx])
                # Ensure the pixel value is within the valid range for uint8
                      frame[i, j, k] = np.uint8(max(0, min(255, new_pixel_value)))
                      bit_idx += 1


        frames.append(frame)

    cap.release()

    # Save the modified video
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + os.path.basename(filename))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames:
        out.write(frame)
    out.release()

    return output_path



def decode_video(filename: str) -> bytes:
    cap = cv2.VideoCapture(filename)
    if not cap.isOpened():
        raise ValueError("Could not open video file")

    # Read the first frame only
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Could not read video frame")

    height, width = frame.shape[:2]
    bits = ''

    # Extract bits from the least significant bits
    for i in range(height):
        for j in range(width):
            for k in range(3):  # RGB channels
                bits += str(frame[i, j, k] & 1)

    # Convert bits to bytes
    bytes_data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) == 8:
            bytes_data.append(int(byte, 2))

    cap.release()
    return bytes(bytes_data)
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/index')
def main():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']
        message = request.form['message']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                encrypted = encrypt_message(message, password)
                data_length = len(encrypted).to_bytes(4, 'big')
                data_to_hide = data_length + encrypted

                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext in ['.png', '.jpg', '.jpeg']:
                    new_img = encode_image(filepath, data_to_hide)
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + os.path.splitext(filename)[0] + '.png')
                    new_img.save(output_path, format='PNG')  # Save as PNG
                    return send_file(output_path, as_attachment=True)

                elif file_ext == '.wav':
                    output_path = encode_audio(filepath, data_to_hide)
                    return send_file(output_path, as_attachment=True)

                elif file_ext == '.mp4':
                    output_path = encode_video(filepath, data_to_hide)
                    return send_file(output_path, as_attachment=True)

            except Exception as e:
                flash(f"Encoding failed: {str(e)}")
                return redirect(url_for('encode'))

        else:
            flash("Invalid file type")
            return redirect(url_for('encode'))

    return render_template('encode.html')
@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext in ['.png', '.jpg', '.jpeg']:
                    encrypted = decode_image(filepath)
                elif file_ext == '.wav':
                    encrypted = decode_audio(filepath)
                elif file_ext == '.mp4':
                    encrypted = decode_video(filepath)

                # Debugging: Print encrypted data
                print("Encrypted data (raw):", encrypted)

                data_length = int.from_bytes(encrypted[:4], 'big')
                encrypted_data = encrypted[4:4 + data_length]

                # Debugging: Print data length and encrypted data
                print("Data length:", data_length)
                print("Encrypted data (extracted):", encrypted_data)

                message = decrypt_message(encrypted_data, password)

                # Debugging: Print decrypted message
                print("Decrypted message:", message)

                if message:
                    flash(f"Decoded message: {message}")
                else:
                    flash("Invalid password or no hidden message found")

            except Exception as e:
                flash(f"Decoding failed: {str(e)}")

            return redirect(url_for('decode'))

        else:
            flash("Invalid file type")
            return redirect(url_for('decode'))

    return render_template('decode.html')

if __name__ == '__main__':
    app.run(debug=True)