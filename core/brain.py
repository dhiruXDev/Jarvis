from core.logger import log_command
from core.local_parser import local_parse
from core.ai_parser import ai_parse

def process(command):
    cleaned = command.lower().strip()
    print("Cleaned Text:", cleaned)
    log_command(cleaned)
    # ============================================
    # STEP 1 — LOCAL PARSER
    # ============================================

    local_result = local_parse(cleaned)

    if local_result:

        print("[LOCAL PARSER USED]")

        print(local_result)

        return local_result

    # ============================================
    # STEP 2 - AI PARSER 
    # ============================================
    ai_result = ai_parse(cleaned)
    if ai_result:
        print("[AI PARSER USED]")
        print(ai_result)
        return ai_result
    # ============================================
    # STEP 3 — CHAT FALLBACK
    # ============================================

    print("[CHAT FALLBACK]")

    return {
        "intent": "chat",
        "message": cleaned
    }