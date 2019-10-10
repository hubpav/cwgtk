import click
import datetime
import fileinput
import gspread
import multiprocessing
import os
import queue
import sqlite3
import tempfile
from oauth2client.client import GoogleCredentials
from google.cloud import texttospeech

__version__ = 'v1.0.0'


class State:
    def __init__(self):
        self.quit = multiprocessing.Event()
        self.queue = multiprocessing.Queue()
        self.ready = multiprocessing.Event()
        self.ready.set()


@click.command()
@click.version_option(version=__version__)
def main():
    try:
        state = State()
        multiprocessing.Process(target=read, args=(state,)).start()
        for line in fileinput.input():
            if state.quit.is_set():
                break
            if state.ready.is_set():
                state.ready.clear()
                state.queue.put(line)
        state.quit.set()
    except KeyboardInterrupt:
        pass
    except:
        state.quit.set()


def create_log(name, tag):
    now = datetime.datetime.now()
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = GoogleCredentials.get_application_default().create_scoped(scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("CWGTK - Coffee Log")
    worksheet = spreadsheet.worksheet('Log')
    values = [now.strftime('%Y-%m-%d %H:%M:%S'), tag, name if name is not None else '']
    if worksheet.row_count < 2:
        worksheet.append_row(['Date', 'Tag', 'Name'])
        worksheet.append_row(values)
    else:
        worksheet.insert_row(values, index=2)


def record(tag):
    conn = sqlite3.connect('sql/coffeelog.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, timestamp INTEGER NOT NULL, tag TEXT NOT NULL)')
    c.execute("INSERT INTO records (timestamp, tag) VALUES (datetime('now', 'localtime'), ?)", (tag,))
    conn.commit()
    c.execute("SELECT count(*) FROM records WHERE timestamp >= date('now', 'localtime') AND tag = ?", (tag,))
    count = c.fetchone()[0]
    c.execute('CREATE TABLE IF NOT EXISTS people (id INTEGER PRIMARY KEY, tag TEXT NOT NULL, name TEXT NOT NULL, phrase TEXT NOT NULL)')
    conn.commit()
    c.execute("SELECT name, phrase FROM people WHERE tag = ?", (tag,))
    row = c.fetchone()
    name = row[0] if row is not None else None
    phrase = ' ' + row[1] if row is not None else ''
    conn.close()
    sentence = 'Dnes je to {}. káva{}.'.format(count, phrase)
    say(sentence)
    return name


def say(text):
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='cs-CZ',
        name='cs-CZ-Wavenet-A',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
    with tempfile.NamedTemporaryFile(suffix='.mp3') as fp:
        fp.write(response.audio_content)
        fp.flush()
        os.system('mpg123 -q {}'.format(fp.name))


def read(state):
    try:
        while not state.quit.is_set():
            try:
                tag = state.queue.get(timeout=0.1).rstrip()
            except queue.Empty:
                continue
            os.system('aplay -q /home/pi/cwgtk/coffeelog/bell.wav')
            name = record(tag)
            state.ready.set()
            create_log(name, tag)
    except KeyboardInterrupt:
        pass
    except:
        state.quit.set()
