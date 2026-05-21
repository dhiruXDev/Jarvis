import re
from typing import List, Dict, Any

class ExtractiveSummarizerFallback:
    """
    A pure Python rule-based extractive summarizer.
    Extremely robust fallback for summarizing conversation history and action history
    when an LLM / Ollama connection is unavailable.
    """
    @staticmethod
    def summarize(items: List[Dict[str, Any]], category: str = "conversations") -> str:
        if not items:
            return f"No recent {category} found to summarize."

        if category == "conversations":
            return ExtractiveSummarizerFallback._summarize_conversations(items)
        elif category == "automation_history":
            return ExtractiveSummarizerFallback._summarize_actions(items)
        else:
            return ExtractiveSummarizerFallback._summarize_generic(items, category)

    @staticmethod
    def _summarize_conversations(items: List[Dict[str, Any]]) -> str:
        # Conversations typically contain 'role' and 'content' or just strings
        exchanges = []
        unique_words = {}
        
        for item in items:
            metadata = item.get("metadata", {})
            role = (item.get("role") or metadata.get("role") or "user").capitalize()
            content = item.get("content", "").strip()
            if not content:
                continue
                
            exchanges.append(f"- {role}: {content}")
            
            # Simple keyword extraction
            words = re.findall(r'\b\w{4,15}\b', content.lower())
            for w in words:
                if w not in ["about", "their", "there", "would", "could", "should", "other"]:
                    unique_words[w] = unique_words.get(w, 0) + 1
                    
        # Sort keywords by frequency
        sorted_keywords = sorted(unique_words.items(), key=lambda x: x[1], reverse=True)[:5]
        keywords_str = ", ".join([kw[0] for kw in sorted_keywords]) if sorted_keywords else "N/A"
        
        summary = [
            "### Conversation Summary (Fallback Mode)",
            f"* **Total Exchanges**: {len(items)}",
            f"* **Key Topics Detected**: {keywords_str}",
            "\n**Recent Dialogue Transcripts**:",
            *exchanges[-6:] # Show last 6 messages
        ]
        
        return "\n".join(summary)

    @staticmethod
    def _summarize_actions(items: List[Dict[str, Any]]) -> str:
        action_counts = {}
        successes = 0
        failures = 0
        recent_log = []
        
        for item in items:
            metadata = item.get("metadata", {})
            act = item.get("action") or metadata.get("command") or item.get("content") or "unknown_action"
            status = item.get("status") or metadata.get("status") or "success"
            
            action_counts[act] = action_counts.get(act, 0) + 1
            if status == "success":
                successes += 1
            else:
                failures += 1
                
            recent_log.append(f"- [{status.upper()}] {act} (at {item.get('created_at', 'N/A')})")

        stats = [f"{k} (x{v})" for k, v in action_counts.items()]
        
        summary = [
            "### Automation & Activity Summary (Fallback Mode)",
            f"* **Total Actions Executed**: {len(items)}",
            f"* **Success Rate**: {successes}/{len(items)} ({successes/len(items)*100:.1f}%)" if items else "* **Success Rate**: N/A",
            f"* **Activity Breakdown**: {', '.join(stats) if stats else 'None'}",
            "\n**Recent Activity Feed**:",
            *recent_log[-5:] # Show last 5 actions
        ]
        
        return "\n".join(summary)

    @staticmethod
    def _summarize_generic(items: List[Dict[str, Any]], category: str) -> str:
        contents = [item.get("content", "") for item in items if item.get("content")]
        
        # Simple frequency extraction
        unique_words = {}
        for c in contents:
            words = re.findall(r'\b\w{4,15}\b', c.lower())
            for w in words:
                unique_words[w] = unique_words.get(w, 0) + 1
                
        sorted_keywords = sorted(unique_words.items(), key=lambda x: x[1], reverse=True)[:5]
        keywords_str = ", ".join([kw[0] for kw in sorted_keywords]) if sorted_keywords else "N/A"

        summary = [
            f"### Memory Summary: {category.capitalize()} (Fallback Mode)",
            f"* **Total Items Record Count**: {len(items)}",
            f"* **Core Themes**: {keywords_str}",
            "\n**Extracted Items Sample**:",
            *[f"- {c[:120]}..." if len(c) > 120 else f"- {c}" for c in contents[-5:]]
        ]
        
        return "\n".join(summary)
