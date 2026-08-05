from gtts import gTTS
from pathlib import Path
from uuid import uuid4

from utils.exceptions import SpeechGenerationError


class SpeechService:
    def generate(self, text: str, language: str) -> str:
        try:
            lang_code = language[:2].lower()
            output_path = Path("outputs") / f"speech_{uuid4().hex}.mp3"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            tts = gTTS(text=text, lang=lang_code)
            tts.save(str(output_path))
            return str(output_path)
        except Exception as exc:
            raise SpeechGenerationError(str(exc)) from exc
