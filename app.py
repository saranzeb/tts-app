import os
import uuid
import io
import zipfile
from gtts import gTTS
import streamlit as st

AUDIO_DIR = "audio_files"

CHINESE_VOICES = [
    "zh-cn",  # gTTS only needs one Chinese language code
]

def synth_one(text: str, filename: str):
    """Generate one MP3 file using gTTS."""
    tts = gTTS(text=text, lang="zh")
    tts.save(filename)

def synth_multiple(text: str, repeat: int) -> list[str]:
    """Generate multiple Chinese TTS files."""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    file_paths = []
    for i in range(repeat):
        file_id = str(uuid.uuid4())[:8]
        filename = os.path.join(AUDIO_DIR, f"tts_{file_id}_{i+1}.mp3")
        synth_one(text, filename)
        file_paths.append(filename)
    return file_paths

def make_zip(file_paths: list[str]) -> bytes:
    """ZIP all generated audio files."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in file_paths:
            if os.path.exists(path):
                zf.write(path, arcname=os.path.basename(path))
    zip_buffer.seek(0)
    return zip_buffer.read()

def main():
    st.title("🇨🇳 Chinese TTS (gTTS Version)")
    st.write("Works on Streamlit Cloud!")

    text = st.text_area("Chinese Text", "你好，我是你的中文老师。")

    repeat = st.slider("How many audio files to generate?", 1, 10, 3)

    if st.button("Generate Audio"):
        with st.spinner("Generating..."):
            try:
                file_paths = synth_multiple(text, repeat)
            except Exception as e:
                st.error(f"Error: {e}")
                return

        st.success("Generated audio successfully!")

        st.subheader("Audio Preview")
        for i, path in enumerate(file_paths, 1):
            with open(path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
                st.caption(os.path.basename(path))

        st.subheader("Download All as ZIP")
        zip_bytes = make_zip(file_paths)
        st.download_button(
            label="Download ZIP",
            data=zip_bytes,
            file_name="tts_outputs.zip"
