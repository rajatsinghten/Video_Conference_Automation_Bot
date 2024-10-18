import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from text_to_speech import text_to_speech
from speech_to_text import transcribe_audio
from record_audio import record_audio

load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Path of audio file for transcribing
input_file = "recording.wav"

# Pre-prompt for the bot
pre_prompt = "Behave as a corporate tech team lead. Analyze the task and the input and ask a relevant follow-up question. Keep the questions very short and simple."

def generate_follow_up_question(conversation_history):
    try:
        combined_history = "\n".join(conversation_history)
        response = model.generate_content(combined_history)
        return response.text
    except Exception as e:
        print(f"Error generating follow-up question: {e}")
        return "Could you clarify that?"

def record_and_transcribe(input_file):
    try:
        record_audio(output_file=input_file)
        return transcribe_audio(input_file)
    except Exception as e:
        print(f"Error in recording or transcribing audio: {e}")
        return None

def read_participant_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        names = [entry['attendee'] for entry in data['previous_tasks']]
        tasks = [entry['task'] for entry in data['previous_tasks']]
        return names, tasks
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return [], []
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        return [], []

def chat_with_gemini(names, tasks):
    # Opening the meeting
    opening_line = "Welcome to the Next Tech Lab Progress Meeting!\n\nGood morning everyone, and welcome to our progress check-in meeting.\nI'm your AI assistant today, and I'll be guiding us through this session."
    print(f"AI: {opening_line}")
    text_to_speech(opening_line)

    for idx in range(len(names)):
        participant_name = names[idx]
        task = tasks[idx]

        call_to_attendee = f"Hello {participant_name}. Could you please share your progress on {task}?"
        print(f"AI: {call_to_attendee}")
        text_to_speech(call_to_attendee)

        user_response = record_and_transcribe(input_file)
        if user_response is None:
            continue
        print(f"{participant_name}: {user_response}")

        conversation_history = [f"instruction: {pre_prompt}", f"Task: {task}", f"User_input: {user_response}"]

        # Dynamic follow-up question loop
        while True:
            follow_up_question = generate_follow_up_question(conversation_history)
            print(f"AI: {follow_up_question}")
            text_to_speech(follow_up_question)
            
            follow_up_response = record_and_transcribe(input_file)
            if follow_up_response is None or len(follow_up_response.strip()) == 0:
                break
            print(f"{participant_name}: {follow_up_response}")
            
            conversation_history.append(f"AI: {follow_up_question}")
            conversation_history.append(f"User_input: {follow_up_response}")

        conclusion = f"Thank you for the update, {participant_name}."
        print(f"AI: {conclusion}")
        text_to_speech(conclusion)

    closing_remarks = "Thank you all for the updates. This concludes our meeting. Keep up the good work!"
    print(f"AI: {closing_remarks}")
    text_to_speech(closing_remarks)

def main():
    # Load participant data from JSON file
    file_path = 'participant_data.json'
    names, tasks = read_participant_data(file_path)

    if names and tasks:  # Only proceed if data is loaded correctly
        chat_with_gemini(names, tasks)
    else:
        print("No participant data found or error in loading data.")

if __name__ == "__main__":
    main()
