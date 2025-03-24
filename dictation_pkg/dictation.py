from dotenv import load_dotenv, set_key
from openai import OpenAI, OpenAIError, AuthenticationError, BadRequestError
import pyaudio
import wave
from playsound import playsound
import pyperclip
import os
import sys
import time

import dictation_pkg.hotkey

script_dir = os.path.dirname(os.path.realpath(__file__))

start_recording_sound = os.path.join(script_dir, "sounds", "25879__acclivity__drip1-2.wav")
start_transcription_sound = os.path.join(script_dir, "sounds", "506545__matrixxx__pop-02-2.wav")
completion_sound = os.path.join(script_dir, "sounds", "388046__paep3nguin__beep_up-2.wav")
error_sound = os.path.join(script_dir, "sounds", "38718__shimsewn__low-tone-with-ringmod-100-200.wav")

ENV_FILE = ".env"

# Ensure the .env file exists and load it
if not os.path.exists(ENV_FILE):
    with open(ENV_FILE, "w") as file:
        pass  # Create an empty .env file if it doesn't exist
load_dotenv(ENV_FILE)

def get_api_key():
    """Retrieve the API key from the .env file or environment variables."""
    return os.getenv("OPENAI_API_KEY")

def prompt_for_api_key(prompt):
    """Prompt the user to input the API key."""
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nGoodbye.")
        sys.exit(0)

def set_api_key(api_key):
    """Save the API key to the .env file programmatically."""
    set_key(ENV_FILE, "OPENAI_API_KEY", api_key)
    print("API key has been saved to the .env file.")

def get_valid_client(api_key):
    client = OpenAI(api_key=api_key)
    try:
        client.models.list()
    except AuthenticationError:
        return None
    else:
        return client

client = None
api_key = get_api_key()
if not api_key:
    api_key = prompt_for_api_key("No OPENAI_API_KEY environment variable found. This is expected if this is your first time running the Dictator, you will only need to provide your API key the first time you run the dictator.\nPlease enter your OpenAI API key (it usually starts with 'sk-'):\n")

while not client:
    client = get_valid_client(api_key=api_key)
    if not client:
        api_key = prompt_for_api_key(f"OPENAI_API_KEY='{api_key}' is invalid! Please provide a current valid API key (it usually starts with 'sk-'). You only need to provide this the first time you run the Dictator:\n")
        if api_key:
            # Save the validated OPENAI API key as an environment variable for future sessions
            set_api_key(api_key)


##########################
# 2. Audio Recording Setup (Desktop Mode - not used for the web version)
##########################
CHUNK = 1024           # Number of frames per buffer
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100           # Sample rate
TEMP_WAV = "temp_audio.wav"

p = pyaudio.PyAudio()

is_recording = False
frames = []      # To store audio data while recording
stream = None    # Will be our PyAudio stream object

def start_recording():
    """Start recording from the microphone."""
    global stream, frames, is_recording
    frames = []

    print("Recording started. Speak now...")
    playsound(start_recording_sound)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    is_recording = True


def stop_recording():
    """Stop recording and save the audio to a .wav file."""
    global stream, frames, is_recording
    print("Recording stopped. Processing...")
    is_recording = False

    if stream is not None:
        stream.stop_stream()
        stream.close()
        stream = None

    playsound(start_transcription_sound) # blocks. don't use a long sound here unless everything in converted to asyncio

    # Save recorded data as a WAV file
    wf = wave.open(TEMP_WAV, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def process_audio_with_whisper_and_gpt():
    """Send the recorded audio to Whisper for transcription, 
       then GPT-4o for cleaning, and finally copy to clipboard.
    """
    print("Transcribing audio with Whisper...")
    pyperclip.copy("TRANSCRIPTION_IN_PROGRESS")

    # Send audio to Whisper for transcription
    try:
        with open(TEMP_WAV, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            transcribed_text = transcription.text
    except BadRequestError:
        print('Audio recording too short to transcribe. Skipping it.')
        playsound(error_sound)
        return
    finally:
        if os.path.exists(TEMP_WAV):
            try:
                audio_file.close()
            except:
                pass
            os.remove(TEMP_WAV)

    print(f"Raw transcription:\n{transcribed_text}\n")

    # --- Send the transcribed text to GPT-4o for cleaning ---
    print("Sending transcription to GPT-4o for cleaning...")

    # Send transcription to GPT-4o for cleanup
    response = client.chat.completions.create(
        model="gpt-4o",  # Adjust to your GPT-4o deployment name if applicable
        messages=[
            {
                "role": "developer",
                "content": """The user will give you a transcription of a dictation.
You should write a summary of the meeting including key points and action items. 
When possible, action items should include action summary, owner, due date. 
Draft a response for all actions where a report or email needs to be written.
Provide the response in plain text without any markdown formatting (no ** characters)""",
            },
            {
                "role": "user",
                "content": (f"Dictation to clean up:\n\n{transcribed_text}"),
            },
        ],
    )

    cleaned_text = response.choices[0].message.content

    playsound(completion_sound)
    print("Transcription returned:", cleaned_text)
    return cleaned_text


def dictate():
    """Record a dictation until toggled off, then transcribes and cleans up the result."""
    global is_recording, frames, stream

    dictation_pkg.hotkey.hotkey_start()
    hotkey_prev = False  # Tracks the previous state of the hotkey

    while True:
        current_hotkey = dictation_pkg.hotkey.hotkey_pressed()
        # Check for a rising edge: hotkey is pressed now, but wasn't in the previous iteration.
        if current_hotkey and not hotkey_prev:
            if not is_recording:
                print("Starting recording...")
                start_recording()
            else:
                print("Stopping recording...")
                stop_recording()
                # Process the recorded audio: transcribe with Whisper and clean with GPT-4o
                cleaned_text = process_audio_with_whisper_and_gpt()
                pyperclip.copy(cleaned_text)
                print(f"Cleaned text (copied to clipboard):\n{cleaned_text}\n")
        hotkey_prev = current_hotkey

        if is_recording and stream is not None:
            data = stream.read(CHUNK)
            frames.append(data)
        time.sleep(0.05)  # Small delay to prevent high CPU usage


# New function for web interface – process an uploaded audio file
def transcribe_audio_file(audio_file):
    TEMP_WAV = "temp_uploaded.wav"
    # Save the uploaded audio file temporarily
    with open(TEMP_WAV, "wb") as f:
        f.write(audio_file.read())
    print("Transcribing audio with Whisper...")
    try:
        with open(TEMP_WAV, "rb") as af:
            transcription = client.audio.transcriptions.create(model="whisper-1", file=af)
            transcribed_text = transcription.text
    except Exception as e:
        print("Error during transcription:", e)
        return "Transcription failed."
    finally:
        if os.path.exists(TEMP_WAV):
            os.remove(TEMP_WAV)
    print("Sending transcription to GPT-4 for cleaning...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "developer",
                "content": (
                    "The user will give you a transcription of a dictation.\n"
                    "You should write a detailed summary of the meeting including key points and any action items.\n"
                    "For each action item, include the action summary, the owner, and the due date.\n"
                    "Also, draft a response (such as an email) for any actions where a report or email needs to be written.\n"
                    "Return the result as plain text without any markdown formatting."
                )
            },
            {
                "role": "user",
                "content": f"Dictation to clean up:\n\n{transcribed_text}"
            },
        ],
    )
    cleaned_text = response.choices[0].message.content
    return cleaned_text
