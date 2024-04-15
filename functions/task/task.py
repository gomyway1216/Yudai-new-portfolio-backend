from datetime import datetime
from openai import OpenAI
from text_to_speech import text_to_speech
from speech_to_text import speech_to_text
from google.cloud import firestore

# Prepare the template
template = """You are an agenet that helps a chunk of text into meaningful task list.
User provide a single text that contains multiple tasks, and you need to extract each task and provide a list of tasks.
Constraints:
- The text will be either in English or Japanese or a mix of both.
"""

def process_audio(audio_file, open_api_key):
    """
    Process the audio file and return the chatbot's response.
    """
    print("running process_audio")

    client = OpenAI(api_key=open_api_key)

    # Initialize messages
    messages = [{"role": "system", "content": template}]

    # Convert speech to text
    user_message = speech_to_text(audio_file, open_api_key)

    # Skip processing if the text is empty
    if user_message == "":
        return None

    print("Your message: \n{}".format(user_message))
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-turbo",
    )

    bot_message = response.choices[0].message.content
    print(type(bot_message))
    save_task_to_database(bot_message)
    print("Chatbot's response: \n{}".format(bot_message))

    # return success response
    return bot_message


def save_task_to_database(bot_message):
    """
    Save the tasks extracted from the chatbot's response to Firestore.
    """

    print('bot_message:', bot_message)
    db = firestore.Client()

    # Extract tasks from the chatbot's response
    tasks = bot_message.strip().split("\n")

    # Get the current date and time
    current_date = datetime.now()

    # Assume you have the user's document ID
    user_doc_id = "aoUPpC4gz7QlvbMcpNH5"  # Replace with the actual user's document ID

    # Iterate over each task and store it in Firestore
    for task in tasks:
        if task:
            task_parts = task.split(".", 1)
            if len(task_parts) == 2:
                task_number = task_parts[0].strip()
                task_name = task_parts[1].strip()

                # Create a new document reference in the "tasks" collection
                task_ref = db.collection("user").document(user_doc_id).collection("task").document()

                # Set the task data in Firestore
                task_ref.set({
                    "name": task_name,
                    "created_at": current_date
                })

    print("Tasks stored in Firestore successfully.")