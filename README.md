# Sonny-Voice

This script implements a voice assistant that integrates OpenAI's GPT-4, text-to-speech (TTS), speech recognition, and memory functionality. Below are the key features and steps to understand the functionality of the script.

Features

1)Speech Recognition:

  Converts speech into text using speech_recognition.

  Handles real-time voice input via the microphone.

2)Text-to-Speech (TTS):

  Converts the assistant's responses into speech using pyttsx3.

3)OpenAI Integration:

  Leverages GPT-4 to generate intelligent and contextual responses.

  Maintains a conversation history for better interactions.

4)Memory Management:

  Stores key-value pairs persistently in a memory.json file.

  Can remember and recall information on request.

5)Utility Functions:

  Fetches current time and date.

  Sets timers based on voice commands.

6)Command Parsing:

  Recognizes specific commands like:

    "What is the time?"

    "Set a timer for X seconds."

    "Remember X is Y."

    "What is X?"

How It Works

1. Environment Setup

Dependencies:
  Install the required Python libraries using:

  pip install openai pyttsx3 SpeechRecognition

API Key:
  Set your OpenAI API key as an environment variable:

  export OPENAI_API_KEY='your_api_key_here'

2. Main Components

  Text-to-Speech (TTS)

  Initializes the TTS engine and sets the desired voice.

  Converts text into speech using:

    engine.say(text)
    engine.runAndWait()

  Speech Recognition

  Uses speech_recognition to capture and transcribe audio input from the microphone.

  Handles audio timeouts and errors gracefully.

  OpenAI GPT Integration

  Maintains a conversation history for better responses:

    conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]

Generates a response using:

    openai.ChatCompletion.create(
      model="gpt-4",
      messages=conversation_history,
      max_tokens=4000,
      temperature=0.5
)

Memory Management

  Stores and retrieves key-value pairs in a JSON file:

  Save Memory:

    with open("memory.json", "w") as f:
      json.dump(memory, f, indent=4)

Load Memory:

    if os.path.exists("memory.json"):
      with open("memory.json", "r") as f:
        memory = json.load(f)

3. Commands and Functions

Command                           Functionality

"What time is it?"          -->      Fetches and speaks the current time.

"What is today's date?"     -->      Fetches and speaks the current date.

"Set a timer for X seconds."   -->   Sets a countdown timer.

"Remember X is Y."         -->       Saves key-value pairs in memory.

"What is X?"               -->       Recalls stored information from memory.

Other Queries                     Generates a response using GPT-4.


4. Running the Script

  Run the script using:

    python your_script_name.py

  The assistant listens for voice commands and responds intelligently.

  Example interactions:

  User: "What time is it?"

  Assistant: "The current time is 10:15 AM."

  User: "Remember my birthday is January 1st."

  Assistant: "I'll remember that your birthday is January 1st."

Customization
  Change Voice:
    Modify the voice index in the script:
        engine.setProperty('voice', voices[0].id)  # Change index to select desired voice
  Adjust GPT Parameters:
    Modify max_tokens and temperature to fine-tune GPT responses.
  Extend Commands: Add more commands and their handlers in the main() function.


Troubleshooting

Microphone Issues: Ensure your microphone is set up and accessible by the script.
API Errors: Check if the OpenAI API key is correctly set in your environment.
Speech Recognition Errors: Install/update PyAudio:
    pip install pyaudio
(For Windows, download appropriate wheels from PyAudio Downloads).



Future Improvements

Add support for offline speech recognition.

Implement more advanced memory querying.

Integrate with other APIs (e.g., weather, calendars).

Add a graphical interface for user interaction.

License

This project is open-source and available under the MIT License.

Feel free to contribute and improve the project!
