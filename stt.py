import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("STT_URL")
API_KEY = os.getenv("STT_API_KEY")

async def convert_to_text(audio_path: str):
    async with aiohttp.ClientSession() as session:
        with open(audio_path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field(
                name="audio",
                value=f,
                filename="voice.ogg",
                content_type="audio/ogg"
            )
            form.add_field("has_offsets", "false")
            form.add_field("has_diarization", "false")
            form.add_field("language", "uz")

            headers = {"x-api-key": API_KEY}

            async with session.post(URL, data=form, headers=headers) as response:
                return await response.json()