import base64
import json
import pickle


def decode_message(message):
    message_body = message.get_body()
    json_body = json.loads(message_body)
    if 'task' in message_body:
        return json_body
    else:
        # Fallback to processing celery messages
        return decode_celery_message(json_body)


def decode_celery_message(json_task):
    message = base64.decodestring(json_task['body'])
    return pickle.loads(message)


def function_to_import_path(function):
    return "{}.{}".format(function.__module__, function.func_name)
