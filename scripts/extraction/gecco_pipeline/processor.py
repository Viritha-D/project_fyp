"""Batch processor for orchestrating the GECCO extraction pipeline."""

import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from tqdm import tqdm
from loguru import logger

from gecco_pipeline.config import Settings
from gecco_pipeline.extractor import GeccoExtractor
from gecco_pipeline.utils import (
    discover_pdfs,
    get_output_path,
    is_already_processed,
    save_result,
)


@dataclass
class ProcessingStats:
    """Tracks processing statistics across the batch run."""
    total_discovered: int = 0
    total_skipped: int = 0
    total_processed: int = 0
    total_failed: int = 0
    total_extractions: int = 0
    failed_files: List[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0

    def summary(self) -> Dict[str, Any]:
        """Return a summary dictionary."""
        return {
            "total_discovered": self.total_discovered,
            "total_skipped": self.total_skipped,
            "total_processed": self.total_processed,
            "total_failed": self.total_failed,
            "total_extractions": self.total_extractions,
            "failed_files": self.failed_files,
            "processing_time_seconds": round(self.processing_time_seconds, 2),
        }


class BatchProcessor:
    """Orchestrates batch processing of GECCO paper PDFs."""

    def __init__(self, settings: Settings):
        """Initialize the batch processor.
        
        Args:
            settings: Pipeline configuration.
        """
        self.settings = settings
        self.extractor = GeccoExtractor(settings)
        logger.info("BatchProcessor initialized")

    def _process_pdf(self, pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
        """Process a PDF (splitting if it exceeds page limits), saves, and returns the result dict.
        
        Args:
            pdf_path: Path to the PDF file.
            output_dir: Base output directory.
            
        Returns:
            The extraction result dictionary.
        """
        temp_dir = output_dir / "tmp_split"
        split_paths = []
        
        try:
            # Check page count
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            # Conservative page threshold
            max_pages = 200
            
            if num_pages <= max_pages:
                result = self.extractor.extract_from_pdf(pdf_path)
                result_dict = result.model_dump(mode="json")
            else:
                logger.info(f"PDF {pdf_path.name} has {num_pages} pages, which exceeds the limit of {max_pages}. Splitting...")
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                # Split pages
                from pypdf import PdfWriter
                for start_idx in range(0, num_pages, max_pages):
                    end_idx = min(start_idx + max_pages, num_pages)
                    writer = PdfWriter()
                    for page_idx in range(start_idx, end_idx):
                        writer.add_page(reader.pages[page_idx])
                        
                    part_name = f"{pdf_path.stem}_part{start_idx//max_pages + 1}.pdf"
                    part_path = temp_dir / part_name
                    
                    with open(part_path, "wb") as f:
                        writer.write(f)
                        
                    logger.info(f"Created split part: {part_name} (pages {start_idx+1} to {end_idx})")
                    split_paths.append(part_path)
                
                # Process parts
                logger.info(f"Processing {len(split_paths)} parts for {pdf_path.name}...")
                merged_extractions = []
                first_result = None
                
                for part_path in split_paths:
                    part_result = self.extractor.extract_from_pdf(part_path)
                    if first_result is None:
                        first_result = part_result
                    merged_extractions.extend(part_result.extractions)
                    
                    # Short pause to prevent overwhelming the API
                    time.sleep(10.0)
                
                # Merge the results
                first_result.extractions = merged_extractions
                first_result.metadata.source_file = pdf_path.name
                result_dict = first_result.model_dump(mode="json")
            
            # Save output
            output_path = get_output_path(pdf_path, output_dir)
            save_result(result_dict, output_path)
            
            return result_dict
            
        finally:
            # Clean up split files
            if split_paths:
                for part_path in split_paths:
                    try:
                        if part_path.exists():
                            part_path.unlink()
                            logger.debug(f"Cleaned up temp split file: {part_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete temp split file {part_path.name}: {e}")
                try:
                    if temp_dir.exists() and not any(temp_dir.iterdir()):
                        temp_dir.rmdir()
                except Exception:
                    pass

    def process_single(self, pdf_path: Path, output_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """Process a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            output_dir: Output directory (defaults to settings.OUTPUT_DIR).
        
        Returns:
            Extraction result dictionary, or None if processing failed.
        """
        output_dir = output_dir or self.settings.OUTPUT_DIR
        
        if not pdf_path.exists():
            logger.error(f"PDF not found: {pdf_path}")
            return None
        
        try:
            return self._process_pdf(pdf_path, output_dir)
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            return None

    def _load_checkpoint(self, checkpoint_path: Path) -> set:
        """Load the set of already-processed PDF paths from a checkpoint file.
        
        Args:
            checkpoint_path: Path to the checkpoint JSON file.
        
        Returns:
            Set of PDF path strings that have been completed.
        """
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                completed = set(data.get("completed", []))
                logger.info(f"Loaded checkpoint: {len(completed)} papers already completed")
                return completed
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")
        return set()

    def _save_checkpoint(self, checkpoint_path: Path, completed: set) -> None:
        """Save the set of completed PDF paths to a checkpoint file.
        
        Args:
            checkpoint_path: Path to the checkpoint JSON file.
            completed: Set of completed PDF path strings.
        """
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({"completed": sorted(completed)}, f, indent=2)

    def process_batch(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        year: Optional[int] = None,
        skip_existing: bool = True,
        dry_run: bool = False,
    ) -> ProcessingStats:
        """Process a batch of PDF files with rate limiting and cooldowns.
        
        Features:
        - Inter-batch cooldown pauses every BATCH_SIZE papers
        - Checkpoint/resume: saves progress to _checkpoint.json
        - Enhanced progress logging with key rotation info
        
        Args:
            input_dir: Directory containing PDF files.
            output_dir: Output directory (defaults to settings.OUTPUT_DIR).
            year: If specified, only process PDFs from this year.
            skip_existing: Skip PDFs that already have output files.
            dry_run: If True, discover files but don't process them.
        
        Returns:
            ProcessingStats with batch statistics.
        """
        output_dir = output_dir or self.settings.OUTPUT_DIR
        stats = ProcessingStats()
        start_time = time.time()
        
        # Discover PDFs
        pdfs = discover_pdfs(input_dir, year)
        stats.total_discovered = len(pdfs)
        
        if not pdfs:
            logger.warning("No PDF files found to process.")
            return stats
        
        # Load checkpoint for resume capability
        checkpoint_path = output_dir / "_checkpoint.json"
        completed_set = self._load_checkpoint(checkpoint_path)
        
        # Filter already processed (both by output file existence AND checkpoint)
        if skip_existing:
            pending_pdfs = [
                p for p in pdfs
                if not is_already_processed(p, output_dir) and str(p) not in completed_set
            ]
            stats.total_skipped = len(pdfs) - len(pending_pdfs)
            if stats.total_skipped > 0:
                logger.info(f"Skipping {stats.total_skipped} already-processed PDFs")
        else:
            pending_pdfs = [p for p in pdfs if str(p) not in completed_set]
        
        if dry_run:
            logger.info(f"[DRY RUN] Would process {len(pending_pdfs)} PDFs")
            for pdf in pending_pdfs:
                logger.info(f"  → {pdf.name}")
            stats.processing_time_seconds = time.time() - start_time
            return stats
        
        if not pending_pdfs:
            logger.info("All PDFs already processed. Nothing to do.")
            stats.processing_time_seconds = time.time() - start_time
            return stats
        
        logger.info(f"Processing {len(pending_pdfs)} PDFs...")
        logger.info(
            f"Batch config: size={self.settings.BATCH_SIZE}, "
            f"cooldown={self.settings.BATCH_COOLDOWN_SECONDS}s, "
            f"RPM={self.settings.RATE_LIMIT_RPM}, "
            f"keys={len(self.settings.api_keys)}"
        )
        
        batch_count = 0  # tracks position within current batch
        
        # Process sequentially with progress bar
        with tqdm(total=len(pending_pdfs), desc="Extracting papers", unit="paper") as pbar:
            for i, pdf_path in enumerate(pending_pdfs):
                try:
                    result_dict = self._process_pdf(pdf_path, output_dir)
                    
                    stats.total_processed += 1
                    stats.total_extractions += len(result_dict.get("extractions", []))
                    
                    # Update checkpoint
                    completed_set.add(str(pdf_path))
                    self._save_checkpoint(checkpoint_path, completed_set)
                    
                    pbar.set_postfix(
                        ok=stats.total_processed,
                        fail=stats.total_failed,
                        entries=stats.total_extractions,
                    )
                    
                except Exception as e:
                    stats.total_failed += 1
                    stats.failed_files.append(str(pdf_path))
                    logger.error(f"Failed: {pdf_path.name} - {e}")
                    
                    # Still save checkpoint on failure so we don't retry endlessly
                    # (the file won't be in completed_set, but output won't exist either,
                    #  so skip_existing handles it. Only truly broken files retry.)
                
                pbar.update(1)
                batch_count += 1
                
                # Inter-batch cooldown
                remaining = len(pending_pdfs) - (i + 1)
                if batch_count >= self.settings.BATCH_SIZE and remaining > 0:
                    cooldown = self.settings.BATCH_COOLDOWN_SECONDS
                    logger.info(
                        f"\n[Pause]  Batch cooldown: pausing {cooldown}s after {batch_count} papers "
                        f"({remaining} remaining)..."
                    )
                    time.sleep(cooldown)
                    batch_count = 0
        
        stats.processing_time_seconds = time.time() - start_time
        
        # Print summary
        self._print_batch_summary(stats)
        
        # Save processing report
        self._save_processing_report(stats, output_dir)
        
        return stats

    def _print_batch_summary(self, stats: ProcessingStats) -> None:
        """Print a formatted summary of batch processing results."""
        print("\n" + "=" * 60)
        print("  GECCO Extraction Pipeline — Batch Summary")
        print("=" * 60)
        print(f"  PDFs discovered:   {stats.total_discovered}")
        print(f"  Skipped (cached):  {stats.total_skipped}")
        print(f"  Processed:         {stats.total_processed}")
        print(f"  Failed:            {stats.total_failed}")
        print(f"  Total extractions: {stats.total_extractions}")
        print(f"  Time elapsed:      {stats.processing_time_seconds:.1f}s")
        
        if stats.total_processed > 0:
            avg_time = stats.processing_time_seconds / stats.total_processed
            print(f"  Avg time/paper:    {avg_time:.1f}s")
        
        if stats.failed_files:
            print(f"\n  ! Failed files:")
            for f in stats.failed_files[:10]:
                print(f"    - {Path(f).name}")
            if len(stats.failed_files) > 10:
                print(f"    ... and {len(stats.failed_files) - 10} more")
        
        print("=" * 60 + "\n")

    def _save_processing_report(self, stats: ProcessingStats, output_dir: Path) -> None:
        """Save processing stats as a JSON report."""
        report_dir = self.settings.REPORTS_DIR
        report_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import datetime
        report_path = report_dir / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, "w") as f:
            json.dump(stats.summary(), f, indent=2)
        
        logger.info(f"Processing report saved to {report_path}")

