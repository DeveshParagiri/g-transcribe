import os
import time
from datetime import datetime, timedelta
from google.cloud import speech_v2, storage
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
from google.api_core import client_options

import base64
import json


creds_base64 = os.environ.get("GOOGLE_CREDENTIALS_BASE64")
creds_json_str = base64.b64decode(creds_base64).decode("utf-8")
creds_info = json.loads(creds_json_str)
# creds = Credentials.from_service_account_info(creds_info)

credentials = service_account.Credentials.from_service_account_info(creds_info)

class GCStorage:
    def __init__(self, storage_client):
        self.client = storage_client
    
    def create_bucket(self, bucket_name, bucket_location='US'):
        bucket = self.client.bucket(bucket_name)
        return self.client.create_bucket(bucket, bucket_location)
    
    def get_bucket(self, bucket_name):
        return self.client.get_bucket(bucket_name)
    
    def list_buckets(self):
        buckets = self.client.list_buckets()
        return [bucket.name for bucket in buckets]

    def upload_to_bucket(self, bucket, blob_destination, file_path):
        try:
            blob = bucket.blob(blob_destination)
            blob.upload_from_filename(file_path)
            return True
        except Exception as e:
            print(e)
            return False
        
    def list_blobs(self, bucket_name):
        return self.client.list_blobs(bucket_name)
    

def transcribe_audio(project_id: str, audio_name: str, audio_location: str, language_code: str) -> cloud_speech.RecognizeResponse:
    print(f'Audio name: {audio_name}\nAudio location: {audio_location}')
    start = time.time()
    # Authenticating clients
    client_options_var = client_options.ClientOptions(
        api_endpoint="us-central1-speech.googleapis.com"
    )
    storage_client = storage.Client(credentials=credentials)
    speech_client = speech_v2.SpeechClient(client_options=client_options_var, credentials=credentials)

    gcs = GCStorage(storage_client=storage_client)

    # Creating bucket if not present
    bucket_name = 'text-stores'
    if not bucket_name in gcs.list_buckets():
        bucket_gcs = gcs.create_bucket(bucket_name=bucket_name)
    else:
        bucket_gcs = gcs.get_bucket(bucket_name=bucket_name)
    
    # Uploading audio file to audio-files folder
    audio_destination = f'audio-files/{audio_name}'
    # audio_path = f'{os.getcwd()}/{audio}'

    gcs.upload_to_bucket(bucket=bucket_gcs, blob_destination=audio_destination, file_path=audio_location)

    # Transcribing audio file

    transcript=''
    gcs_uri = 'gs://' + bucket_name + '/' + audio_destination

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[language_code],
        model='chirp',
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{project_id}/locations/us-central1/recognizers/chirp-english",
        config=config,
        uri=gcs_uri,
    )

    response = speech_client.recognize(request=request)

    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    transcript_file = f'Transcription_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'
    with open(transcript_file,'w+') as f:
        f.write(transcript)
    
    # Upload to transcript folder
    transcript_destination = f'transcripts/{transcript_file}'
    transcript_path = f'{os.getcwd()}/{transcript_file}'

    if gcs.upload_to_bucket(bucket=bucket_gcs, blob_destination=transcript_destination, file_path=transcript_path):
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(audio_destination)
        blob.delete()
        os.remove(transcript_path)
    
    end = time.time()
    print("==============================================================")
    print("PROCESSED SUCCESSFULLY!")
    print("TIME TAKEN: ", str(timedelta(seconds=end-start)))
    print("==============================================================")

    return transcript

# transcribe_audio('tpus-302411','jfk.wav','en-US')