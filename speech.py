import speech_recognition as sr
import pyaudio
import wave
import datetime
import sqlite3
import pyttsx3
import re

# Set up the database
conn = sqlite3.connect('speech_recognition.db')
c = conn.cursor()


# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS speech_recognition
             (id INTEGER PRIMARY KEY,
              date TEXT,
              time TEXT,
              speech TEXT)''')

# Set up the speech recognition
r = sr.Recognizer()
m = sr.Microphone()
text_speech = pyttsx3.init()


# Set up the audio file
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"


# Set up the audio stream
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


# Set up the audio file
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)

# Start recording
print("* recording")

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    wf.writeframes(data)

print("* done recording")

# Stop recording
stream.stop_stream()
stream.close()
p.terminate()
wf.close()

# Read the audio file
with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
    audio = r.record(source)


def text_divide(text):
    """
    Text divide using Python.
    """
    text = re.sub(r'([ .!?])', r'\1|', text)
    text = re.sub(r'\|\s*', '\n', text)
    return text


# Recognize the speech
try:
    print("You said: " + r.recognize_google(audio))
    speech = r.recognize_google(audio)
    text_speech.say(r.recognize_google(audio)+" Your work is in Process.....")
    text_speech.runAndWait()
except sr.UnknownValueError:
    print("Flutter Assistant could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Flutter Assistant service; {0}".format(e))


# Get the date and time
if "insert" in speech:
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    # Insert the data into the database
    c.execute("INSERT INTO speech_recognition (date, time, speech) VALUES (?, ?, ?)", (date, time, speech))
    conn.commit()
    text_speech.say(r.recognize_google(audio) + " Your work is Done.....")
    text_speech.runAndWait()


# Close the database
conn.close()
