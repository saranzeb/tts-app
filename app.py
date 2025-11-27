import os
import uuid
import asyncio
import io
import zipfile

import streamlit as st
import edge_tts

# ==========================
# CONFIG
# ==========================

# Folder for saving audio files
AUDIO_DIR = "audio_files"

# A reasonably rich set of Chinese voices from Edge TTS.
# If any voice fails on your setup, you can comment it out.
CHINESE_VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-XiaohanNeural",
    "zh-CN-XiaomengNeural",
    "zh-CN-XiaomoNeural",
    "zh-CN-XiaoruiNeural",
    "zh-CN-XiaoshuangNeural",
    "zh-CN-XiaoxuanNeural",
    "zh-CN-XiaoyanNeural",
    "zh-CN-XiaoyuNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
]

# Map to nicer labels if you want
VOICE_LABELS = {v: v for v in CHINESE_VOICES}


# ==========================
# TTS LOGIC
# ==========================

async def synth_one(text: str, voice: str, filename: str):
    """
    Generate one MP3 file with given text and voice using edge_tts.
    """
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(filename)


async def synth_multiple(text: str, voices: list[str], repeat: int) -> list[str]:
    """
    Generate multiple audio files:
    - Use selected voices
    - Loop over them until we reach 'repeat' count
    - Return list of file paths
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    file_paths = []

    if not voices:
        raise ValueError("No voices selected.")

    tasks = []

    for i in range(repeat):
        voice = voices[i % len(voices)]  # Smart looping
        file_id = str(uuid.uuid4())[:8]
        safe_voice = voice.replace("zh-CN-", "")
        filename = os.path.join(AUDIO_DIR, f"{safe_voice}_{file_id}_{i+1}.mp3")
        tasks.append(synth_one(text, voice, filename))
        file_paths.append(filename)

    # Run all synth tasks
    await asyncio.gather(*tasks)

    return file_paths


def make_zip(file_paths: list[str]) -> bytes:
    """
    Create an in-memory ZIP file from list of file paths.
    Returns bytes for Streamlit download_button.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in file_paths:
            if os.path.exists(path):
                arcname = os.path.basename(path)
                zf.write(path, arcname=arcname)
    zip_buffer.seek(0)
    return zip_buffer.read()


# ==========================
# STREAMLIT UI
# ==========================

def main():
    st.set_page_config(page_title="Chinese TTS Multi-Voice", page_icon="🗣️")
    st.title("🗣️ Chinese TTS with Multiple Voices")
    st.write("Enter Chinese text, select voices, choose repeat count, and generate multiple MP3s.")

    # Text input
    text = st.text_area("Chinese Text", value="你好，我是你的中文老师。", height=100)

    # Voice selection
    st.subheader("Voices")
    selected_voices = st.multiselect(
        "Select one or more voices",
        options=CHINESE_VOICES,
        default=["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"],
        format_func=lambda v: VOICE_LABELS.get(v, v),
    )

    # Repeat count
    repeat = st.slider(
        "How many audio files to generate?",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )

    # Generate button
    if st.button("Generate Audio"):
        if not text.strip():
            st.error("Please enter some Chinese text.")
            return
        if not selected_voices:
            st.error("Please select at least one voice.")
            return

        with st.spinner("Generating audio files..."):
            try:
                # Run async synthesis
                file_paths = asyncio.run(synth_multiple(text, selected_voices, repeat))
            except Exception as e:
                st.error(f"Error during TTS generation: {e}")
                return

        if not file_paths:
            st.warning("No files were generated.")
            return

        st.success(f"Generated {len(file_paths)} audio file(s).")

        # Show audio players
        st.subheader("Preview Audio")
        for idx, path in enumerate(file_paths, start=1):
            if os.path.exists(path):
                with open(path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
                st.caption(f"File {idx}: {os.path.basename(path)}")
            else:
                st.warning(f"Missing file: {path}")

        # ZIP download
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
