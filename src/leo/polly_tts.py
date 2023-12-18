#https://us-east-1.console.aws.amazon.com/iamv2/home#/security_credentials/access-key-wizard
#https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/users
import boto3


def store_audio(resource_name:str, audio:bytes) -> Path:
    audio_path = Path('temp.mp3').absolute()
    with open(str(audio_path), 'wb') as f:
        f.write(audio)
    return audio_path

def synthetize_sentence(sentence:str, voice:str='Victoria'):
    polly = boto3.client('polly')
    polly_response = polly.synthesize_speech(Text=sentence, VoiceId=voice, LanguageCode='pt-BR', OutputFormat='mp3', Engine='neural')
    audio = polly_response['AudioStream'].read()
    audio_path = store_audio('temp.mp3', audio)
    return audio_path



if __name__ == '__main__':
    synthetize_sentence('Boa tarde a todos, e quero contar uma história muito comovente sobre a importância de amar seus pais enquanto eles estão aqui.')