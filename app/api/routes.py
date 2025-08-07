from fastapi import APIRouter, HTTPException

from app.schemas.study import StudyRequest, StudyResponse, VerseResponse, RelatedVerseResponse
from app.services.bible_service import parse_reference, get_verse, get_verses, get_related_verses, \
    get_text_for_reference, get_related_by_topic, get_emotion_verses, query_synonyms, list_topics, get_today_devotional
from app.schemas.ask import AskResponse, AskRequest, VerseTextResponse, TopicResponse, EmotionResponse, \
    TopicListResponse

router = APIRouter()

@router.post("/study", response_model=StudyResponse)
async def study(request: StudyRequest):
    """api endpoint for studying a bible verse"""
    try:
        #parse the reference
        book, chapter, start_verse, end_verse = parse_reference(request.reference)
        # get related references from related.json
        related_refs = get_related_verses(request.reference)

        verse_data = []
        #format main verse and return it
        if start_verse == end_verse:
            verse_text = get_verse(book, chapter, start_verse)

            if not verse_text:
                raise FileNotFoundError("verse not found")
            verse_data.append(VerseResponse(verse=start_verse, text=verse_text))
        else:
            # multiple verses
            verses = get_verses(book, chapter, start_verse, end_verse)

            if not verses:
                raise FileNotFoundError("verse not found")
            for v in verses:
                verse_data.append(VerseResponse(verse=v["verse"], text=v["text"]))
        # trial 15 or 20 rewriting the related verse logic
        related_verses = []
        for ref in related_refs:
            related_text = get_text_for_reference(ref)
            if related_text:
                related_verses.append(RelatedVerseResponse(reference=ref, text=related_text))
        return StudyResponse(reference=request.reference, verses=verse_data, related_verses=related_verses)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    query = request.query.strip().lower()

    #expand with synonyms
    q_synonyms = query_synonyms(query)

    #prepare response placeholders
    topic_result = None
    emotion_result = None

    #try topic search and match
    for keyword in q_synonyms:
        topic_match = get_related_by_topic(keyword)
        if topic_match:
            topic_result = TopicResponse(topic=topic_match["topic"],
                                         verses=[VerseTextResponse(reference=v["reference"],
                                                                   text=v["text"]) for v in topic_match["verses"]
                                                 ])
            break
    #emotion based match
    for keyword in q_synonyms:
        emotion_match = get_emotion_verses(keyword)
        if emotion_match:
            verses_with_text = []
            for ref in emotion_match["verses"]:
                text = get_text_for_reference(ref)
                verses_with_text.append(VerseTextResponse(reference=ref, text=text or "Text not found"))
                emotion_result = EmotionResponse(emotion=emotion_match["emotion"], verses=verses_with_text)
                break
    return AskResponse(query=query, topic_result=topic_result, emotion_result=emotion_result)

@router.post("/topics", response_model=TopicListResponse)
async def get_topics():
    """Return a list of topics by name only"""
    return {"topics": list_topics()}

@router.get("/devotional")
async def devotional_today():
    devo = get_today_devotional()
    if devo:
        return devo
    raise HTTPException(status_code=404, detail="NO devotional found for today")