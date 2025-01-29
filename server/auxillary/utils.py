import os
from mutagen.mp3 import MP3 
import assemblyai as aai
import yt_dlp
import warnings

def getAssemblyAITranscript(audioFile : str, authKey : str, log : bool = False) -> list[aai.types.Word]:
    '''Return a transcript of the given audio, composed of a list containting type Word (see assemblyai.types) with start, end, speaker, and confidence attributes
    
    params:
    audioFile: The filepath of the audio file to be processed into a transcript via the AssemblyAI SDK.
    authKey: The AssemblyAI API key for authorization.
    log: Whether to print the transcript into the terminal.
    '''
    if not (isinstance(authKey, str) and isinstance(audioFile, str)):
        raise TypeError

    if not os.path.isfile(audioFile):
        raise FileNotFoundError("Audio file for transcription not found")
    

    aai.settings.api_key = authKey
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audioFile)

    if log:
        print(f"AssemblyAI Transcript: {len(transcript.words)} words")
        for word in transcript.words:
            print(f"Transcript Word Metadata: Text: {word.text} Start: {word.start} End: {word.end} Confidence: {word.confidence} Speaker: {word.speaker}")
    return transcript.words

def getAudioLength(filepath : str | MP3) -> float:
    '''Return the length of the audio file or mutagen MP3 instance provided'''
    if isinstance(filepath, str):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Given filepath {filepath} could not be found.")
        
        if not filepath.endswith(".mp3"):
            raise TypeError(f"File {filepath} is not recognized as an MP3 file.")

        try:
            mpeg_obj = MP3(filepath)
            if mpeg_obj.info.length == 0:
                warnings.warn("Given audio file's length is 0. Please ensure audio integrity")
            return mpeg_obj.info.length
        
        except Exception as e:
            raise RuntimeError(f"Error processing filepath {filepath} using Mutagen.mp3\n{e}")

    elif isinstance(filepath, MP3):
        if filepath.info.length == 0:
            warnings.warn("Given MP3 object's length is 0. Please ensure MP3 integrity")
        return filepath.info.length
    else:
        raise TypeError(f"Invalid input given {filepath} to getAudioLength function (Only filepaths as str or direct Mutagen.mp3.MP3 instances supported)")


def download_youtube_video(url : str, output_path : str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
