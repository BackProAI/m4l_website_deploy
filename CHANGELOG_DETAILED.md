# Detailed Change Log (A3 OCR Updates)

## Overview
This document describes the exact code changes made to add hybrid OCR behavior, document-mode detection, diagonal strike-through handling, and the model switch to `gpt-4.1`.

## Files Changed
- [sectioned_gpt4o_ocr.py](sectioned_gpt4o_ocr.py)
- [requirements.txt](requirements.txt)
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

---

## [sectioned_gpt4o_ocr.py](sectioned_gpt4o_ocr.py)

### 1) New dependencies and imports
Added OpenCV and NumPy for diagonal strike-through detection.

```python
import cv2
import numpy as np
```

### 2) New document-mode detection (handwriting-only vs hybrid)
Added a document-level classifier that inspects up to two pages and returns:
- `mode`: `handwriting_only` or `hybrid`
- `confidence`: `high` | `medium` | `low`
- `reason`: short model-provided explanation

New methods:
- `detect_document_mode(page_images)`
- `_prepare_classification_image(image, max_side=1600)`

Behavior:
- Uses low-detail image inputs for classification to keep it fast.
- Defaults to `hybrid` on low confidence.

### 3) Hybrid extraction prompt
Added a new hybrid extraction path for sections with printed text + handwritten corrections.

New method:
- `extract_text_from_section_hybrid(section_image, section_name)`

Hybrid prompt rules implemented:
- Straight line strike-through removes only the struck words.
- Diagonal strike-through across a line/dotpoint removes the whole line.
- Arrows or handwritten notes replace printed text.
- Handwritten bullet/dash items are appended beneath the relevant printed line.

### 4) Diagonal strike-through detection (CV-based)
Added a section-level diagonal line detector to override hybrid extraction when strong diagonals are present.

New method:
- `detect_diagonal_strike_through(section_image)`

Algorithm:
- Convert section image to grayscale.
- Edge detect (Canny).
- Hough line detection in two passes (strict then relaxed).
- Detect diagonal lines within a center region to avoid border artifacts.

If diagonals are detected:
- Printed text is excluded.
- Handwriting-only extraction is used for that section.

### 5) Section processing routing
Updated `process_page_sections()` to route per section based on:
- Document mode (`handwriting_only` vs `hybrid`)
- Diagonal strike-through detection (only in hybrid mode)

Flow:
- `handwriting_only` -> `extract_text_from_section()`
- `hybrid` + diagonals -> `extract_text_from_section()`
- `hybrid` + no diagonals -> `extract_text_from_section_hybrid()`

### 6) Document processing flow changes
Updated `process_document()` to:
- Run document-mode detection once per document (PDF or image).
- Log the detected mode and confidence.
- Pass `document_mode` to `process_page_sections()`.
- Include `document_mode` and `document_mode_confidence` in the returned result dict.

### 7) Vision model switch to `gpt-4.1`
All vision payloads in the A3 flow were switched from `gpt-4o` to `gpt-4.1`, including:
- Section extraction (handwriting-only)
- Hybrid extraction
- Document-mode detection
- Page quick text extraction
- Layout analysis

---

## [requirements.txt](requirements.txt)

### Added dependency
```text
opencv-python>=4.10.0
```
Purpose: enables diagonal strike-through detection via OpenCV.

---

## [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

Added a full implementation plan documenting:
- The two-mode OCR strategy
- Hybrid behavior rules (straight vs diagonal strike-through)
- Document-level detection
- Test plan and risks

---

## Dependency Summary
To match this update in another project, install:
- `opencv-python>=4.10.0`

The rest of the dependencies remain unchanged.

---

## Notes for Porting to Another Project
Minimum changes to replicate behavior:
- Copy the new/updated methods from [sectioned_gpt4o_ocr.py](sectioned_gpt4o_ocr.py):
  - `detect_document_mode`
  - `_prepare_classification_image`
  - `extract_text_from_section_hybrid`
  - `detect_diagonal_strike_through`
- Update `process_page_sections()` routing to use these methods.
- Update `process_document()` to detect and log document mode and pass it through.
- Ensure `opencv-python` and `numpy` are installed.
- Switch model payloads to `gpt-4.1`.

---

## Code Diff (This Chat Only)

This section includes the exact diff hunks for only the files changed in this chat.

### Diff: [requirements.txt](requirements.txt)

```diff
@@ -6,6 +6,7 @@
 # Core Image & PDF Processing
 Pillow>=10.0.0              # Image processing and manipulation
 PyMuPDF>=1.23.0             # PDF processing and form field handling
+opencv-python>=4.10.0       # Diagonal strike-through detection
```

