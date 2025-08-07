import fitz
import json
import re

def format_devotion_page(text):
    result = {
        "topic": "",
        "memory_verse": "",
        "body_text": "",
        "prayer": "",
        "further_study": "",
        "bible_reading_plan": {
            "1_year_plan": "",
            "2_year_plan": ""
        }
    }

    # Normalize and split into lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    n = len(lines)

    # Step 1: Find the topic (line after day heading)
    for i in range(n):
        if re.match(r"(?i)^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+\d{1,2}$", lines[i]):
            if i + 1 < n:
                result["topic"] = lines[i + 1].strip()
            break

    # Step 2: Memory verse = first line that starts with (
    for line in lines:
        if line.startswith("(") and result["memory_verse"] == "":
            result["memory_verse"] = line.strip()
            break

    # Join for easier block detection
    full_text = "\n".join(lines)

    # Step 3: Extract PRAYER block
    prayer_match = re.search(r'(?i)\bPRAYER\b\s*(.*?)(?=\bFURTHER STUDY\b|\b1[-–]YEAR|\b2[-–]YEAR|$)', full_text, re.DOTALL)
    if prayer_match:
        result["prayer"] = prayer_match.group(1).strip()

    # Step 4: Extract FURTHER STUDY
    fs_match = re.search(r'(?i)\bFURTHER STUDY\b\s*[:\-]?\s*(.*?)(?=\b1[-–]YEAR|\b2[-–]YEAR|$)', full_text, re.DOTALL)
    if fs_match:
        result["further_study"] = fs_match.group(1).strip()

    # Step 5: Extract 1-year plan
    one_year = re.search(r'(?i)\b1[\-–]YEAR BIBLE READING PLAN\b\s*(.+)', full_text)
    if one_year:
        result["bible_reading_plan"]["1_year_plan"] = one_year.group(1).strip()

    # Step 6: Extract 2-year plan
    two_year = re.search(r'(?i)\b2[\-–]YEAR BIBLE READING PLAN\b\s*(.+)', full_text)
    if two_year:
        result["bible_reading_plan"]["2_year_plan"] = two_year.group(1).strip()

    # Step 7: Body text is from after memory verse to before PRAYER
    body_text = ""
    try:
        start_index = lines.index(result["memory_verse"]) + 1
        for i in range(start_index, n):
            if re.match(r'(?i)PRAYER', lines[i]):
                break
            body_text += lines[i] + "\n"
    except ValueError:
        body_text = ""

    result["body_text"] = body_text.strip()

    return result

def extract_pdf(pdf_path, start_page=6, output_path="devotionals.json"):
    doc = fitz.open(pdf_path)
    pages = [doc[i].get_text() for i in range(start_page, len(doc))]
    devotionals = []
    for i in range(0, len(pages) - 1,2):
        combined_text = pages[i] + "\n" + pages[i + 1]
        formatted = format_devotion_page(combined_text)
        devotionals.append(formatted)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(devotionals, f, ensure_ascii=False, indent=2)

    print(f"{len(devotionals)} devotionals saved to {output_path}")

    #usage
extract_pdf("august_ror.pdf", start_page=6, output_path="../data/rhapsody.json")