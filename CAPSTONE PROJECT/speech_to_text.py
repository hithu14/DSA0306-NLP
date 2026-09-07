import whisper

# Load Whisper model
model = whisper.load_model("base")


def convert_speech_to_text(audio_file):

    result = model.transcribe(audio_file)

    return result["text"]