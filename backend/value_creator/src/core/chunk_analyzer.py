#!/usr/bin/env python3
"""
GPT-4o Chunk Analyzer
Uses OpenAI's GPT-4o to analyze document chunks for various markings and annotations
"""

import base64
import io
import logging
from typing import Dict, List, Optional, Any
import openai
from PIL import Image
import numpy as np
import os
from dotenv import load_dotenv

# FORCE RELOAD ENVIRONMENT VARIABLES
load_dotenv(override=True)

class ChunkAnalyzer:
    """Analyzes document chunks using GPT-4o vision capabilities"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI client - use environment variable or config
        api_key = os.getenv('OPENAI_API_KEY') or config.get('openai', {}).get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment or config")
        
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        
        self.model = config['openai']['model']
        self.max_tokens = config['openai']['max_tokens']
        self.temperature = config['openai']['temperature']
        
        # Analysis settings
        self.detect_handwriting = config['analysis']['detect_handwriting']
        self.detect_strikethrough = config['analysis']['detect_strikethrough']
        self.detect_crosses = config['analysis']['detect_crosses']
        self.detect_highlighting = config['analysis']['detect_highlighting']
        self.detect_annotations = config['analysis']['detect_annotations']
        self.confidence_threshold = config['analysis']['confidence_threshold']
    
    def analyze_chunk(self, chunk: Dict) -> Dict:
        """
        Analyze a single document chunk using GPT-4o
        
        Args:
            chunk: Chunk dictionary with image data and metadata
            
        Returns:
            Dictionary with detected items and their properties
        """
        try:
            # Convert chunk image to base64
            image_b64 = self._image_to_base64(chunk["image"])
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt()
            
            # Log the API call
            self.logger.debug(f"Sending chunk {chunk['chunk_id']} to GPT-4o (model: {self.model})")
            self.logger.debug(f"Image size: {len(image_b64)} characters")
            
            # Call GPT-4o
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert document analyzer. Analyze the provided image chunk and identify various markings and annotations with high precision."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Log the response
            response_text = response.choices[0].message.content
            self.logger.debug(f"GPT-4o response for chunk {chunk['chunk_id']}: {response_text[:200]}...")
            
            # Parse response
            analysis_result = self._parse_gpt_response(response.choices[0].message.content)
            
            # Add metadata
            analysis_result["chunk_metadata"] = {
                "chunk_id": chunk["chunk_id"],
                "position": chunk["position"],
                "analysis_model": self.model,
                "confidence_threshold": self.confidence_threshold
            }
            
            self.logger.debug(f"Analyzed chunk {chunk['chunk_id']}: {len(analysis_result.get('detections', []))} items found")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing chunk {chunk.get('chunk_id', 'unknown')}: {str(e)}")
            return {
                "error": str(e),
                "chunk_id": chunk.get("chunk_id", "unknown"),
                "handwritten_text": [],
                "strikethrough_text": [],
                "crosses": [],
                "highlights": [],
                "annotations": []
            }
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert numpy image array to base64 string"""
        # Convert to PIL Image
        if len(image.shape) == 3:
            pil_image = Image.fromarray(image.astype('uint8'))
        else:
            pil_image = Image.fromarray(image.astype('uint8'), mode='L')
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def _create_analysis_prompt(self) -> str:
        """Create the analysis prompt for GPT-4o"""
        
        detection_items = []
        if self.detect_handwriting:
            detection_items.append("- Handwritten text (cursive, printed, notes, signatures, corrections)")
        if self.detect_strikethrough:
            detection_items.append("- Strikethrough text (crossed out words or lines, deletions)")
        if self.detect_crosses:
            detection_items.append("- Cross marks or X marks (small item deletions, large section deletions)")
        if self.detect_highlighting:
            detection_items.append("- Highlighted text (yellow, colored backgrounds)")
        if self.detect_annotations:
            detection_items.append("- Annotations (margin notes, arrows, circles, underlines, connecting lines)")
        
        prompt = f"""
Analyze this document image chunk and detect the following items with special attention to RELATIONSHIPS between markings:

{chr(10).join(detection_items)}

SPECIAL INSTRUCTIONS FOR BULLET POINT SECTIONS:
- If you see bullet points () with handwritten text, group ALL continuous handwritten text that belongs to the SAME bullet point into a SINGLE detection
- Multiple lines under the same bullet point should be combined into ONE handwritten_text entry
- Look for visual spacing and alignment to determine where one bullet point ends and the next begins
- Each bullet point should result in ONE complete handwritten_text detection, not multiple separate detections

Pay special attention to:
1. ARROWS pointing from one element to another (handwriting to text, cross to correction, etc.)
2. PROXIMITY relationships (handwriting near strikethrough suggests replacement)
3. SIZE of crosses/marks (large diagonal lines = delete whole section, small crosses = delete item)
4. CONNECTING LINES between annotations and text
5. BULLET POINT GROUPING: Combine all text lines that belong to the same bullet point

For each detected item, provide:
1. Type of marking (handwritten_text, strikethrough_text, cross, highlight, annotation, arrow)
2. Text content (if readable) - FOR BULLET POINTS: Include ALL text lines that belong to the same bullet point
3. Approximate position (x, y coordinates as percentages of image)
4. Size estimation (small, medium, large) for crosses and marks
5. Confidence level (0.0 to 1.0)
6. Description of the item and its relationship to nearby elements
7. Color (if applicable)
8. Connected_to: if this item points to or relates to another item

Respond in JSON format:
{{
    "handwritten_text": [
        {{
            "text": "Complete bullet point text including all lines that belong to this bullet point, combined into one continuous text entry",
            "position": {{"x": 0.2, "y": 0.3}},
            "confidence": 0.9,
            "description": "complete handwritten bullet point content with multiple lines combined",
            "color": "black",
            "connected_to": "bullet point marker",
            "relationship_type": "bullet_content"
        }}
    ],
    "strikethrough_text": [
        {{
            "text": "crossed out text",
            "position": {{"x": 0.5, "y": 0.4}},
            "confidence": 0.8,
            "description": "single line through text",
            "has_replacement": true
        }}
    ],
    "crosses": [
        {{
            "position": {{"x": 0.1, "y": 0.2}},
            "confidence": 0.9,
            "description": "large diagonal cross through paragraph",
            "size": "large",
            "deletion_scope": "paragraph"
        }}
    ],
    "arrows": [
        {{
            "start_position": {{"x": 0.2, "y": 0.3}},
            "end_position": {{"x": 0.5, "y": 0.4}},
            "confidence": 0.8,
            "description": "arrow from handwriting to strikethrough text",
            "connects": ["handwritten_text", "strikethrough_text"]
        }}
    ],
    "highlights": [
        {{
            "text": "highlighted text",
            "position": {{"x": 0.3, "y": 0.6}},
            "confidence": 0.7,
            "description": "yellow highlighting",
            "color": "yellow"
        }}
    ],
    "annotations": [
        {{
            "text": "margin note",
            "position": {{"x": 0.8, "y": 0.5}},
            "confidence": 0.8,
            "description": "handwritten note in right margin",
            "type": "margin_note",
            "points_to_text": true
        }}
    ]
}}

CRITICAL: Look for RELATIONSHIPS between markings:
- Handwriting near strikethrough = replacement
- Arrows connecting elements = directed relationships  
- Large crosses/diagonal lines = delete entire section
- Small crosses = delete specific item
- Proximity matters for determining intent
- BULLET POINTS: Group all handwritten text under the same bullet into ONE detection

BULLET POINT RULE: If you see multiple lines of handwritten text under the same bullet point (), combine them into a SINGLE handwritten_text entry. Do NOT create separate entries for each line. Look at the visual alignment and spacing to determine bullet point boundaries.

Only include items with confidence above {self.confidence_threshold}. Be precise and conservative in your detections.
"""
        
        return prompt
    
    def _parse_gpt_response(self, response_text: str) -> Dict:
        """Parse GPT-4o response into structured data"""
        try:
            import json
            import re
            
            # Clean the response text to extract JSON
            clean_text = response_text.strip()
            
            # If it's wrapped in markdown code blocks, extract the content
            json_block_match = re.search(r'```json\s*(.*?)\s*```', clean_text, re.DOTALL)
            if json_block_match:
                clean_text = json_block_match.group(1).strip()
            
            # Try to parse as JSON
            parsed = json.loads(clean_text)
            
            # Validate structure
            result = {
                "handwritten_text": parsed.get("handwritten_text", []),
                "strikethrough_text": parsed.get("strikethrough_text", []),
                "crosses": parsed.get("crosses", []),
                "arrows": parsed.get("arrows", []),
                "highlights": parsed.get("highlights", []),
                "annotations": parsed.get("annotations", [])
            }
            
            # Filter by confidence threshold
            for category in result:
                result[category] = [
                    item for item in result[category] 
                    if item.get("confidence", 0.0) >= self.confidence_threshold
                ]
            
            return result
            
        except json.JSONDecodeError as e:
            # The response likely contains markdown formatting, extract the JSON
            try:
                # First, try to extract JSON from markdown code blocks
                import re
                
                # Look for ```json ... ``` blocks
                json_block_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_block_match:
                    json_text = json_block_match.group(1).strip()
                    result = json.loads(json_text)
                    return result
                
                # If no markdown blocks, look for any JSON object
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_text = json_match.group()
                    result = json.loads(json_text)
                    return result
                    
            except Exception as extraction_error:
                self.logger.warning(f"Could not extract JSON from response: {extraction_error}")
                self.logger.debug(f"Response text (first 200 chars): {response_text[:200]}...")
            
            # Fallback: try to extract information using text parsing
            return self._fallback_parse_response(response_text)
    
    def _fallback_parse_response(self, response_text: str) -> Dict:
        """Fallback parsing when JSON parsing fails"""
        self.logger.warning("Using fallback response parsing")
        
        # Return empty but properly structured result to avoid errors
        result = {
            "handwritten_text": [],
            "strikethrough_text": [],
            "crosses": [],
            "highlights": [],
            "annotations": [],
            "arrows": []
        }
        
        # Look for mentions of different types
        lines = response_text.lower().split('\n')
        
        for line in lines:
            if 'handwritten' in line or 'handwriting' in line:
                result["handwritten_text"].append({
                    "text": "detected handwriting",
                    "position": {"x": 0.5, "y": 0.5},
                    "confidence": 0.6,
                    "description": line.strip()
                })
            elif 'strikethrough' in line or 'crossed out' in line:
                result["strikethrough_text"].append({
                    "text": "strikethrough detected",
                    "position": {"x": 0.5, "y": 0.5},
                    "confidence": 0.6,
                    "description": line.strip()
                })
            elif 'cross' in line or 'x mark' in line:
                result["crosses"].append({
                    "position": {"x": 0.5, "y": 0.5},
                    "confidence": 0.6,
                    "description": line.strip()
                })
            elif 'highlight' in line:
                result["highlights"].append({
                    "text": "highlighted text",
                    "position": {"x": 0.5, "y": 0.5},
                    "confidence": 0.6,
                    "description": line.strip()
                })
            elif 'annotation' in line or 'note' in line:
                result["annotations"].append({
                    "text": "annotation detected",
                    "position": {"x": 0.5, "y": 0.5},
                    "confidence": 0.6,
                    "description": line.strip()
                })
        
        return result
    
    def batch_analyze(self, chunks: List[Dict]) -> List[Dict]:
        """Analyze multiple chunks in batch"""
        results = []
        
        for i, chunk in enumerate(chunks):
            self.logger.info(f"Analyzing chunk {i+1}/{len(chunks)}: {chunk['chunk_id']}")
            result = self.analyze_chunk(chunk)
            results.append(result)
        
        return results