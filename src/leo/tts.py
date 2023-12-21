from pathlib import Path
import tempfile
import datetime

from dataclasses import dataclass

import pydub
from pysubparser.parser import parse
from pysubparser.classes.subtitle import Subtitle
from pysubparser import writer
from pydub import AudioSegment
import tempfile

import polly

class Clip:
    def __init__(self, subtitles:list[Subtitle]=None):
        self._subtitles:list[Subtitle] = subtitles
        self.fixed_subtitles:list[Subtitle] = list()
        self.audio:pydub.audio_segment.AudioSegment = pydub.audio_segment.AudioSegment.empty()

    def compile(self):
        '''Main method. reads the loaded _subtitles and creates the self with both the fixed subtitles and audios'''
        for sub in self._subtitles:
            file = polly.synthetize(sub.text)
            audio = AudioSegment.from_file(file.name)
            fixed_subtitle = self._fix_subtitle(sub, audio)
            self.fixed_subtitles.append(fixed_subtitle)
            self.audio += audio
        writer.write(self.fixed_subtitles, path='temp.srt')
        self.audio.export('temp.mp3', format='mp3')

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

    def _add_seconds_to_time(self, date: datetime.time, seconds: float) -> datetime.time:
        total_seconds = date.hour * 3600 + date.minute * 60 + date.second + seconds
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return datetime.time(hours % 24, minutes, seconds)


def from_file(srt_path:str) -> Clip:
    '''Gets a string pointing to the path of a srt file and returns a Clip of it.'''
    _file = Path(srt_path).absolute()
    if not _file.exists():
        raise FileNotFoundError(_file)
    return Clip(subtitles=list(parse(str(_file))))


if __name__ == '__main__':
    clip = from_file('sample.srt')
    clip.compile()
    # clip._create_working_directory()clip