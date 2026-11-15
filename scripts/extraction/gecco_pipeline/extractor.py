"""Core extraction engine using Google Gemini API."""

import time
import random
from pathlib import Path
from typing import Optional, List

from google import genai
from google.genai import types
from loguru import logger

from gecco_pipeline.config import Settings
from gecco_pipeline.schemas import PaperResult, PaperExtraction, PaperMetadata
from gecco_pipeline.prompt_template import SYSTEM_PROMPT, EXTRACTION_PROMPT
from gecco_pipeline.utils import detect_year_from_path


class GeccoExtractor:
    """Extracts structured data from GECCO papers using Gemini."""

    def __init__(self, settings: Settings):
        """Initialize the extractor with API client and settings.
        
        Args:
            settings: Pipeline configuration settings.
        """
        self.settings = settings
        
        # Multi-key rotation setup
        self._api_keys: List[str] = settings.api_keys
        self._current_key_index: int = 0
        self._requests_on_current_key: int = 0
        self._total_requests: int = 0
        
        # Create initial client with the first key
        self.client = self._create_client(self._api_keys[0])
        
        # Rate limiting state
        self._request_count = 0
        self._window_start = time.time()
        
        logger.info(
            f"Initialized GeccoExtractor with model: {settings.MODEL_NAME}, "
            f"{len(self._api_keys)} API key(s) available"
        )

    def _create_client(self, api_key: str) -> genai.Client:
        """Create a new Gemini API client with the given key.
        
        Args:
            api_key: The Google AI API key.
        
        Returns:
            Configured genai.Client instance.
        """
        return genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                api_version="v1beta",
                timeout=120000, # 120 seconds timeout
            ),
        )

    def rotate_key(self, reason: str = "scheduled") -> None:
        """Rotate to the next API key in the pool.
        
        Args:
            reason: Why the rotation is happening (for logging).
        """
        if len(self._api_keys) <= 1:
            logger.debug("Only 1 API key available, skipping rotation")
            return
        
        old_index = self._current_key_index
        self._current_key_index = (self._current_key_index + 1) % len(self._api_keys)
        self._requests_on_current_key = 0
        
        self.client = self._create_client(self._api_keys[self._current_key_index])
        
        # Reset rate limit window for the new key
        self._request_count = 0
        self._window_start = time.time()
        
        logger.info(
            f"🔑 Rotated API key: {old_index + 1} → {self._current_key_index + 1} "
            f"(reason: {reason})"
        )

    @property
    def current_key_info(self) -> str:
        """Return a human-readable string about the current key status."""
        return (
            f"Key {self._current_key_index + 1}/{len(self._api_keys)}, "
            f"{self._requests_on_current_key}/{self.settings.REQUESTS_PER_KEY_BEFORE_ROTATE} requests"
        )

    def _rate_limit_wait(self) -> None:
        """Enforce rate limiting based on RPM configuration."""
        self._request_count += 1
        self._requests_on_current_key += 1
        self._total_requests += 1
        elapsed = time.time() - self._window_start
        
        if elapsed < 60:
            if self._request_count >= self.settings.RATE_LIMIT_RPM:
                wait_time = 60 - elapsed + random.uniform(0.5, 2.0)
                logger.info(f"Rate limit reached ({self._request_count} requests in {elapsed:.1f}s). Waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
                self._request_count = 0
                self._window_start = time.time()
        else:
            # Reset window
            self._request_count = 0
            self._window_start = time.time()
        
        # Check if scheduled key rotation is needed
        if self._requests_on_current_key >= self.settings.REQUESTS_PER_KEY_BEFORE_ROTATE:
            self.rotate_key(reason="scheduled rotation")

    def extract_from_pdf(self, pdf_path: Path, year: Optional[int] = None) -> PaperResult:
        """Extract structured data from a single GECCO paper PDF.
        
        Args:
            pdf_path: Path to the PDF file.
            year: Publication year (used for metadata if not extractable).
        
        Returns:
            PaperResult with metadata and all algorithm-landscape extractions.
        
        Raises:
            Exception: If extraction fails after all retries.
        """
        logger.info(f"Processing: {pdf_path.name} [{self.current_key_info}]")
        
        # Determine year from directory/file name if not provided
        if year is None:
            year = detect_year_from_path(pdf_path)
        
        if year is None:
            year = 2024  # Fallback default
            logger.warning(f"Could not determine year for {pdf_path.name}, using {year}")
        
        # Upload PDF to Gemini File API
        uploaded_file = self._upload_pdf(pdf_path)
        
        # Build the prompt with source file placeholder replaced
        prompt = EXTRACTION_PROMPT.replace("__SOURCE_FILE__", pdf_path.name)
        
        # Call Gemini with retry logic
        result = self._call_with_retry(uploaded_file, prompt, pdf_path, year)
        
        # Replace source_file placeholder in metadata
        result.metadata.source_file = pdf_path.name
        if result.metadata.year == 0:
            result.metadata.year = year
        
        logger.success(f"Extracted {len(result.extractions)} entries from {pdf_path.name}")
        return result

    def _upload_pdf(self, pdf_path: Path):
        """Upload a PDF file to the Gemini File API.
        
        Args:
            pdf_path: Path to the PDF file.
        
        Returns:
            Uploaded file object from the Gemini API.
        """
        logger.debug(f"Uploading {pdf_path.name} to Gemini File API...")
        
        # Check if the filename contains non-ASCII characters
        has_non_ascii = not pdf_path.name.isascii()
        temp_path = None
        
        try:
            if has_non_ascii:
                import shutil
                # Create a temporary file with a safe ASCII name in the same directory
                safe_name = f"temp_upload_{int(time.time())}_{random.randint(1000, 9999)}.pdf"
                temp_path = pdf_path.parent / safe_name
                logger.debug(f"Filename contains non-ASCII characters. Copying to safe temporary path: {safe_name}")
                shutil.copy(pdf_path, temp_path)
                upload_target = temp_path
            else:
                upload_target = pdf_path
                
            uploaded_file = self.client.files.upload(file=upload_target)
            logger.debug(f"Upload complete: {uploaded_file.name}")
            return uploaded_file
        except Exception as e:
            logger.error(f"Failed to upload {pdf_path.name}: {e}")
            raise
        finally:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def _call_with_retry(self, uploaded_file, prompt: str, pdf_path: Path, year: int) -> PaperResult:
        """Call Gemini API with exponential backoff retry.
        
        On 429 RESOURCE_EXHAUSTED errors, automatically rotates to the next
        API key before retrying.
        
        Args:
            uploaded_file: The uploaded PDF file object.
            prompt: The extraction prompt.
            pdf_path: Path to the original PDF.
            year: Publication year.
        
        Returns:
            Validated PaperResult.
        
        Raises:
            Exception: If all retries are exhausted.
        """
        last_exception = None
        
        try:
            for attempt in range(1, self.settings.MAX_RETRIES + 1):
                try:
                    self._rate_limit_wait()
                    
                    response = self.client.models.generate_content(
                        model=self.settings.MODEL_NAME,
                        contents=[
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_uri(
                                        file_uri=uploaded_file.uri,
                                        mime_type="application/pdf",
                                    ),
                                    types.Part.from_text(text=prompt),
                                ],
                            )
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            response_mime_type="application/json",
                            response_schema=PaperResult,
                            temperature=self.settings.TEMPERATURE,
                        ),
                    )
                    
                    # Use the SDK's built-in parsed response
                    if response.parsed:
                        return response.parsed
                    
                    # Fallback: manually parse if .parsed is None
                    if response.text:
                        result = PaperResult.model_validate_json(response.text)
                        return result
                    
                    raise ValueError(f"Empty response from Gemini for {pdf_path.name}")
                    
                except Exception as e:
                    last_exception = e
                    error_str = str(e)
                    
                    # On 429 (rate limit), rotate key and retry
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        logger.warning(f"Rate limited on key {self._current_key_index + 1} for {pdf_path.name}. Rotating key...")
                        # Clean up old uploaded file
                        try:
                            self.cleanup_uploaded_file(uploaded_file.name)
                        except Exception:
                            pass
                            
                        self.rotate_key(reason="429 rate limit")
                        # Re-upload the file with the new client
                        try:
                            uploaded_file = self._upload_pdf(pdf_path)
                        except Exception as upload_err:
                            logger.error(f"Failed to re-upload {pdf_path.name} after key rotation: {upload_err}")
                        
                        wait_time = random.uniform(5, 15)
                        logger.info(f"Waiting {wait_time:.1f}s after key rotation...")
                        time.sleep(wait_time)
                        continue
                    
                    # Handle file reference invalidation (403/404)
                    is_file_access_error = ("403" in error_str or "404" in error_str) and (
                        "File" in error_str or 
                        "permission" in error_str or 
                        "exist" in error_str or 
                        "not found" in error_str.lower()
                    )
                    if is_file_access_error:
                        logger.warning(
                            f"File reference invalid (403/404) for {pdf_path.name} "
                            f"(error: {error_str}). Re-uploading and retrying..."
                        )
                        try:
                            self.cleanup_uploaded_file(uploaded_file.name)
                        except Exception:
                            pass
                        try:
                            uploaded_file = self._upload_pdf(pdf_path)
                        except Exception as upload_err:
                            logger.error(f"Failed to re-upload {pdf_path.name}: {upload_err}")
                        
                        wait_time = random.uniform(2, 5)
                        time.sleep(wait_time)
                        continue
                    
                    # Don't retry on non-transient errors
                    if "400" in error_str or "403" in error_str or "404" in error_str:
                        logger.error(f"Non-retryable error for {pdf_path.name}: {e}")
                        raise
                    
                    if attempt < self.settings.MAX_RETRIES:
                        wait_time = (self.settings.RETRY_BASE_DELAY ** attempt) + random.uniform(0, 1)
                        logger.warning(
                            f"Attempt {attempt}/{self.settings.MAX_RETRIES} failed for {pdf_path.name}: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {self.settings.MAX_RETRIES} attempts failed for {pdf_path.name}: {e}")
            
            raise last_exception
        finally:
            # Clean up the final uploaded file
            try:
                self.cleanup_uploaded_file(uploaded_file.name)
            except Exception:
                pass

    def cleanup_uploaded_file(self, file_name: str) -> None:
        """Delete an uploaded file from the Gemini File API.
        
        Args:
            file_name: The name of the uploaded file to delete.
        """
        try:
            self.client.files.delete(name=file_name)
            logger.debug(f"Deleted uploaded file: {file_name}")
        except Exception as e:
            logger.warning(f"Failed to delete uploaded file {file_name}: {e}")

