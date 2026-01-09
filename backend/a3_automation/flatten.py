"""
Headless PDF flattening wrapper.
Provides `flatten_pdf(input_path: str, output_path: str) -> bool` that reuses
logic from `pdf_flattening_tool.py` but without any GUI dependencies.

This file is safe to import in a headless server.
"""
from pathlib import Path
from typing import Optional
import fitz
import re


def flatten_pdf(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Flatten a PDF by converting form fields to permanent text (headless).
    Returns path to the flattened PDF (string) on success or raises Exception on failure.
    """
    input_p = Path(input_path)
    if not input_p.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    output_p = Path(output_path) if output_path else input_p.with_name(input_p.stem + "_flattened.pdf")
    output_p.parent.mkdir(parents=True, exist_ok=True)

    try:
        pdf_doc = fitz.open(str(input_p))

        # Pre-processing: ensure fields readable
        needs_preprocessing = False
        sample_field_found = False
        for page_num in range(min(len(pdf_doc), 3)):
            page = pdf_doc[page_num]
            widgets = list(page.widgets())
            if widgets:
                sample_field_found = True
                widget = widgets[0]
                try:
                    widget.update()
                    value = getattr(widget, 'field_value', None)
                    if value is None:
                        needs_preprocessing = True
                        break
                except Exception:
                    needs_preprocessing = True
                    break

        if sample_field_found and needs_preprocessing:
            import tempfile, os
            temp_path = tempfile.mktemp(suffix='.pdf')
            pdf_doc.save(temp_path, incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
            pdf_doc.close()
            pdf_doc = fitz.open(temp_path)
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        # First pass - debug/info only: count total fields
        total_fields_found = 0
        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            widgets = list(page.widgets())
            total_fields_found += len(widgets)

        # Second pass - flatten fields
        field_count = 0
        processed_count = 0
        skipped_empty_count = 0

        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            widgets = list(page.widgets())

            for widget in widgets:
                field_count += 1
                field_name = getattr(widget, 'field_name', f'field_{field_count}')

                # Attempt to get current field value with multiple strategies
                field_value = _get_current_field_value(widget, pdf_doc)

                # Determine problematic fields
                problematic_fields = ['Right_mid', 'Right_belowmid', 'Right_bottom']
                is_problematic_field = any(prob in field_name for prob in problematic_fields)

                if field_value and field_value.strip():
                    processed_count += 1
                    font_props = _get_field_font_properties(widget)
                    try:
                        _insert_formatted_text(page, field_value, widget.rect, font_props)
                    except Exception as e:
                        # fallback: insert plain text at top-left of rect
                        try:
                            page.insert_text(fitz.Point(widget.rect.x0 + 2, widget.rect.y0 + font_props.get('font_size', 12) + 2),
                                             field_value.replace('\n', ' ')[:200], fontsize=font_props.get('font_size', 12), color=font_props.get('text_color', (0,0,0)))
                        except Exception:
                            pass
                else:
                    skipped_empty_count += 1

            # Remove widgets
            for widget in widgets:
                try:
                    # For problematic empty fields, attempt cleaning
                    field_name = getattr(widget, 'field_name', 'unnamed_field')
                    problematic_fields = ['Right_mid', 'Right_belowmid', 'Right_bottom']
                    is_problematic_field = any(prob in field_name for prob in problematic_fields)
                    if is_problematic_field:
                        field_value = _get_current_field_value(widget, pdf_doc)
                        if not field_value or not field_value.strip():
                            _clean_empty_field_artifacts(widget, page, pdf_doc)

                    page.delete_widget(widget)
                except Exception:
                    pass

        # Save
        pdf_doc.save(str(output_p))
        pdf_doc.close()

        return str(output_p)

    except Exception as e:
        raise


# --- Helper functions copied/adapted from original tool but headless ---

def _get_current_field_value(widget, doc) -> str:
    """Headless extraction for a widget's value."""
    final_value = ""

    # Method 1: direct
    try:
        widget.update()
        raw_value = getattr(widget, 'field_value', None)
        if raw_value and _clean_field_value(raw_value):
            return _clean_field_value(raw_value)
    except Exception:
        pass

    # Method 2: appearance
    try:
        ap_obj = None
        if hasattr(widget, 'xref') and widget.xref:
            try:
                ap_obj = doc.xref_get_key(widget.xref, "AP")
            except Exception:
                ap_obj = None
        if ap_obj and len(ap_obj) > 1 and ap_obj[1]:
            ap_content = ap_obj[1]
            if isinstance(ap_content, str) and "BT" in ap_content and "ET" in ap_content:
                text_matches = re.findall(r'BT.*?\((.*?)\).*?ET', ap_content, re.DOTALL)
                if text_matches:
                    return text_matches[0].strip()
            tj_matches = re.findall(r'\((.*?)\)\s*Tj', ap_content)
            if tj_matches:
                combined_text = ' '.join(tj_matches).strip()
                if combined_text:
                    return combined_text
    except Exception:
        pass

    # Method 3: direct pdf object keys
    try:
        if hasattr(widget, 'xref') and widget.xref:
            for key in ['V', 'DV', 'RV']:
                try:
                    obj = doc.xref_get_key(widget.xref, key)
                    if obj and len(obj) > 1 and obj[1]:
                        value_str = obj[1].strip()
                        if value_str.startswith('(') and value_str.endswith(')'):
                            content = value_str[1:-1]
                        elif value_str.startswith('<') and value_str.endswith('>'):
                            try:
                                hex_content = value_str[1:-1]
                                content = bytes.fromhex(hex_content).decode('utf-8', errors='ignore')
                            except Exception:
                                content = value_str
                        else:
                            content = value_str
                        if content and content.strip() and content.lower() not in ['null', 'undefined']:
                            return content.strip()
                except Exception:
                    continue
    except Exception:
        pass

    # Method 4: visual extraction
    try:
        page = widget.parent
        visual = _extract_text_from_field_area(page, widget.rect)
        if visual:
            return visual
    except Exception:
        pass

    # Method 5: form data
    try:
        doc_obj = widget.parent
        if hasattr(doc_obj, 'get_form_field_value'):
            try:
                value = doc_obj.get_form_field_value(widget.field_name)
                if value and str(value).strip() and str(value).lower() not in ['null', 'undefined']:
                    return str(value).strip()
            except Exception:
                pass
    except Exception:
        pass

    return ""


def _clean_field_value(raw_value) -> str:
    if raw_value is None:
        return ""
    if not isinstance(raw_value, str):
        try:
            raw_value = str(raw_value)
        except:
            return ""
    value_lower = raw_value.lower().strip()
    null_indicators = ['null','undefined','none','nil','empty','(null)','(undefined)','(none)','(empty)','null\x00','\x00null','n/a','na','not applicable','---','__','_','.']
    if value_lower in null_indicators:
        return ""
    cleaned = raw_value.replace('\x00','').replace('\r\n','\n').replace('\r','\n')
    cleaned = cleaned.replace('\u00A0',' ').strip()
    if not cleaned.strip():
        return ""
    if re.match(r'^[\s\-_\.]+$', cleaned):
        return ""
    if re.match(r'^[_\s\n]+$', cleaned):
        return ""
    lines = cleaned.split('\n')
    non_underscore_lines = []
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and not re.match(r'^_{10,}$', line_stripped):
            non_underscore_lines.append(line)
    if not non_underscore_lines:
        return ""
    if len(non_underscore_lines) < len(lines):
        cleaned = '\n'.join(non_underscore_lines)
    return cleaned.strip()


def _extract_text_from_field_area(page, field_rect) -> str:
    try:
        text_dict = page.get_text("dict")
        field_texts = []
        for block in text_dict.get('blocks', []):
            if 'lines' in block:
                for line in block['lines']:
                    line_rect = fitz.Rect(line['bbox'])
                    if field_rect.intersects(line_rect):
                        line_text = ''
                        for span in line.get('spans', []):
                            span_rect = fitz.Rect(span['bbox'])
                            if field_rect.intersects(span_rect):
                                text = span.get('text','').strip()
                                if text:
                                    line_text += text + ' '
                        if line_text.strip():
                            field_texts.append(line_text.strip())
        if field_texts:
            combined_text = '\n'.join(field_texts).strip()
            if combined_text and combined_text.lower() not in ['null','undefined','none','']:
                lines = combined_text.split('\n')
                content_lines = []
                for line in lines:
                    if not re.match(r'^_{10,}$', line.strip()):
                        content_lines.append(line)
                if content_lines and any(l.strip() for l in content_lines):
                    return '\n'.join(content_lines).strip()
        return ""
    except Exception:
        return ""


def _clean_empty_field_artifacts(widget, page, doc):
    try:
        if hasattr(widget, 'xref') and widget.xref:
            try:
                doc.xref_set_key(widget.xref, 'AP', 'null')
            except Exception:
                pass
            try:
                doc.xref_set_key(widget.xref, 'BS', 'null')
                doc.xref_set_key(widget.xref, 'Border', 'null')
                doc.xref_set_key(widget.xref, 'BG', 'null')
                doc.xref_set_key(widget.xref, 'H', 'null')
            except Exception:
                pass
            try:
                doc.xref_set_key(widget.xref, 'V', 'null')
                doc.xref_set_key(widget.xref, 'DV', 'null')
            except Exception:
                pass
        try:
            widget.field_value = ''
            widget.update()
        except Exception:
            pass
    except Exception:
        pass


def _get_field_font_properties(widget) -> dict:
    props = {'font_size': 12.0, 'font_name': 'helv', 'text_color': (0,0,0), 'alignment': 0, 'border_width': 0}
    try:
        font_size = None
        for attr in ['text_font_size','text_fontsize','fontsize']:
            if hasattr(widget, attr):
                size = getattr(widget, attr)
                if size and size > 0:
                    font_size = float(size)
                    break
        if not font_size and hasattr(widget, 'text_da') and widget.text_da:
            try:
                da_parts = widget.text_da.split()
                for i, part in enumerate(da_parts):
                    if part == 'Tf' and i>0:
                        font_size = float(da_parts[i-1])
                        break
                    if part.startswith('/') and i < len(da_parts)-1:
                        props['font_name'] = part[1:]
            except Exception:
                pass
        if not font_size:
            try:
                h = widget.rect.height
                if h>0:
                    font_size = min(h*0.6,24.0)
                    if font_size < 6:
                        font_size = 10.0
            except Exception:
                pass
        if font_size:
            props['font_size'] = font_size
        if hasattr(widget, 'text_align'):
            props['alignment'] = getattr(widget, 'text_align', 0)
        if hasattr(widget, 'text_color'):
            props['text_color'] = getattr(widget, 'text_color', (0,0,0))
    except Exception:
        pass
    return props


def _insert_formatted_text(page, text: str, rect, font_props: dict):
    try:
        font_size = font_props.get('font_size', 12.0)
        text_color = font_props.get('text_color', (0,0,0))
        alignment = font_props.get('alignment', 0)
        padding = 2
        available_width = rect.width - (padding*2)
        line_height = font_size * 1.2
        text = text.replace('\r\n','\n').replace('\r','\n')
        def get_x_position(line_text, line_width):
            if alignment == 1:
                return rect.x0 + (rect.width - line_width)/2
            elif alignment == 2:
                return rect.x1 - line_width - padding
            else:
                return rect.x0 + padding
        lines = text.split('\n')
        current_y = rect.y0 + font_size + padding
        for line_idx, line in enumerate(lines):
            if not line:
                current_y += line_height * 0.8
                continue
            words = line.split(' ')
            current_line = ''
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                try:
                    text_width = fitz.get_text_length(test_line, fontsize=font_size)
                except Exception:
                    text_width = len(test_line) * font_size * 0.6
                if text_width <= available_width or not current_line:
                    current_line = test_line
                else:
                    if current_line:
                        try:
                            line_width = fitz.get_text_length(current_line, fontsize=font_size)
                        except Exception:
                            line_width = len(current_line) * font_size * 0.6
                        x_pos = get_x_position(current_line, line_width)
                        page.insert_text(fitz.Point(x_pos, current_y), current_line, fontsize=font_size, color=text_color)
                        current_y += line_height
                    current_line = word
                    if current_y > rect.y1 - font_size:
                        return
            if current_line:
                try:
                    line_width = fitz.get_text_length(current_line, fontsize=font_size)
                except Exception:
                    line_width = len(current_line) * font_size * 0.6
                x_pos = get_x_position(current_line, line_width)
                page.insert_text(fitz.Point(x_pos, current_y), current_line, fontsize=font_size, color=text_color)
                current_y += line_height
            if current_y > rect.y1 - font_size:
                if line_idx < len(lines)-1:
                    return
    except Exception:
        try:
            fallback_text = text.replace('\n',' ')[:200]
            page.insert_text(fitz.Point(rect.x0+2, rect.y0 + font_props.get('font_size',12)+2), fallback_text, fontsize=font_props.get('font_size',12), color=font_props.get('text_color',(0,0,0)))
        except Exception:
            pass
