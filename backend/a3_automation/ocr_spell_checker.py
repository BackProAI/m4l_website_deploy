#!/usr/bin/env python3
"""
Efficient OCR Spell Checker
Optimized spell checking for A3 document OCR text extraction
"""

import re
from spellchecker import SpellChecker
from typing import Dict, List, Tuple, Optional

class OCRSpellChecker:
    def __init__(self):
        """Initialize the spell checker with optimized settings."""
        # Initialize spell checker (English dictionary)
        self.spell = SpellChecker()
        
        # Common OCR error patterns (character substitutions)
        self.ocr_patterns = {
            # Common OCR mistakes
            r'\brn\b': 'm',           # 'rn' often read as 'm'
            r'\bm\b': 'rn',           # Sometimes 'm' should be 'rn'
            r'\bl\b': 'I',            # lowercase 'l' as uppercase 'I'
            r'\bO\b': '0',            # uppercase 'O' as zero
            r'\b0\b': 'O',            # zero as uppercase 'O'
            r'\b1\b': 'l',            # '1' as lowercase 'l'
            r'\b5\b': 'S',            # '5' as 'S'
            r'\b6\b': 'G',            # '6' as 'G'
            r'\b8\b': 'B',            # '8' as 'B'
            r'\bii\b': 'll',          # 'ii' as 'll'
            r'\bvv\b': 'w',           # 'vv' as 'w'
            r'\btuming\b': 'turning', # Common OCR error
            r'\bfrom\b': 'form',      # Context-dependent
        }
        
        # Financial terms dictionary (words to preserve)
        self.financial_terms = {
            'repayments', 'borrow', 'borrowing', 'mortgage', 'loan', 'finance',
            'investment', 'property', 'refinancing', 'equity', 'principal',
            'interest', 'rate', 'annual', 'monthly', 'weekly', 'fortnightly',
            'deposit', 'settlement', 'valuation', 'lender', 'applicant',
            'income', 'expenses', 'assets', 'liabilities', 'employment',
            'australia', 'overseas', 'superannuation', 'salary', 'wages'
        }
        
        # Add financial terms to spell checker
        self.spell.word_frequency.load_words(self.financial_terms)
        
        # Number patterns to preserve
        self.number_patterns = [
            r'\$[\d,]+\.?\d*',        # Currency: $123,456.78
            r'\d+\.\d+%',             # Percentage: 3.5%
            r'\d{1,2}/\d{1,2}/\d{4}', # Date: 12/31/2024
            r'\d+\s*years?',          # Years: 30 years
            r'\d+\s*months?',         # Months: 12 months
            r'\d+\s*weeks?',          # Weeks: 2 weeks
        ]
        
        print("✅ OCR Spell Checker initialized with financial dictionary")
    
    def preserve_important_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Preserve numbers, currencies, and dates during spell check.
        Returns (text_with_placeholders, preservation_map)
        """
        preservation_map = {}
        preserved_text = text
        placeholder_counter = 0
        
        # Preserve all number patterns
        for pattern in self.number_patterns:
            matches = re.finditer(pattern, preserved_text, re.IGNORECASE)
            for match in matches:
                placeholder = f"__PRESERVE_{placeholder_counter}__"
                preservation_map[placeholder] = match.group()
                preserved_text = preserved_text.replace(match.group(), placeholder, 1)
                placeholder_counter += 1
        
        return preserved_text, preservation_map
    
    def restore_preserved_text(self, text: str, preservation_map: Dict[str, str]) -> str:
        """Restore preserved text from placeholders."""
        restored_text = text
        for placeholder, original in preservation_map.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text
    
    def apply_ocr_corrections(self, text: str) -> str:
        """Apply common OCR error corrections."""
        corrected_text = text
        
        for pattern, replacement in self.ocr_patterns.items():
            corrected_text = re.sub(pattern, replacement, corrected_text, flags=re.IGNORECASE)
        
        return corrected_text
    
    def spell_check_word(self, word: str) -> str:
        """Check and correct a single word."""
        # Skip if it's likely a number or special character
        if re.match(r'^[\d\W]+$', word):
            return word
        
        # Skip if word is too short
        if len(word) < 2:
            return word
        
        # Check if word is in dictionary
        if word.lower() in self.spell:
            return word
        
        # Get correction suggestions
        suggestions = self.spell.candidates(word.lower())
        
        if suggestions:
            # Return the most likely correction
            best_suggestion = min(suggestions, key=lambda x: self.spell.word_frequency.dictionary.get(x, 0))
            
            # Preserve original capitalization
            if word.isupper():
                return best_suggestion.upper()
            elif word.istitle():
                return best_suggestion.capitalize()
            else:
                return best_suggestion
        
        return word  # Return original if no suggestions
    
    def check_text(self, text: str, apply_corrections: bool = True) -> Tuple[str, List[Dict]]:
        """
        Main spell check function.
        Returns (corrected_text, corrections_made)
        """
        if not text or not text.strip():
            return text, []
        
        # Step 1: Preserve important text (numbers, dates, etc.)
        preserved_text, preservation_map = self.preserve_important_text(text)
        
        # Step 2: Apply OCR pattern corrections
        pattern_corrected = self.apply_ocr_corrections(preserved_text)
        
        corrections_made = []
        
        if apply_corrections:
            # Step 3: Word-by-word spell checking
            words = re.findall(r'\b\w+\b', pattern_corrected)
            corrected_words = []
            
            for word in words:
                corrected_word = self.spell_check_word(word)
                corrected_words.append(corrected_word)
                
                if corrected_word != word:
                    corrections_made.append({
                        'original': word,
                        'corrected': corrected_word,
                        'type': 'spelling'
                    })
            
            # Rebuild text with corrected words
            corrected_text = pattern_corrected
            for original, corrected in zip(words, corrected_words):
                corrected_text = corrected_text.replace(original, corrected, 1)
        else:
            corrected_text = pattern_corrected
        
        # Step 4: Restore preserved text
        final_text = self.restore_preserved_text(corrected_text, preservation_map)
        
        return final_text, corrections_made
    
    def check_section_results(self, section_results: Dict) -> Dict:
        """
        Apply spell check to all sections in OCR results.
        Optimized for A3 sectioned results format.
        """
        corrected_results = section_results.copy()
        all_corrections = []
        
        print("🔤 Running spell check on extracted text...")
        
        for page_key, sections in section_results.items():
            if page_key.startswith('_'):  # Skip metadata
                continue
            
            corrected_sections = []
            
            for section in sections:
                if 'text' in section and section['text']:
                    original_text = section['text']
                    corrected_text, corrections = self.check_text(original_text)
                    
                    # Update section with corrected text
                    corrected_section = section.copy()
                    corrected_section['text'] = corrected_text
                    
                    # Add correction info
                    if corrections:
                        corrected_section['spell_corrections'] = corrections
                        all_corrections.extend(corrections)
                        print(f"   📝 Section '{section.get('name', 'Unknown')}': {len(corrections)} corrections")
                    
                    corrected_sections.append(corrected_section)
                else:
                    corrected_sections.append(section)
            
            corrected_results[page_key] = corrected_sections
        
        # Add summary to metadata
        if '_metadata' not in corrected_results:
            corrected_results['_metadata'] = {}
        
        corrected_results['_metadata']['spell_check'] = {
            'enabled': True,
            'total_corrections': len(all_corrections),
            'corrections': all_corrections
        }
        
        print(f"✅ Spell check complete: {len(all_corrections)} corrections made")
        
        return corrected_results

# Global instance for efficiency
_spell_checker_instance = None

def get_spell_checker() -> OCRSpellChecker:
    """Get or create spell checker instance (singleton pattern for efficiency)."""
    global _spell_checker_instance
    if _spell_checker_instance is None:
        _spell_checker_instance = OCRSpellChecker()
    return _spell_checker_instance

def spell_check_text(text: str, apply_corrections: bool = True) -> Tuple[str, List[Dict]]:
    """Quick function to spell check text."""
    checker = get_spell_checker()
    return checker.check_text(text, apply_corrections)

def spell_check_sections(section_results: Dict) -> Dict:
    """Quick function to spell check section results."""
    checker = get_spell_checker()
    return checker.check_section_results(section_results)

if __name__ == "__main__":
    # Test the spell checker
    print("🧪 Testing OCR Spell Checker...")
    
    test_text = "I need to bomw $625,000 with monthly repayrnents of $3,774.59"
    
    corrected, corrections = spell_check_text(test_text)
    
    print(f"Original:  {test_text}")
    print(f"Corrected: {corrected}")
    print(f"Corrections: {corrections}")
