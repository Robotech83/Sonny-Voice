# Import necessary libraries
import datetime
import json
import openai
import os
import pyttsx3
import speech_recognition as sr
import time
import re
import random

# Set up the OpenAI API key using environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the pyttsx3 text-to-speech engine
engine = pyttsx3.init()

# Set the voice property for the speech engine
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Change index to select desired voice

# Maintain a conversation history for the assistant to reference in responses
conversation_history = [{"role": "system", "content": "You are a helpful and funny assistant."}]

# Define the memory file path where the assistant's memory will be saved
memory_file = "memory.json"

# Function to load stored memory from a file
def load_memory():
    """Load memory from the JSON file if it exists."""
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            return json.load(f)  # Load and return the memory data
    return {}  # Return an empty dictionary if no memory exists

# Function to save memory to a file
def save_memory(memory):
    """Save memory to a JSON file and reload it to ensure persistence."""
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=4)  # Write the memory to file with readable indentation
    print("Memory successfully saved.")

# Initialize the memory by loading from file
memory = load_memory()

# Function to get the current time in 12-hour format with AM/PM
def get_current_time():
    return datetime.datetime.now().strftime("%I:%M:%S %p")

# Function to get the current date in YYYY-MM-DD format
def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")

# Function to set a timer for the given duration in seconds
def set_timer(duration):
    print(f"Timer set for {duration} seconds.")
    speak(f"Timer set for {duration} seconds.")  
    time.sleep(duration)  
    print("Timer expired!")
    speak("Time's up!")  

# Function to make the assistant speak the given text
def speak(text):
    engine.say(text)  
    engine.runAndWait()  

# Function to parse the timer command and extract the duration in seconds
def parse_timer_command(command):
    words = command.split()  
    for i, word in enumerate(words):
        if word.isdigit():  
            return int(word)  
    return None  

# Function to remember a key-value pair (store in memory)
def remember(key, value):
    """Stores a key-value pair in memory."""
    key = key.lower()  # Normalize key to lowercase
    memory[key] = value  
    save_memory(memory)  
    print(f"Memory saved: {key} -> {value}")  
    speak(f"I'll remember that {key} is {value}.")  

# Function to recall a value by key from memory
def recall(key):
    """Retrieves a value from memory by key."""
    memory = load_memory()  # Reload latest memory
    return memory.get(key.lower(), None)  

# Function to generate a response from OpenAI's API based on user input
def generate_response(prompt):
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

# Function to parse the "remember" command
def parse_remember_command(command):
    """Parses a 'remember' command and extracts key-value pairs."""
    match = re.search(r"remember (.*?) is (.*)", command, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None

# Predefined list of jokes
jokes = [
    "Why don’t skeletons fight each other? Because they don’t have the guts!",
    "I told my wife she should embrace her mistakes. She gave me a hug.",
    "Why don’t eggs tell jokes? Because they might crack up!",
    "What do you call a fake noodle? An impasta!",
    "Parallel lines have so much in common. It’s a shame they’ll never meet."
]

# Function to tell a joke
def tell_joke():
    """Tells a joke either using OpenAI API or from a predefined list."""
    joke_prompt = "Tell me a short and funny joke."
    joke = generate_response(joke_prompt)  # Try to get a joke from OpenAI

    if not joke:  # If OpenAI fails, use a predefined joke
        joke = random.choice(jokes)

    print(f"Joke: {joke}")
    speak(joke)

# Main function to handle speech recognition and interaction with the assistant
def main():
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

                    # Check if the user asked for the current time
                    if "time" in text.lower():
                        current_time = get_current_time()  
                        print(f"The current time is: {current_time}")  
                        speak(f"The current time is {current_time}")  
                        continue
                    
                    # Check if the user asked for the current date
                    if "date" in text.lower() or "today's date" in text.lower():
                        current_date = get_current_date()  
                        print(f"Today's date is: {current_date}")  
                        speak(f"Today's date is {current_date}")  
                        continue

                    # Check if the user asked to set a timer
                    if "set a timer" in text.lower():
                        duration = parse_timer_command(text)  
                        if duration:
                            set_timer(duration)  
                        else:
                            speak("I didn't catch the timer duration. Please try again.")  
                        continue
                    
                    # Check for "remember" commands (store information in memory)
                    if "remember" in text.lower():
                        key, value = parse_remember_command(text)
                        if key and value:
                            remember(key, value)
                            continue
                        else:
                            speak("Please tell me what to remember in the format 'remember X is Y'.")
                        continue
                    
                    # Check for "recall" commands (retrieve stored memory)
                    if "what is" in text.lower() or "do you remember" in text.lower():
                        key = text.lower().replace("what is", "").replace("do you remember", "").strip()  
                        value = recall(key)  
                        if value:
                            speak(f"You told me that {key} is {value}.")  
                        else:
                            speak(f"I don't have a memory for {key}.")  
                        continue
                    
                    # Check if the user asks for a joke
                    if "tell me a joke" in text.lower() or "say something funny" in text.lower():
                        tell_joke()
                        continue

                    # Generate a response for any other user input
                    response = generate_response(text)  
                    if response:
                        print(f"Assistant says: {response}")  
                        speak(response)  
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")  
            except sr.UnknownValueError:
                print("Could not understand the audio.")  
            except Exception as e:
                print(f"An error occurred: {e}")  

# Start the main function when the script is executed
if __name__ == "__main__":
    main()