### Diff: [sectioned_gpt4o_ocr.py](sectioned_gpt4o_ocr.py)

#### 1) Added OpenCV / NumPy imports

```diff
@@ -13,6 +13,8 @@
 from PIL import Image
 import requests
 from typing import Dict, List, Any, Tuple
 import fitz  # PyMuPDF
+import cv2
+import numpy as np
```

#### 2) Added diagonal strike-through detection

```diff
@@ -211,6 +213,63 @@ class SectionedGPT4oOCR:
         return cropped
+
+    def detect_diagonal_strike_through(self, section_image: Image.Image) -> bool:
+        """Detect diagonal strike-through lines in a section image."""
+        image_array = np.array(section_image)
+
+        if image_array.ndim == 3:
+            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
+        else:
+            gray = image_array
+
+        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
+        edges = cv2.Canny(blurred, 40, 120)
+
+        height, width = edges.shape
+        diag_len = (width ** 2 + height ** 2) ** 0.5
+
+        # Two-pass detection: strict then relaxed
+        passes = [
+            {"min_ratio": 0.25, "threshold": 60, "max_gap": 18},
+            {"min_ratio": 0.18, "threshold": 45, "max_gap": 25}
+        ]
+
+        for params in passes:
+            min_line_length = max(35, int(diag_len * params["min_ratio"]))
+
+            lines = cv2.HoughLinesP(
+                edges,
+                rho=1,
+                theta=np.pi / 180,
+                threshold=params["threshold"],
+                minLineLength=min_line_length,
+                maxLineGap=params["max_gap"]
+            )
+
+            if lines is None:
+                continue
+
+            for line in lines:
+                x1, y1, x2, y2 = line[0]
+                dx = x2 - x1
+                dy = y2 - y1
+                length = (dx ** 2 + dy ** 2) ** 0.5
+                if length < min_line_length:
+                    continue
+
+                angle = abs(np.degrees(np.arctan2(dy, dx))) % 180
+                if not ((20 <= angle <= 70) or (110 <= angle <= 160)):
+                    continue
+
+                mid_x = (x1 + x2) / 2
+                mid_y = (y1 + y2) / 2
+                if not (0.15 * width <= mid_x <= 0.85 * width and 0.15 * height <= mid_y <= 0.85 * height):
+                    continue
+
+                return True
+
+        return False
```

#### 3) Switched vision model from `gpt-4o` to `gpt-4.1` (section extraction)

```diff
@@ -243,7 +302,7 @@
         # API payload - simple text response
         payload = {
-            "model": "gpt-4o",
+            "model": "gpt-4.1",
```

#### 4) Added hybrid section extraction prompt

```diff
@@ -301,8 +360,178 @@
             }
+
+    def extract_text_from_section_hybrid(self, section_image: Image.Image, section_name: str) -> Dict[str, Any]:
+        """Extract final corrected text from a hybrid section using GPT-4o."""
+        print(f"   🔍 Processing section (hybrid): {section_name}")
+
+        # Encode image
+        base64_image = self.encode_image(section_image)
+
+        # Create prompt for hybrid printed + handwritten corrections
+        prompt = f"""You are an expert OCR system. This section contains printed text and handwritten corrections.
+
+TASK: Return the final corrected text for this section.
+
+CRITICAL INSTRUCTIONS:
+1. **PRINTED TEXT BASELINE**: Start from the printed text as the base.
+2. **STRAIGHT LINE STRIKE-THROUGH**: If a straight line strikes through specific words, delete only those words.
+3. **DIAGONAL STRIKE-THROUGH**: If diagonal lines cross an entire line, dotpoint, or paragraph, omit that entire line/paragraph.
+4. **ARROWS & REPLACEMENTS**: If arrows or handwritten notes indicate a replacement, replace the printed text with the handwritten correction.
+5. **HANDWRITTEN ADDITIONS**: If a handwritten dash or bullet continues a list, add that handwritten line beneath the related printed line.
+6. **NO HALLUCINATION**: Only include text that is visible in the image.
+7. **PRESERVE STRUCTURE**: Keep line breaks and list formatting consistent with the section.
+
+Return the corrected text directly, no JSON formatting needed. If nothing should remain after applying corrections, return "NO_TEXT_FOUND".
+"""
+
+        payload = {
+            "model": "gpt-4.1",
+            "messages": [
+                {
+                    "role": "user",
+                    "content": [
+                        {"type": "text", "text": prompt},
+                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
+                    ]
+                }
+            ],
+            "max_tokens": 500,
+            "temperature": 0
+        }
+        ...
```

