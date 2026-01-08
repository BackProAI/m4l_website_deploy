"""
Post Review Document Processing System

A comprehensive system for processing handwritten annotations on PDF documents
and applying changes to Word documents using GPT-4o vision analysis.
"""

__version__ = "1.0.0"
__author__ = "Post Review Team"

from .core.master_unified_processor import MasterUnifiedProcessor
from .ui.post_review_modern_ui import ModernPostReviewProcessor

__all__ = ["MasterUnifiedProcessor", "ModernPostReviewProcessor"]
