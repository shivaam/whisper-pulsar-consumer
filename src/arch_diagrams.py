from diagrams import Cluster, Diagram
from diagrams.aws.compute import ECS, Lambda
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.queue import RabbitMQ

with Diagram("Chat Message Processing Workflow", show=False, filename="arch.png"):
    user = User("User")

    with Cluster("Django Web Application"):
        django = Server("Django Web Server")

    with Cluster("Pulsar Cluster"):
        pulsar_new = RabbitMQ("new_chat_message_topic")
        pulsar_transcribed = RabbitMQ("chat_message_transcribed")

    with Cluster("Processing Jobs"):
        ecs_transcribe = ECS("Transcription Job")
        ecs_image = Lambda("Image Generation Job")

    user >> django >> pulsar_new >> ecs_transcribe >> django
    django >> pulsar_transcribed >> ecs_image >> django