#### 5) Added document-level mode detection and classification helper

```diff
+    def _prepare_classification_image(self, image: Image.Image, max_side: int = 1600) -> Image.Image:
+        """Downscale images for document-level mode classification."""
+        max_dim = max(image.width, image.height)
+        if max_dim <= max_side:
+            return image
+
+        scale = max_side / max_dim
+        new_size = (int(image.width * scale), int(image.height * scale))
+        return image.resize(new_size, Image.Resampling.LANCZOS)
+
+    def detect_document_mode(self, page_images: List[Image.Image]) -> Dict[str, Any]:
+        """Detect whether the document is handwriting-only or hybrid printed with corrections."""
+        if not page_images:
+            return {"mode": "hybrid", "confidence": "low", "reason": "no_images"}
+        ...
+        payload = {
+            "model": "gpt-4.1",
+            "messages": [
+                {
+                    "role": "user",
+                    "content": content
+                }
+            ],
+            "max_tokens": 200,
+            "temperature": 0
+        }
+        ...
```

#### 6) Updated per-section routing for hybrid + diagonal strike-throughs

```diff
@@ -332,7 +561,15 @@
-            extraction_result = self.extract_text_from_section(section_image, section_name)
+            if document_mode == "hybrid":
+                has_diagonal = self.detect_diagonal_strike_through(section_image)
+                if has_diagonal:
+                    print("       ↘️ Detected diagonal strike-through; extracting handwriting only")
+                    extraction_result = self.extract_text_from_section(section_image, section_name)
+                else:
+                    extraction_result = self.extract_text_from_section_hybrid(section_image, section_name)
+            else:
+                extraction_result = self.extract_text_from_section(section_image, section_name)
```

#### 7) Switched remaining vision model payloads to `gpt-4.1`

```diff
@@ -593,7 +830,7 @@
-        payload = {
-            "model": "gpt-4o",
+        payload = {
+            "model": "gpt-4.1",
@@ -623,7 +860,7 @@
-        payload = {
-            "model": "gpt-4o",
+        payload = {
+            "model": "gpt-4.1",
```

#### 8) Document-level mode use in `process_document()`

```diff
@@ -663,12 +900,35 @@
         try:
             total_start_time = time.time()
             all_results = []
+            document_mode = "hybrid"
+            mode_confidence = "low"
@@
                 pdf_doc = fitz.open(document_path)
+
+                # Detect document mode using low-res images from both pages
+                try:
+                    import io
+                    classification_images = []
+                    for page_index in range(min(2, len(pdf_doc))):
+                        page = pdf_doc[page_index]
+                        mat = fitz.Matrix(1.0, 1.0)
+                        pix = page.get_pixmap(matrix=mat)
+                        img_data = pix.tobytes("png")
+                        page_image = Image.open(io.BytesIO(img_data))
+                        classification_images.append(page_image)
+
+                    mode_info = self.detect_document_mode(classification_images)
+                    document_mode = mode_info.get("mode", "hybrid")
+                    mode_confidence = mode_info.get("confidence", "low")
+                    print(f"🔎 Document mode: {document_mode} (confidence: {mode_confidence})")
+                except Exception as e:
+                    print(f"⚠️ Document mode detection error: {e}")
+                    document_mode = "hybrid"
+                    mode_confidence = "low"
@@
-                    page_results = self.process_page_sections(page_image, logical_page_num + 1)
+                    page_results = self.process_page_sections(page_image, logical_page_num + 1, document_mode)
@@
                 with Image.open(document_path) as img:
                     if img.mode != "RGB":
                         img = img.convert("RGB")
+
+                    # Detect document mode for single image
+                    mode_info = self.detect_document_mode([img])
+                    document_mode = mode_info.get("mode", "hybrid")
+                    mode_confidence = mode_info.get("confidence", "low")
+                    print(f"🔎 Document mode: {document_mode} (confidence: {mode_confidence})")
@@
-                    page_results = self.process_page_sections(img, 1)
+                    page_results = self.process_page_sections(img, 1, document_mode)
@@
             return {
                 "success": True,
                 "file_name": document_path.name,
+                "document_mode": document_mode,
+                "document_mode_confidence": mode_confidence,
```

---

## New files (entire files added in this chat)

### [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

This file was created from scratch. The full content was added in this chat.

### [CHANGELOG_DETAILED.md](CHANGELOG_DETAILED.md)

This file was created from scratch. The full content was added in this chat.
