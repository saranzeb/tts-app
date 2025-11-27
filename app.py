import os
import uuid
import io
import zipfile
import base64
from gtts import gTTS
import streamlit as st

AUDIO_DIR = "audio_files"

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

def audio_player(path):
    """100% phone-safe audio player using Base64."""
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    audio_html = f"""
    <audio controls style="width:100%">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def main():
    st.title("🇨🇳 Chinese TTS (Mobile-Friendly Version)")
    st.write("Generate Chinese audio that plays correctly on ALL phones.")

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

        st.subheader("Audio Preview (Phone Safe)")
        for i, path in enumerate(file_paths, 1):
            audio_player(path)
            st.caption(os.path.basename(path))

        st.subheader("Download All as ZIP")
        zip_bytes = make_zip(file_paths)
        st.download_button(
            label="Download ZIP",
            data=zip_bytes,
            file_name="tts_outputs.zip",
            mime="application/zip",
        )

if __name__ == "__main__":
    main()
