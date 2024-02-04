import io
import time
import traceback

import pulsar
from pulsar.schema import *
from avro.io import DatumReader, BinaryDecoder, DatumWriter, BinaryEncoder
from avro.schema import parse
from chat_message_processor import update_transcription_using_whisper
from pulsar.schema import BytesSchema, JsonSchema
from env_variables import PULSAR_URL
import os

# Get the current working directory
current_directory = os.getcwd()

print("Current Directory:", current_directory)

topic = 'persistent://babblebox/audio_processing/new_message'
send_message_topic = 'persistent://babblebox/audio_processing/new_transcription'

client = pulsar.Client(f'pulsar://${PULSAR_URL}:6650')
print("Pulsar Python client version:", pulsar.__version__)


class ChatMessage(Record):
    id = String()
    chat_id = String()
    audio_message_id = String()
    image_id = String()
    timestamp = String()


consumer = client.subscribe(topic, subscription_name='my-sub')
producer = client.create_producer(send_message_topic, schema=JsonSchema(ChatMessage))

# Define your Avro schema
schema_path = current_directory + '/src/audiofile_schema.avsc'
with open(schema_path, 'r') as file:
    schema = parse(file.read())

print(schema)


def deserialize_from_avro(data, avro_schema):
    bytes_reader = io.BytesIO(data)
    decoder = BinaryDecoder(bytes_reader)
    reader = DatumReader(avro_schema)
    return reader.read(decoder)


def serialize_to_avro(data, avro_schema):
    writer = DatumWriter(avro_schema)
    bytes_writer = io.BytesIO()
    encoder = BinaryEncoder(bytes_writer)
    writer.write(data, encoder)
    return bytes_writer.getvalue()


def send_pulsar_message(serialized_data):
    producer.send(serialized_data)
    print("Message sent to pulsar successfully")


#
# data = ChatMessage()
# data.id = "test"
# data.chat_id = "test"
# data.audio_message_id = "ae89dd51-b683-48b7-aa2d-6bac9e768c97"
# data.image_id = "42037c35-262c-4bf6-88bc-2d3d3a0ad524"
# data.timestamp = "test"
# print(data)
# while True:
#     # pause for 5 seconds here
#     time.sleep(60)
#     send_pulsar_message(data)


while True:
    msg = consumer.receive()
    try:
        print("Received message: '%s'" % msg.data())
        deserialize_msg = deserialize_from_avro(msg.data(), schema)
        print(deserialize_msg)
        update_transcription_using_whisper(deserialize_msg["audio_message_id"])
        data = ChatMessage(
            id=deserialize_msg["id"],
            chat_id=deserialize_msg["chat_id"],
            audio_message_id=deserialize_msg["audio_message_id"],
            image_id=deserialize_msg["image_id"],
            timestamp=deserialize_msg["timestamp"]
        )
        send_pulsar_message(data)
        consumer.acknowledge(msg)
    except Exception as e:
        print("Error message:", e)
        traceback.print_exc()

client.close()
