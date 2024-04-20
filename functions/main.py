from firebase_functions import firestore_fn, https_fn, options
from firebase_admin import initialize_app, firestore
import base64
import voice_chat_bot
import task.task
from firebase_functions.params import IntParam, StringParam
import json

app = initialize_app()

WELCOME_MESSAGE = StringParam("WELCOME_MESSAGE")
OPENAI_API_KEY = StringParam('OPENAI_API_KEY')
VOICEVOX_URL= StringParam('VOICEVOX_URL')

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def voice_chat(req: https_fn.Request) -> https_fn.Response:
    """Process voice chat request"""
    try:
        print('voice_chat request received')
        audio_file = req.files['audio']

        open_api_key_1 = OPENAI_API_KEY.value
        voicevox_url = VOICEVOX_URL.value

        if audio_file is None:
            return https_fn.Response("No audio data provided", status=400)

        # Save the audio data to a file
        audio_file.save("input.wav")

        # Process the audio using the process_audio function
        bot_audio_data = voice_chat_bot.process_audio("input.wav", open_api_key_1, voicevox_url)

        if bot_audio_data is None:
            return https_fn.Response("No response generated", status=400)

        # Convert the bot's audio data to base64
        bot_audio_base64 = base64.b64encode(bot_audio_data).decode("utf-8")
        # print('bot_audio_base64 response:', bot_audio_base64)
        return https_fn.Response(bot_audio_base64, headers={'Content-Type': 'audio/wav'}, status=200)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def voice_task(req: https_fn.Request) -> https_fn.Response:
    """Process voice task request"""
    try:
        print('voice_task request received')
        audio_file = req.files['audio']
        open_api_key_1 = OPENAI_API_KEY.value

        if audio_file is None:
            return https_fn.Response("No audio data provided", status=400)

        # Save the audio data to a file
        audio_file.save("input_voice_task.wav")

        # Process the audio using the process_audio function from task.task module
        bot_message = task.task.process_audio("input_voice_task.wav", open_api_key_1)

        if bot_message is None:
            return https_fn.Response("No response generated", status=400)

        return https_fn.Response(bot_message, headers={'Content-Type': 'text/plain'}, status=200)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return https_fn.Response(f"An error occurred: {str(e)}", status=500)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def get_completed_tasks(req: https_fn.Request) -> https_fn.Response:
    """Get completed tasks"""
    print('get_completed_tasks request received')
    tasks = task.task.get_completed_tasks(req.args.get('user_id'))
    tasks_json = json.dumps(tasks, default=str)
    print('tasks_json:', tasks_json)
    return https_fn.Response(tasks_json, headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def get_incomplete_tasks(req: https_fn.Request) -> https_fn.Response:
    """Get incomplete tasks"""
    print('get_incomplete_tasks request received')
    tasks = task.task.get_incomplete_tasks(req.args.get('user_id'))
    tasks_json = json.dumps(tasks, default=str)
    print('tasks_incomplete_json:', tasks_json)
    return https_fn.Response(tasks_json, headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def create_task(req: https_fn.Request) -> https_fn.Response:
    """Add a task"""
    task_id = task.task.create_task(req.args.get('user_id'), req.args.get('task_data'))
    return https_fn.Response(json.dumps({"task_id": task_id}), status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def mark_task_as_completed(req: https_fn.Request) -> https_fn.Response:
    """Complete a task"""
    task.task.mark_task_as_completed(req.args.get('user_id'), req.args.get('task_id'))
    return https_fn.Response('{"message": "Task completed"}', headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def mark_task_as_incomplete(req: https_fn.Request) -> https_fn.Response:
    """Mark a task as incomplete"""
    task.task.mark_task_as_incomplete(req.args.get('user_id'), req.args.get('task_id'))
    return https_fn.Response('{"message": "Task incomplete"}', headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def delete_task(req: https_fn.Request) -> https_fn.Response:
    """Delete a task"""
    task.task.delete_task(req.args.get('user_id'), req.args.get('task_id'))
    return https_fn.Response('{"message": "Task removed"}', status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def get_all_tasks(req: https_fn.Request) -> https_fn.Response:
    """Get all tasks"""
    tasks = task.task.get_all_tasks(req.args.get('user_id'))
    return https_fn.Response(tasks, headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def get_task(req: https_fn.Request) -> https_fn.Response:
    """Get a task"""
    task_resp = task.task.get_task_by_id(req.args.get('user_id'), req.args.get('task_id'))
    return https_fn.Response(task_resp, headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def update_task_name(req: https_fn.Request) -> https_fn.Response:
    """Update a task name"""
    task.task.update_task_name(req.args.get('user_id'), req.args.get('task_id'), req.args.get('task_name'))
    return https_fn.Response('{"message": "Task name updated"}', status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def update_task(req: https_fn.Request) -> https_fn.Response:
    """Update a task"""
    task.task.update_task(req.args.get('user_id'), req.args.get('task_id'), req.args.get('task_data'))
    return https_fn.Response('{"message": "Task updated"}', status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def create_task_tag(req: https_fn.Request) -> https_fn.Response:
    """Create a task tag"""
    task.task.create_tag(req.args.get('user_id'), req.args.get('tag_name'))
    return https_fn.Response('{"message": "Task tag created"}', status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def get_all_task_tags(req: https_fn.Request) -> https_fn.Response:
    """Get all task tags"""
    tags = task.task.get_all_tags(req.args.get('user_id'))
    return https_fn.Response(tags, headers={'Content-Type': 'application/json'}, status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def create_task_category(req: https_fn.Request) -> https_fn.Response:
    """Create a task category"""
    task.task.create_category(req.args.get('user_id'), req.args.get('category_name'))
    return https_fn.Response('{"message": "Task category created"}', status=200)

@https_fn.on_request(
    cors=options.CorsOptions(
        cors_origins=[r"http://localhost:3000", r"https://meetyudai\.com$"],
        cors_methods=["GET", "POST"],
    )
)
def get_all_task_categories(req: https_fn.Request) -> https_fn.Response:
    """Get all task categories"""
    categories = task.task.get_all_categories(req.args.get('user_id'))
    return https_fn.Response(categories, headers={'Content-Type': 'application/json'}, status=200)