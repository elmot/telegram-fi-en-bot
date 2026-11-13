import logging
import os
import re
from typing import List, Optional
from deep_translator import MyMemoryTranslator

logger = logging.getLogger(__name__)

class FinnishTranslator:
    def __init__(self, provider: str = "mymemory", deepl_key: Optional[str] = None, mymemory_email: Optional[str] = None):
        self.provider = provider.lower().strip()
        self.deepl_key = deepl_key
        self.mymemory_email = mymemory_email
        self._deepl_client = None

        if self.provider == "deepl" and self.deepl_key:
            try:
                import deepl
                self._deepl_client = deepl.Translator(self.deepl_key)
                logger.info("Initialized DeepL translation engine.")
            except Exception as e:
                logger.warning(f"Failed to initialize DeepL client: {e}. Falling back to MyMemory.")
                self.provider = "mymemory"

        if self.provider == "mymemory":
            logger.info("Initialized MyMemory translation engine (Finnish -> English).")

    def _chunk_text(self, text: str, max_chunk_size: int = 400) -> List[str]:
        """Split text into chunks that respect sentence/line boundaries and character limits."""
        if len(text) <= max_chunk_size:
            return [text]

        paragraphs = text.split("\n")
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_len = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if current_len + len(para) + 1 <= max_chunk_size:
                current_chunk.append(para)
                current_len += len(para) + 1
            else:
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = []
                    current_len = 0

                if len(para) <= max_chunk_size:
                    current_chunk.append(para)
                    current_len = len(para)
                else:
                    # Paragraph is longer than max_chunk_size, split by sentence
                    sentences = re.split(r'(?<=[.!?]) +', para)
                    for sent in sentences:
                        if current_len + len(sent) + 1 <= max_chunk_size:
                            current_chunk.append(sent)
                            current_len += len(sent) + 1
                        else:
                            if current_chunk:
                                chunks.append(" ".join(current_chunk))
                                current_chunk = []
                                current_len = 0
                            
                            # Fallback if a single sentence is still huge: split by words
                            if len(sent) > max_chunk_size:
                                words = sent.split(" ")
                                for word in words:
                                    if current_len + len(word) + 1 <= max_chunk_size:
                                        current_chunk.append(word)
                                        current_len += len(word) + 1
                                    else:
                                        if current_chunk:
                                            chunks.append(" ".join(current_chunk))
                                        current_chunk = [word]
                                        current_len = len(word)
                            else:
                                current_chunk.append(sent)
                                current_len = len(sent)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks or [text]

    def translate(self, text: str) -> str:
        """Translate Finnish text to English."""
        if not text or not text.strip():
            return ""

        text = text.strip()

        # DeepL Translation
        if self.provider == "deepl" and self._deepl_client:
            try:
                # DeepL handles long text automatically
                result = self._deepl_client.translate_text(
                    text,
                    source_lang="FI",
                    target_lang="EN-US"
                )
                return str(result.text)
            except Exception as e:
                logger.error(f"DeepL translation error: {e}. Falling back to MyMemory.")

        # MyMemory Translation (default, free, no key required)
        chunks = self._chunk_text(text, max_chunk_size=400)
        translator = MyMemoryTranslator(source="fi-FI", target="en-GB")
        
        translated_parts = []
        for chunk in chunks:
            try:
                translated_part = translator.translate(chunk)
                if translated_part:
                    translated_parts.append(translated_part)
                else:
                    translated_parts.append(chunk)
            except Exception as err:
                logger.warning(f"MyMemory chunk error: {err}. Keeping original chunk.")
                translated_parts.append(chunk)

        return "\n\n".join(translated_parts)

