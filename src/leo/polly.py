#https://us-east-1.console.aws.amazon.com/iamv2/home#/security_credentials/access-key-wizard
#https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/users
import boto3
from pathlib import Path
import tempfile

def synthetize(sentence:str, voice:str='Vitoria') -> tempfile.NamedTemporaryFile:
    polly = boto3.client('polly')
    polly_response = polly.synthesize_speech(Text=sentence, VoiceId=voice, LanguageCode='pt-BR', OutputFormat='mp3', Engine='neural')
    audio = polly_response['AudioStream'].read()
    file = tempfile.NamedTemporaryFile(mode='w+b', prefix='audio_', suffix='.mp3')
    file.write(audio)
    return file


if __name__ == '__main__':
    synthetize('Boa tarde a todos, e quero contar uma história muito comovente sobre a importância de amar seus pais enquanto eles estão aqui.')