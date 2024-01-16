import requests
from whisper_run import get_transcription

# URLs for the API endpoints
api_url_chat = "http://127.0.0.1:8000/api/ChatMessage"
api_url_audio = "http://127.0.0.1:8000/api/AudioFile"


def get_transcription_using_whisper(audio_message_id):
    file_name = download_audio_file_from_audio_message_id(audio_message_id)
    transcription = get_transcription(file_name)
    update_transcriptions(transcription,  audio_message_id)


def update_transcriptions(transcription, audio_message_id):
    url = f"{api_url_audio}/{audio_message_id}/"
    data = {"transcription_en": transcription}
    response = requests.patch(url, data=data)
    if response.status_code == 200:
        print("Transcription updated successfully.")
    else:
        print(f"Failed to update transcription. Status code: {response.status_code}")


def download_audio_file_from_chat_message(chat_message_id):
    audio_message_id = get_audio_message_id(chat_message_id)
    audio_file_link = get_audio_file_link(audio_message_id)
    download_file(audio_file_link, "audio.webm")


def download_audio_file_from_audio_message_id(audio_message_id):
    audio_file_link = get_audio_file_link(audio_message_id)
    file_name = f"audio+{audio_message_id}.webm"
    download_file(audio_file_link, file_name)
    return file_name


# Function to get the audio message ID
def get_audio_message_id(chat_message_id):
    url = f"{api_url_chat}/{chat_message_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Assuming the first item in the list contains the required ID
        print(data)
        return data['audio_message_id']
    else:
        raise Exception(f"Failed to get audio message ID. Status code: {response.status_code}")


# Function to get the audio file link
def get_audio_file_link(audio_message_id):
    # Construct the URL with the audio message ID
    url = f"{api_url_audio}/{audio_message_id}/"
    print(url)
    print("http://127.0.0.1:8000/api/AudioFile/b4856f71-be16-4fd0-8aae-dac684e30668/")
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        # Assuming the structure of the response and getting the 'audio' field
        return data['audio']
    else:
        raise Exception(f"Failed to get audio file link. Status code: {response.status_code}")


def download_file(url, file_name):
    # Send an HTTP GET request to the file URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Define the local filename to save the file

        # Open the file in binary write mode and save the content
        with open(file_name, 'wb') as file:
            file.write(response.content)

        print(f"File downloaded successfully: {file_name}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")