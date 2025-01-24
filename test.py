import openai
import pyttsx3
import pyaudio
import wave

# Set up the OpenAI API key (use environment variables for security)
openai.api_key = ""

# Set up the speech synthesis engine
engine = pyttsx3.init()

def transcribe_audio_to_text_whisper(filename):
    try:
        with open(filename, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
            return response.get("text", "").strip()
    except Exception as e:
        print(f"Error transcribing audio with Whisper: {e}")
        return None

def generate_response(prompt):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=4000,
            n=1,
            stop=None,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def speak(text):
    engine.say(text)
    engine.runAndWait()

def record_audio(filename, duration=10):
    """Record audio from the microphone and save it to a file."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)

    print("Recording...")
    frames = []

    for _ in range(0, int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))

def main():
    activation_phrase = "hey sonny"
    print(f"Say '{activation_phrase}' to start speaking")

    while True:
        print("Listening for the activation phrase...")
        filename = "input.wav"

        # Record audio and process transcription
        record_audio(filename, duration=10)
        text = transcribe_audio_to_text_whisper(filename)

        if text and activation_phrase in text.lower():
            print("Activation phrase detected. Say your question.")
            record_audio(filename, duration=10)
            text = transcribe_audio_to_text_whisper(filename)

            if text:
                print(f"You said: {text}")
                response = generate_response(text)

                if response:
                    print(f"Sonny says: {response}")
                    speak(response)

if __name__ == "__main__":
    main()
