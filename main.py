import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from text_to_speech import text_to_speech
from speech_to_text import transcribe_audio
from record_audio import record_audio

load_dotenv()

# Configure the API key
genai.configure(api_key = os.getenv('GOOGLE_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

#path of audio file for transcribing
input_file = "recording.wav"

# Pre-prompt for the bot
pre_prompt = "Behave as a corporate tech team lead. Analyze the task and the input and ask a relevant follow-up question. Keep the questions very short and simple."

def generate_follow_up_question(conversation_history):
    combined_history = "\n".join(conversation_history)
    response = model.generate_content(combined_history)
    return response.text

def read_participant_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    names = []
    tasks = []

    # Extract names and tasks into separate lists
    for entry in data['previous_tasks']:
        names.append(entry['attendee'])
        tasks.append(entry['task'])

    # print("Names", names)
    # print("Tasks", tasks)
    return names, tasks

def chat_with_gemini(names, tasks):
    # Opening the meeting
    opening_line = "Welcome to the Next Tech Lab Progress Meeting!\n\nGood morning everyone, and welcome to our progress check-in meeting.\nI'm your AI assistant today, and I'll be guiding us through this session."
    print(f"AI: {opening_line}")
    text_to_speech(opening_line)

    for idx in range(len(names)):
        participant_name = names[idx]
        task = tasks[idx]

        # Start with the attendee
        call_to_attendee = f"Hello {participant_name}. Could you please share your progress on {task}?"
        print(f"AI: {call_to_attendee}")
        text_to_speech(call_to_attendee)

        # Ask for user response
        record_audio(output_file="recording.wav")
        user_response = transcribe_audio(input_file)
        print(f"{participant_name}: {user_response}")
        
        # Conversation history for context
        conversation_history = [
            f"instruction: {pre_prompt}",
            f"Task: {task}",
            f"User_input: {user_response}"
        ]

        # Generate and handle follow-up questions in a loop
        for i in range(2):  # Two iterations for follow-up questions
            follow_up_question = generate_follow_up_question(conversation_history)
            print(f"AI: {follow_up_question}")
            text_to_speech(follow_up_question)
            
            record_audio(output_file="recording.wav")
            follow_up_response = transcribe_audio(input_file)
            print(f"{participant_name}: {follow_up_response}")
            # follow_up_response = input(f"Your follow-up response (for {participant_name}): ")
            
            # Update conversation history
            conversation_history.append(f"AI: {follow_up_question}")
            conversation_history.append(f"User_input: {follow_up_response}")

        # Conclude discussion for this participant
        conclusion = f"Thank you for the update, {participant_name}."
        print(f"AI: {conclusion}")
        text_to_speech(conclusion)
        
    # Closing the meeting
    closing_remarks = "Thank you all for the updates. This concludes our meeting. Keep up the good work!"
    print(f"AI: {closing_remarks}")
    text_to_speech(closing_remarks)

def main():
    # Load participant data from JSON file
    file_path = 'participant_data.json'
    names, tasks = read_participant_data(file_path)

    chat_with_gemini(names, tasks)

if __name__ == "__main__":
    main()
