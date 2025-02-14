# Steganography Secure Data Hiding

A Flask-based web application for securely hiding and retrieving encrypted messages using steganography in images, audio, and video files. Supports PNG, JPG, WAV, and MP4 formats with least significant bit (LSB) encoding. Implements password-based encryption for added security.

## Features
- **Image Steganography:** Hide messages in PNG, JPG, and JPEG files.
- **Audio Steganography:** Encode messages in WAV audio files.
- **Video Steganography:** Conceal data within MP4 videos.
- **Password-Based Encryption:** Secure messages with a user-defined password.
- **User-Friendly Interface:** Upload files and retrieve hidden messages with ease.

## Technologies Used
- Python (Flask)
- OpenCV (cv2)
- Pillow (PIL)
- NumPy
- Wave
- HTML, CSS (Frontend)

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/steganography-secure-hiding.git
   cd steganography-secure-hiding
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   python app.py
   ```
5. Open a web browser and go to `http://127.0.0.1:5000/`

## Usage
### Encoding a Message
1. Navigate to the **Encode** section.
2. Upload an image, audio, or video file.
3. Enter your secret message and set a password.
4. Download the encoded file.

### Decoding a Message
1. Navigate to the **Decode** section.
2. Upload the encoded file.
3. Enter the password used during encoding.
4. Retrieve the hidden message.

## File Types Supported
- **Images:** PNG, JPG, JPEG
- **Audio:** WAV
- **Video:** MP4

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact
For inquiries, reach out to mahnoorfatimamf786@gmail.com

