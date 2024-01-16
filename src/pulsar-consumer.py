import io

import pulsar
from avro.io import DatumReader, BinaryDecoder
from avro.schema import parse
from chat_message_processor import get_transcription_using_whisper

topic = 'persistent://babblebox/audio_processing/test'

client = pulsar.Client('pulsar://10.2.115.98:6650')
print("Pulsar Python client version:", pulsar.__version__)

consumer = client.subscribe(topic, subscription_name='my-sub')

# Define your Avro schema
schema_path = 'audiofile_schema.avsc'
with open(schema_path, 'r') as file:
    schema = parse(file.read())

print(schema)


def deserialize_from_avro(data, avro_schema):
    bytes_reader = io.BytesIO(data)
    decoder = BinaryDecoder(bytes_reader)
    reader = DatumReader(avro_schema)
    return reader.read(decoder)


while True:
    msg = consumer.receive()
    try:
        print("Received message: '%s'" % msg.data())
        deserialize_msg = deserialize_from_avro(msg.data(), schema)
        print(deserialize_msg)
        get_transcription_using_whisper(deserialize_msg["audio_message_id"])
    except Exception as e:
        print(e)
    consumer.acknowledge(msg)

client.close()
