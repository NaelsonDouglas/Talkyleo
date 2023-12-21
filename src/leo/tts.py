from pathlib import Path
import datetime
import tempfile

from pysubparser.classes.subtitle import Subtitle
from pysubparser.parser import parse
from pysubparser import writer
from pydub import AudioSegment
import pydub

import polly

class _Clip:
    def __init__(self, subtitles:list[Subtitle]=None):
        self._subtitles:list[Subtitle] = subtitles
        self.fixed_subtitles:list[Subtitle] = list()
        self.audio:pydub.audio_segment.AudioSegment = pydub.audio_segment.AudioSegment.empty()

    def compile(self) -> tuple[tempfile.NamedTemporaryFile]:
        '''Main method. reads the loaded _subtitles returns two temporary files: one containing the narration audio and other with the synced subtitles in srt'''
        for sub in self._subtitles:
            file = polly.synthetize(sub.text)
            audio = AudioSegment.from_file(file.name)
            fixed_subtitle = self._fix_subtitle(sub, audio)
            self.fixed_subtitles.append(fixed_subtitle)
            self.audio += audio
        srt_file = tempfile.NamedTemporaryFile(mode='w', prefix='subtitle_', suffix='.srt')
        audio_file = tempfile.NamedTemporaryFile(mode='w+b', prefix='audio_', suffix='.mp3')
        writer.write(self.fixed_subtitles, path=srt_file.name)
        self.audio.export(audio_file.name, format='mp3')
        return (audio_file, srt_file)

    def _fix_subtitle(self, subtitle:Subtitle, audio:pydub.AudioSegment) -> Subtitle:
        '''Fix the syncronization of a subtitle by synching it to the audio'''
        duration = audio.duration_seconds
        if self.fixed_subtitles:
            new_start = self.fixed_subtitles[-1].end
            new_end = new_start + datetime.timedelta(seconds=duration)
        else:
            new_start = datetime.datetime.min
            new_end = new_start + datetime.timedelta(seconds=duration)
        fixed_subtitle = Subtitle(index=subtitle.index, start=new_start, end=new_end, lines=subtitle.lines)
        return fixed_subtitle

def from_file(srt_path:str) -> tuple[tempfile.NamedTemporaryFile]:
    '''Gets a string pointing to the path of a srt file and returns two temporary files: one containing the narration audio and other with the synced subtitles in srt'''
    _file = Path(srt_path).absolute()
    if not _file.exists():
        raise FileNotFoundError(_file)
    return _Clip(subtitles=list(parse(str(_file)))).compile()

def from_string(string:str) -> tuple[tempfile.NamedTemporaryFile]:
    '''Gets with a valid srt subtitle and returns two temporary files: one containing the narration audio and other with the synced subtitles in srt . Wraps over `from_file`'''
    with tempfile.NamedTemporaryFile(mode='w', prefix='sub_', suffix='.srt') as file:
        file.write(string)
        file.seek(0)
        return from_file(file.name)



if __name__ == '__main__':
    sample = '1\n00:00:00,000 --> 00:00:05,000\nNão costumo compartilhar, hoje decidi, desabafar sobre minha vida.\n\n2\n00:00:00,000 --> 00:00:05,000\nNão costumo compartilhar, hoje decidi, desabafar sobre minha vida.'
    audio, srt = from_string(sample)
    audio2, srt2 = from_file('sample.srt')