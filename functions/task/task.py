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
                    "created_at": current_date,
                    "completed": False,
                })

    print("Tasks stored in Firestore successfully.")

def get_completed_tasks(user_doc_id):
    """
    Get the completed tasks for a user from Firestore.
    """
    db = firestore.Client()

    # Get the user's document reference
    user_ref = db.collection("user").document(user_doc_id)

    # Get the completed tasks for the user
    completed_tasks = user_ref.collection("task").where("completed", "==", True).stream()

    tasks = []
    for task in completed_tasks:
        task_data = task.to_dict()
        task_data["id"] = task.id
        tasks.append(task_data)

    return tasks

def get_incomplete_tasks(user_doc_id):
    """Get the incomplete tasks for a user from Firestore."""
    db = firestore.Client()
    # Get the user's document reference
    user_ref = db.collection("user").document(user_doc_id)
    
    # Query for tasks where the "completed" field is not True or doesn't exist
    incomplete_tasks = user_ref.collection("task").where("completed", "==", False).stream()

    # print('incomplete_tasks len:', len(incomplete_tasks) )
    
    tasks = []
    for task in incomplete_tasks:
        print('task:', task.to_dict())
        task_data = task.to_dict()
        task_data["id"] = task.id
        tasks.append(task_data)
    
    return tasks

def create_task(user_doc_id, task_data):
    """
    Create a new task for a user in Firestore.
    """
    db = firestore.Client()

    # Create a new document reference in the "tasks" collection
    task_ref = db.collection("user").document(user_doc_id).collection("task").document()

    # Set the task data in Firestore
    task_ref.set(task_data)

    print("Task created successfully.")


def mark_task_as_completed(user_doc_id, task_id):
    """
    Mark a task as completed for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task as completed
    task_ref.update({
        "completed": True
    })

    print("Task marked as completed successfully.")

def mark_task_as_incomplete(user_doc_id, task_id):
    """
    Mark a task as incomplete for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task as incomplete
    task_ref.update({
        "completed": False
    })

    print("Task marked as incomplete successfully.")

def delete_task(user_doc_id, task_id):
    """
    Delete a task for a user from Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Delete the task
    task_ref.delete()

    print("Task deleted successfully.")

def get_all_tasks(user_doc_id):
    """
    Get all tasks for a user from Firestore.
    """
    db = firestore.Client()

    # Get the user's document reference
    user_ref = db.collection("user").document(user_doc_id)

    # Get all tasks for the user
    all_tasks = user_ref.collection("task").stream()

    tasks = []
    for task in all_tasks:
        task_data = task.to_dict()
        tasks.append(task_data)

    return tasks

def get_task_by_id(user_doc_id, task_id):
    """
    Get a task by ID for a user from Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Get the task data
    task_data = task_ref.get().to_dict()

    return task_data

def update_task_name(user_doc_id, task_id, new_name):
    """
    Update the name of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task name
    task_ref.update({
        "name": new_name
    })

    print("Task name updated successfully.")

def update_task(user_doc_id, task_id, task_data):
    """
    Update the task data for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task data
    task_ref.update(task_data)

    print("Task updated successfully.")

def update_task_priority(user_doc_id, task_id, priority):
    """
    Update the priority of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task priority
    task_ref.update({
        "priority": priority
    })

    print("Task priority updated successfully.")

def update_task_category(user_doc_id, task_id, category):
    """
    Update the category of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task category
    task_ref.update({
        "category": category
    })

    print("Task category updated successfully.")

def update_task_tags(user_doc_id, task_id, tags):
    """
    Update the tags of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task tags
    task_ref.update({
        "tags": tags
    })

    print("Task tags updated successfully.")

def update_task_duration(user_doc_id, task_id, duration):
    """
    Update the duration of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task duration
    task_ref.update({
        "duration": duration
    })

    print("Task duration updated successfully.")

def update_task_start_time(user_doc_id, task_id, start_time):
    """
    Update the start time of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task start time
    task_ref.update({
        "start_time": start_time
    })

    print("Task start time updated successfully.")

def update_task_end_time(user_doc_id, task_id, end_time):
    """
    Update the end time of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task end time
    task_ref.update({
        "end_time": end_time
    })

    print("Task end time updated successfully.")

def update_task_recurring(user_doc_id, task_id, recurring):
    """
    Update the recurring status of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task recurring status
    task_ref.update({
        "recurring": recurring
    })

    print("Task recurring status updated successfully.")

def update_task_recurrence_rule(user_doc_id, task_id, recurrence_rule):
    """
    Update the recurrence rule of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task recurrence rule
    task_ref.update({
        "recurrence_rule": recurrence_rule
    })

    print("Task recurrence rule updated successfully.")

def update_task_recurrence_end_date(user_doc_id, task_id, recurrence_end_date):
    """
    Update the recurrence end date of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task recurrence end date
    task_ref.update({
        "recurrence_end_date": recurrence_end_date
    })

    print("Task recurrence end date updated successfully.")

def update_task_recurrence_count(user_doc_id, task_id, recurrence_count):
    """
    Update the recurrence count of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task recurrence count
    task_ref.update({
        "recurrence_count": recurrence_count
    })

    print("Task recurrence count updated successfully.")

def update_task_recurrence_interval(user_doc_id, task_id, recurrence_interval):
    """
    Update the recurrence interval of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task recurrence interval
    task_ref.update({
        "recurrence_interval": recurrence_interval
    })

    print("Task recurrence interval updated successfully.")

def update_task_recurrence_days(user_doc_id, task_id, recurrence_days):
    """
    Update the recurrence days of a task for a user in Firestore.
    """
    db = firestore.Client()

    # Get the task's document reference
    task_ref = db.collection("user").document(user_doc_id).collection("task").document(task_id)

    # Update the task recurrence days
    task_ref.update({
        "recurrence_days": recurrence_days
    })

    print("Task recurrence days updated successfully.")

def create_tag(user_doc_id, tag_name):
    """
    Create a new tag for a user in Firestore.
    """
    db = firestore.Client()

    # Create a new document reference in the "tags" collection
    tag_ref = db.collection("user").document(user_doc_id).collection("task_tag").document()

    # Set the tag data in Firestore
    tag_ref.set({
        "name": tag_name
    })

    print("Tag created successfully.")

def get_all_tags(user_doc_id):
    """
    Get all tags for a user from Firestore.
    """
    db = firestore.Client()

    # Get the user's document reference
    user_ref = db.collection("user").document(user_doc_id)

    # Get all tags for the user
    all_tags = user_ref.collection("task_tag").stream()

    tags = []
    for tag in all_tags:
        tag_data = tag.to_dict()
        tags.append(tag_data)

    return tags

def create_category(user_doc_id, category_name):
    """
    Create a new category for a user in Firestore.
    """
    db = firestore.Client()

    # Create a new document reference in the "categories" collection
    category_ref = db.collection("user").document(user_doc_id).collection("task_category").document()

    # Set the category data in Firestore
    category_ref.set({
        "name": category_name
    })

    print("Category created successfully.")

def get_all_categories(user_doc_id):
    """
    Get all categories for a user from Firestore.
    """
    db = firestore.Client()

    # Get the user's document reference
    user_ref = db.collection("user").document(user_doc_id)

    # Get all categories for the user
    all_categories = user_ref.collection("task_category").stream()

    categories = []
    for category in all_categories:
        category_data = category.to_dict()
        categories.append(category_data)

    return categories

