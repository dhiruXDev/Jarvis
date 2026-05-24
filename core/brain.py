from core.logger import log_command
from core.local_parser import local_parse
from core.ai_parser import ai_parse

def process(command):
    cleaned = command.lower().strip()
    speak("Cleaned Text:", cleaned)
    log_command(cleaned)
    # ============================================
    # STEP 1 — LOCAL PARSER
    # ============================================

    local_result = local_parse(cleaned)

    if local_result:

        speak("[LOCAL PARSER USED]")

        speak(local_result)

        return local_result

    # ============================================
    # STEP 2 - AI PARSER 
    # ============================================
    ai_result = ai_parse(cleaned)
    if ai_result:
        speak("[AI PARSER USED]")
        speak(ai_result)
        return ai_result
    # ============================================
    # STEP 3 — CHAT FALLBACK
    # ============================================

    speak("[CHAT FALLBACK]")

    return {
        "intent": "chat",
        "message": cleaned
    }