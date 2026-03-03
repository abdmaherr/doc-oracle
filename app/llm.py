import json
import re
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a precise document analyst. You answer questions using ONLY the provided document context.

## Rules
1. **Citation Required**: Every factual claim MUST cite its source as [Page N]. If multiple pages support a claim, cite all: [Page 2, Page 5].
2. **Grounded Answers Only**: If the context does not contain the answer, respond exactly: "The provided document does not contain information regarding [topic]."
3. **No Fabrication**: Never invent information, statistics, or quotes not present in the context.
4. **Concise & Structured**: Use markdown headers, bullet points, and numbered lists. Keep answers focused.
5. **TL;DR**: End every response with a **TL;DR** section — a 1-2 sentence summary of your answer.

## Response Format
- Use direct quotes from the document when precision matters, formatted as: > "quote text" [Page N]
- For multi-part questions, address each part with its own sub-heading.
- If only partial information is available, state what you found and explicitly note what is missing."""

BRIEF_PROMPT = """You are a document analyst. Given the following document text, produce an Executive Brief.

## Instructions
1. Identify the 3-5 most critical pieces of information in this document.
2. Each bullet must cite its source page as [Page N].
3. Focus on: key findings, decisions, numbers/metrics, action items, and conclusions.
4. If the document is too short or unclear, state what you can determine and note limitations.
5. End with a one-sentence "Bottom Line" that captures the document's core purpose.

## Output Format
Return ONLY a JSON object (no markdown fences) with this structure:
{"bullets": ["point 1 [Page N]", "point 2 [Page N]", ...], "bottom_line": "One sentence summary."}"""


class LLMClient:
    """Groq wrapper for RAG response generation (free tier, very fast)."""

    def __init__(self, model: str = settings.LLM_MODEL):
        self.api_key = settings.GROQ_API_KEY
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def _chat(self, system: str, user: str) -> str:
        """Send a chat completion request to Groq."""
        response = httpx.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _chat_with_history(self, system: str, messages: list[dict]) -> str:
        """Send a multi-turn chat request to Groq."""
        groq_messages = [{"role": "system", "content": system}]
        for msg in messages:
            groq_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        response = httpx.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": groq_messages,
                "temperature": 0.3,
                "max_tokens": 2048,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def generate_response(
        self,
        query: str,
        context_chunks: list[dict],
        chat_history: list[dict] | None = None,
    ) -> dict:
        """
        Generate a response using retrieved context chunks.

        Returns: {"answer": str, "sources": [{"page": int, "text_snippet": str}]}
        """
        # Build context section
        context_parts = []
        for chunk in context_chunks:
            page = chunk["metadata"].get("page_number", "?")
            context_parts.append(f"[Page {page}]: {chunk['text']}")
        context_str = "\n---\n".join(context_parts)

        user_message = f"""Document context:
---
{context_str}
---

Question: {query}"""

        try:
            if chat_history:
                messages = []
                for msg in chat_history[-6:]:  # Last 3 turns
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role in ("user", "assistant"):
                        messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": user_message})
                answer = self._chat_with_history(SYSTEM_PROMPT, messages)
            else:
                answer = self._chat(SYSTEM_PROMPT, user_message)

            sources = self._extract_sources(answer, context_chunks)
            return {"answer": answer, "sources": sources}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise RuntimeError(
                    "Groq rate limit reached. Free tier: 30 req/min. Wait a moment and try again."
                )
            raise RuntimeError(f"Groq API error: {e.response.text}")

    def generate_brief(self, pages_text: list[dict]) -> dict:
        """
        Generate an executive brief from full document pages.

        Args:
            pages_text: [{"page_number": int, "text": str}, ...]

        Returns: {"bullets": [...], "bottom_line": "..."}
        """
        # Build document text with page markers
        doc_parts = []
        for page in pages_text:
            doc_parts.append(f"[Page {page['page_number']}]:\n{page['text']}")
        doc_text = "\n\n---\n\n".join(doc_parts)

        # Groq supports large context but keep it reasonable
        if len(doc_text) > 30000:
            doc_text = doc_text[:30000] + "\n\n[Document truncated for briefing...]"

        try:
            raw = self._chat(BRIEF_PROMPT, doc_text).strip()

            # Handle potential markdown fences
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            return json.loads(raw)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse brief JSON: {e}")
            return {
                "bullets": ["Could not generate executive brief. Please query the document directly."],
                "bottom_line": "Brief generation encountered an error.",
            }
        except Exception as e:
            logger.error(f"Brief generation error: {e}")
            return {
                "bullets": [f"Brief generation failed: {str(e)}"],
                "bottom_line": "Please query the document directly.",
            }

    def _extract_sources(
        self, answer: str, context_chunks: list[dict]
    ) -> list[dict]:
        """Extract page citations from the answer and match to source chunks."""
        cited_pages = set()
        for match in re.finditer(r"\[Page\s+(\d+)\]", answer):
            cited_pages.add(int(match.group(1)))

        sources = []
        seen_pages = set()
        for chunk in context_chunks:
            page = chunk["metadata"].get("page_number")
            if page in cited_pages and page not in seen_pages:
                sources.append(
                    {
                        "page": page,
                        "text_snippet": chunk["text"][:300],
                    }
                )
                seen_pages.add(page)

        return sources
