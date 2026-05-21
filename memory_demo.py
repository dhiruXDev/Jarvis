import time
import asyncio
from datetime import datetime
from memory import ModularMemoryEngine, MemoryCategory

# Custom terminal color highlights
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"{BOLD}{BLUE}{title.center(80)}{RESET}")
    print("=" * 80)

def print_sub_header(title: str):
    print(f"\n{BOLD}{CYAN}--- {title} ---{RESET}")

async def run_demo():
    print_header("JARVIS MODULAR MEMORY ENGINE SHOWCASE")
    
    # 1. Initialize Memory Engine
    print(f"{BOLD}Step 1: Initializing Memory Engine...{RESET}")
    # Using 'sentence-transformers' but engine automatically falls back if missing
    engine = ModularMemoryEngine(
        db_dir=".memories",
        embedding_preferred="sentence-transformers",
        half_life_hours=1.0  # short half life of 1 hour to easily observe recency decay!
    )
    
    print(f"{GREEN}[OK] Embedding Provider Loaded: {type(engine.embeddings).__name__}{RESET}")
    print(f"{GREEN}[OK] SQLite Database Connected: {engine.long_term.db_path}{RESET}")
    print(f"{GREEN}[OK] Vector Database Connected: {type(engine.vector_store._collection).__name__}{RESET}")

    # Reset databases for a clean demo run
    print("\nResetting databases for a clean demonstration...")
    engine.long_term.clear()
    engine.vector_store.clear()
    engine.short_term.clear()

    # 2. Add Memories across categories
    print_header("ADD MEMORIES (add_memory)")
    print("Inserting structured memories across all 6 required categories...")

    memories_to_add = [
        # Preferences
        ("User prefers dark mode for all code editors and terminal sessions.", "preferences", 8, {"theme": "dark"}),
        ("User's favorite programming language is Python, with Go as a close second.", "preferences", 7, {"primary": "python"}),
        
        # Habits
        ("User opens Outlook email and reviews calendar schedules every weekday morning at 9:00 AM.", "habits", 5, {"time": "09:00"}),
        
        # Projects
        ("Active project is 'Jarvis', a modular python-based agentic personal AI assistant.", "projects", 10, {"status": "development"}),
        ("Jarvis uses Ollama for local LLM intent parsing and speech recognition for input.", "projects", 9, {"component": "LLM"}),
        
        # Workflows
        ("After compiling code, the user always runs pytest to verify system stability.", "workflows", 6, {"action": "testing"}),
        
        # Conversations
        ("User mentioned they plan to deploy the Jarvis server instance to AWS next Tuesday.", "conversations", 8, {"role": "user"}),
        ("Jarvis replied confirming AWS ECS target deployment using Docker containers.", "conversations", 7, {"role": "assistant"}),
        
        # Automation History
        ("Executed internet speedtest. Download: 154 Mbps, Upload: 48 Mbps.", "automation_history", 4, {"status": "success", "command": "speedtest"}),
        ("Attempted to launch vscode, process failed due to missing system path.", "automation_history", 5, {"status": "failed", "command": "open_vscode"})
    ]

    ids = {}
    for i, (content, category, importance, metadata) in enumerate(memories_to_add):
        mem_id = await engine.add_memory(content, category, importance, metadata)
        ids[f"memory_{i}"] = mem_id
        print(f"[{GREEN}ADDED{RESET}] Category: {category:<20} | ID: ...{mem_id[-8:]} | Importance: {importance} | Content: \"{content}\"")
        time.sleep(0.05) # Tiny pause to ensure slightly different timestamps

    # 3. Retrieve Memory and update frequency
    print_header("RETRIEVE MEMORY (retrieve_memory)")
    target_key = "memory_0" # "User prefers dark mode..."
    target_id = ids[target_key]
    print(f"Retrieving target memory ID: {target_id}")
    
    # Let's retrieve it multiple times to build up a high access frequency!
    print("Simulating multiple accesses to trigger frequency scoring amplification...")
    for _ in range(4):
        record = await engine.retrieve_memory(target_id)
        time.sleep(0.01)

    print(f"\n{BOLD}Retrieved Record Details:{RESET}")
    print(f"  - Content: {YELLOW}\"{record['content']}\"{RESET}")
    print(f"  - Category: {record['category']}")
    print(f"  - Importance: {record['importance']}/10")
    print(f"  - {BOLD}Access Frequency (Access Count): {record['access_count']}{RESET}")
    print(f"  - Created At: {record['created_at']}")
    print(f"  - Last Accessed At: {record['last_accessed_at']}")

    # 4. Short Term Session context demonstration
    print_header("SHORT-TERM SESSION MEMORY BUFFER")
    print("Reviewing recent messages inside in-memory short-term buffers...")
    short_term_history = engine.short_term.get_history()
    for msg in short_term_history:
        print(f"  [{BLUE}Short-Term Msg{RESET}] {msg['role'].upper()}: {msg['content']}")
        
    print("\nReviewing recent actions logged in short-term buffer...")
    short_term_actions = engine.short_term.get_recent_actions()
    for act in short_term_actions:
        print(f"  [{YELLOW}Short-Term Action{RESET}] {act['action']} (Status: {act['status']})")

    # Dynamic context tracking
    print("\nDemonstrating dynamic session variables...")
    engine.short_term.set_context("current_working_directory", "e:\\Project\\Jarvis")
    engine.short_term.set_context("user_mood", "productive")
    print(f"  - Active Session Path: {GREEN}{engine.short_term.get_context('current_working_directory')}{RESET}")
    print(f"  - User State: {GREEN}{engine.short_term.get_context('user_mood')}{RESET}")

    # 5. Semantic similarity search with Unified Memory Scoring
    print_header("SEMANTIC SEARCH WITH UNIFIED MEMORY SCORING (search_memory)")
    print("Searching database semantically. Results are mathematically ranked using a weighted sum of:")
    print(f"  {BOLD}Unified Score = 0.5 * Similarity + 0.2 * Importance + 0.15 * Recency + 0.15 * Frequency{RESET}")
    print("-" * 80)

    queries = [
        "How should the editor or terminal colors look?",
        "What does the user do at the start of a weekday morning?",
        "How do we deploy the application server?",
        "What is the current main coding project?"
    ]

    for q in queries:
        print(f"\n{BOLD}{CYAN}Search Query: \"{q}\"{RESET}")
        results = await engine.search_memory(q, limit=3)
        
        # Print a beautiful ASCII scoring table
        print(f"{'Memory Content Summary':<45} | {'Category':<12} | {'Sim':<4} | {'Imp':<4} | {'Rec':<4} | {'Frq':<4} | {'UNIFIED':<7}")
        print("-" * 90)
        for r in results:
            content_truncated = r['content'][:42] + "..." if len(r['content']) > 42 else r['content']
            print(
                f"{content_truncated:<45} | "
                f"{r['category']:<12} | "
                f"{r['similarity_score']:.2f} | "
                f"{r['importance_score']:.2f} | "
                f"{r['recency_score']:.2f} | "
                f"{r['frequency_score']:.2f} | "
                f"{BOLD}{GREEN}{r['unified_score']:.3f}{RESET}"
            )
        print("-" * 90)

    # 6. Memory Summarization Showcase
    print_header("MEMORY SUMMARIZATION (summarize_memory)")
    print("Synthesizing conversation logs into high-level summaries...")
    conv_summary = await engine.summarize_memory(category="conversations")
    print(f"\n{BOLD}Conversations Synthesis Output:{RESET}\n{conv_summary}")

    print("\nSynthesizing automation activity logs...")
    auto_summary = await engine.summarize_memory(category="automation_history")
    print(f"\n{BOLD}Automation Activity Synthesis Output:{RESET}\n{auto_summary}")

    # 7. Delete memory demonstration
    print_header("DELETE MEMORY (delete_memory)")
    delete_target = ids["memory_9"] # Launch vscode failed
    print(f"Deleting memory entry: \"{memories_to_add[9][0]}\" (ID: {delete_target})")
    
    deleted = await engine.delete_memory(delete_target)
    print(f"Deletion status: {GREEN if deleted else RED}{deleted}{RESET}")
    
    # Confirm deletion via search
    print("\nSearching again for 'vscode'...")
    search_after_delete = await engine.search_memory("vscode", limit=1)
    if not search_after_delete or delete_target not in [x["id"] for x in search_after_delete]:
        print(f"{GREEN}[OK] Confirmed: Memory successfully expunged from SQLite and Vector databases.{RESET}")
    else:
        print(f"{RED}[WARN] Warning: Memory was found in database after delete operation.{RESET}")

    print_header("DEMONSTRATION CONCLUDED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(run_demo())
