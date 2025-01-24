import datetime
import json
import openai
import os
import pyttsx3
import speech_recognition as sr
import time

# Set up the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set voice property
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Change index to select desired voice

# Maintain conversation history
conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]

# Memory file path
memory_file = "memory.json"

# Load memory from file
def load_memory():
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            return json.load(f)
    return {}

# Save memory to file
def save_memory(memory):
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=4)

# Initialize memory
memory = load_memory()

def get_current_time():
    """Returns the current time in 12-hour format with AM/PM."""
    current_time = datetime.datetime.now()
    return current_time.strftime("%I:%M:%S %p")

def get_current_date():
    """Returns the current date in YYYY-MM-DD format."""
    current_date = datetime.datetime.now()
    return current_date.strftime("%Y-%m-%d")

def set_timer(duration):
    """Sets a timer for the given duration in seconds."""
    print(f"Timer set for {duration} seconds.")
    speak(f"Timer set for {duration} seconds.")
    time.sleep(duration)
    print("Timer expired!")
    speak("Time's up!")

def transcribe_audio_to_text(filename):
    """Transcribes audio from a file to text."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError as e:
            print(f"Google Speech Recognition error: {e}")
        return None

def generate_response(prompt):
    """Generates a response from OpenAI."""
    global conversation_history
    conversation_history.append({"role": "user", "content": prompt})
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation_history,
            max_tokens=4000,
            temperature=0.5
        )
        assistant_reply = response.choices[0].message['content'].strip()
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

def speak(text):
    """Speaks the given text using the text-to-speech engine."""
    engine.say(text)
    engine.runAndWait()

def parse_timer_command(command):
    """Parses the duration from a timer command (e.g., 'Set a timer for 5 seconds')."""
    words = command.split()
    for i, word in enumerate(words):
        if word.isdigit():  # Check for numeric values in the command
            return int(word)
    return None

def remember(key, value):
    """Stores a key-value pair in memory."""
    memory[key] = value
    save_memory(memory)
    speak(f"I'll remember that {key} is {value}.")

def recall(key):
    """Retrieves a value from memory by key."""
    return memory.get(key, None)

def main():
    """Main function to handle speech recognition and assistant interaction."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                text = recognizer.recognize_google(audio)
                if text:
                    print(f"You said: {text}")
                    
                    # Check for time request
                    if "time" in text.lower():
                        current_time = get_current_time()
                        print(f"The current time is: {current_time}")
                        speak(f"The current time is {current_time}")
                        continue
                    
                    # Check for date request
                    if "date" in text.lower() or "today's date" in text.lower():
                        current_date = get_current_date()
                        print(f"Today's date is: {current_date}")
                        speak(f"Today's date is {current_date}")
                        continue

                    # Check for timer request
                    if "set a timer" in text.lower():
                        duration = parse_timer_command(text)
                        if duration:
                            set_timer(duration)
                        else:
                            speak("I didn't catch the timer duration. Please try again.")
                        continue
                    
                    # Check for "remember" commands
                    if "remember" in text.lower():
                        parts = text.split("remember")
                        if len(parts) > 1:
                            key_value = parts[1].strip().split(" is ")
                            if len(key_value) == 2:
                                remember(key_value[0].strip(), key_value[1].strip())
                                continue
                            else:
                                speak("Please tell me what to remember in the format 'remember X is Y'.")
                        continue
                    
                    # Check for "recall" commands
                    if "what is" in text.lower() or "do you remember" in text.lower():
                        key = text.lower().replace("what is", "").replace("do you remember", "").strip()
                        value = recall(key)
                        if value:
                            speak(f"You told me that {key} is {value}.")
                        else:
                            speak(f"I don't have a memory for {key}.")
                        continue
                    
                    # Generate response for other inputs
                    response = generate_response(text)
                    if response:
                        print(f"Sonny says: {response}")
                        speak(response)
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")
            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
