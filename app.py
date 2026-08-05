"""Streamlit entry point for the Enterprise AI Translator."""

import os
import tempfile

import streamlit as st

from config.config import load_settings
from services.file_reader import read_file
from services.speech import SpeechService
from services.translator import TranslatorService
from utils.constants import SUPPORTED_LANGUAGES
from utils.exceptions import AppError
from utils.logger import get_logger
from utils.validators import validate_file_size

logger = get_logger(__name__)


@st.cache_resource
def get_translator() -> TranslatorService:
    """Build a cached TranslatorService for the lifetime of the app process."""
    return TranslatorService(load_settings())


@st.cache_resource
def get_speech_service() -> SpeechService:
    """Build a cached SpeechService for the lifetime of the app process."""
    return SpeechService()


@st.cache_data(show_spinner=False)
def cached_translate(text: str, language: str) -> str:
    """Translate text, caching identical (text, language) requests to save API calls."""
    return get_translator().translate(text, language)


def _init_session_state() -> None:
    st.session_state.setdefault("translated_text", "")
    st.session_state.setdefault("audio_path", "")


def _render_sidebar() -> tuple[str, str]:
    st.sidebar.title("Menu")
    mode = st.sidebar.radio("Input Method", ["Text", "File"])
    language = st.sidebar.selectbox("Target Language", list(SUPPORTED_LANGUAGES.keys()))
    return mode, language


def _get_input_text(mode: str, max_upload_size_mb: int) -> str:
    if mode == "Text":
        return st.text_area("Enter text to translate", height=200)

    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt", "csv", "xlsx", "xls"])
    if uploaded_file is None:
        return ""

    try:
        validate_file_size(uploaded_file.size, max_upload_size_mb)
    except AppError as exc:
        st.error(str(exc))
        return ""

    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    try:
        text = read_file(tmp_path, uploaded_file.name)
        st.success(f"Extracted text from '{uploaded_file.name}'.")
        return text
    except AppError as exc:
        st.error(str(exc))
        return ""
    finally:
        os.remove(tmp_path)


def main() -> None:
    """Render the Enterprise AI Translator Streamlit application."""
    st.set_page_config(page_title="Enterprise AI Translator", page_icon="🌍", layout="wide")
    _init_session_state()

    st.title("🌍 Enterprise AI Translator")
    st.caption("Translate text and documents, then listen to or download the result.")

    settings = load_settings()
    mode, language = _render_sidebar()
    source_text = _get_input_text(mode, settings.max_upload_size_mb)

    if st.button("Translate", type="primary"):
        if not source_text.strip():
            st.warning("Please enter text or upload a file first.")
        else:
            with st.spinner("Translating..."):
                try:
                    translated = cached_translate(source_text, language)
                    st.session_state.translated_text = translated
                    st.session_state.audio_path = ""
                except AppError as exc:
                    logger.error("Translation failed: %s", exc)
                    st.error(f"Translation failed: {exc}")

    if st.session_state.translated_text:
        left, right = st.columns(2)
        with left:
            st.subheader("Original")
            st.write(source_text)
        with right:
            st.subheader("Translated")
            st.write(st.session_state.translated_text)

        st.download_button(
            "Download Translation (.txt)",
            st.session_state.translated_text,
            file_name="translation.txt",
        )

        if st.button("Generate Speech"):
            with st.spinner("Generating audio..."):
                try:
                    st.session_state.audio_path = get_speech_service().generate(
                        st.session_state.translated_text, language
                    )
                except AppError as exc:
                    logger.error("Speech generation failed: %s", exc)
                    st.error(f"Speech generation failed: {exc}")

        if st.session_state.audio_path:
            st.audio(st.session_state.audio_path)
            with open(st.session_state.audio_path, "rb") as audio_file:
                st.download_button(
                    "Download Audio (.mp3)",
                    audio_file,
                    file_name="translation.mp3",
                    mime="audio/mp3",
                )

    st.markdown("---")
    st.caption("Built with Streamlit, Google Gemini, and gTTS.")


if __name__ == "__main__":
    main()
