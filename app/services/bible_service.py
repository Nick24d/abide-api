import os, json, re
from datetime import datetime
from typing import Dict, List

#file path for the json file
BASE_BIBLE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bible")  # path to bible folder
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

#list of bible books for validation and normalization
BIBLE_BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel",
               "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
               "Psalms", "Proverbs", "Ecclesiastes", "Songs of Solomon", "Isaiah", "Jeremiah", "Lamentations",
               "Ezekiel",
               "Daniel", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
               "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians",
               "Ephesians", "Philippians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
               "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"]


def parse_reference(reference: str):
    """parse a bible reference string into book, chapter and verse. example: John 3:16 -->("John", 3, 16)"""

    #normalize spacing and capitalization
    reference = reference.strip()

    # extract book name and also can include numbers
    # match up to chapter:verse using regex
    match = re.match(r"^([1-3]?\s?[A-Za-z\s]+)\s+(\d+):(\d+)(?:-(\d+))?$", reference)
    if not match:
        raise ValueError("Invalid reference format. use Book Chapter:Verse like 'John 3:16'.")

    #extract parts
    book = match.group(1).strip().title()  #John
    chapter = int(match.group(2))  # 3
    start_verse = int(match.group(3))  #16
    end_verse = int(match.group(4)) if match.group(4) else start_verse

    if end_verse < start_verse:
        return ValueError("End verse cannot be lower than start verse")

    # validate book name
    if book not in BIBLE_BOOKS:
        raise ValueError(f"Invalid book name: {book}")
    return book, chapter, start_verse, end_verse


def get_verse(book: str, chapter: int, verse: int):
    """fetch the verse text from the json bible files based on book, chapter and verse"""

    # build the file path
    chapter_file = os.path.join(BASE_BIBLE_PATH, book, f"{chapter}.json")

    # check if chapter exists
    if not os.path.exists(chapter_file):
        raise FileNotFoundError(f"chapter {chapter} for {book} not found.")

    # load the chapter json file
    with open(chapter_file, "r", encoding="utf-8") as f:
        chapter_data = json.load(f)

    # convert the verse number to string because json keys are strings
    verse_key = chapter_data.get("verses", [])

    for v in verse_key:
        if v.get("verse") == verse:
            return v.get("text")

    return None


def get_verses(book: str, chapter: int, start_verse: int, end_verse: int):
    """fetch the verse text from the json bible files based on book, chapter and verse"""

    # build the file path
    chapter_file = os.path.join(BASE_BIBLE_PATH, book, f"{chapter}.json")

    # check if chapter exists
    if not os.path.exists(chapter_file):
        raise FileNotFoundError(f"chapter {chapter} for {book} not found.")

    # load the chapter json file
    with open(chapter_file, "r", encoding="utf-8") as f:
        chapter_data = json.load(f)

    # convert the verse number to string because json keys are strings
    verse_key = chapter_data.get("verses", [])

    selected_verses = [v for v in verse_key if start_verse <= v.get("verse", 0) <= end_verse]

    return selected_verses


def get_related_by_topic(keyword: str):
    """get related verse by keyword or topic"""

    topic_path = os.path.join(BASE_DIR, "topics.json")

    if not os.path.exists(topic_path):
        raise FileNotFoundError("topics.json not found")

    with open(topic_path, "r", encoding="utf-8") as f:
        topics = json.load(f)

    keyword = keyword.lower()
    for topic, verses in topics.items():
        if keyword in topic.lower():
            verses_w_text = []
            for ref in verses:
                text = get_text_for_reference(ref)
                verses_w_text.append({"reference": ref,
                                      "text": text if text else "Text not found"})
            return {"topic": topic,
                    "verses": verses_w_text}
    return None

def get_related_verses(reference: str):
    """" get related verse using the key verse"""
    related_file = os.path.join(BASE_DIR, "related.json")
    if not os.path.exists(related_file):
        raise FileNotFoundError("related.json not found")

    with open(related_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for verse in data.get("verse_groups", []):
        if verse.get("main").lower() == reference.lower():
            return verse.get("related", [])
    return []

def get_text_for_reference(ref: str):
    """ fetch text for a given bible reference either single or multiple"""
    book, chapter, start_verse, end_verse = parse_reference(ref)

    if start_verse == end_verse:
        text = get_verse(book, chapter, start_verse)
        if text:
            return text
        else:
            print(f"error returning text for {ref}")
            return " "
    else:
        verses = get_verses(book, chapter, start_verse, end_verse)
        if verses:
            return " ".join([v["text"] for v in verses ])
        else:
            print(f"error returning text for {ref}")
            return " "

def get_emotion_verses(feeling: str):
    """search the emotion.json file and return it verses"""
    emotion_path = os.path.join(BASE_DIR, "emotion.json")

    if not os.path.exists(emotion_path):
        raise FileNotFoundError("emotion.json not found")

    try:
        with open(emotion_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        feeling = feeling.lower()
        emotion_data = data.get("Feelings", {})

        for subfeelings in emotion_data.values():
            for sub, verses in subfeelings.items():
                if feeling in sub.lower():
                    return {"emotion": sub,
                            "verses": verses }
    except FileNotFoundError:
        return print("emotion.json not found")

def query_synonyms(query: str) -> list:
    """load synonyms and expand th query into a list of keywords.
    get the synonyms from the txt file and expand each keyword with its synonyms"""

    synonyms_path = os.path.join(BASE_DIR, "Synonyms.txt")

    if not os.path.exists(synonyms_path):
        raise FileNotFoundError("file not found")
    #load synonyms dictionary
    try:
        with open(synonyms_path,"r", encoding="utf-8") as f:
            synonyms = json.load(f)
    except json.JSONDecodeError:
        print(" unable to load file")
        synonyms = {}

    # normalise and split
    words = query.lower().split()

    # expand query with synonyms
    expanded = set(words)
    for word in words:
        if word in synonyms:
            expanded.update(synonyms[word])
    return list(expanded)

def find_matches(expanded: list, emotions_data: dict, topics: dict):
    """ find the best match from the topics.json and the emotion.json"""

    topic_match = None
    emotion_match = None

    #match topic
    for topic, verses in topics.items():
        for keyword in expanded:
            if keyword in topic.lower():
                topic_match = {"name": topic, "verse": verses}
                break
        if topic_match:
            break

    #match emotion
    for subfeelings in emotions_data.values():
        for sub, verses in subfeelings.items():
            for keyword in expanded:
                if keyword in sub.lower():
                    emotion_match = {"name": sub, "verses":verses}
                    break
                else:
                    return None
            if emotion_match:
               break
        if emotion_match:
            break
    return {"topic": topic_match, "emotion": emotion_match}

def list_topics():
    topic_path = os.path.join(BASE_DIR, "topics.json")

    if not os.path.exists(topic_path):
        raise FileNotFoundError("topics.json not found")
    try:
        with open(topic_path, "r", encoding="utf-8") as f:
            topics = json.load(f)
        return list(topics.keys())
    except Exception:
        return []

def get_today_devotional():
    devo_path = os.path.join(BASE_DIR, "rhapsody.json")
    try:
        with open(devo_path, "r", encoding="utf-8") as f:
            rhapsody =json.load(f)

        today = datetime.now().strftime("%B %d") # Month and date e.g Aug 4

        for devo in rhapsody:
            if devo.get("date").strip().lower() == today.lower():
                return devo
        return None
    except Exception as e:
        print(f"[Error] could not load devotional: {e}")
        return None