import json
import re
import unicodedata
from typing import Any

import httpx
from fastapi import HTTPException, status
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings


class AIService:
    def __init__(self) -> None:
        self.api_url = self._normalize_api_url(settings.mimo_api_url)
        self.api_key = settings.mimo_api_key
        self.model = settings.mimo_model

    def _normalize_api_url(self, api_url: str) -> str:
        url = api_url.rstrip("/")
        if url.endswith("/v1"):
            return f"{url}/chat/completions"
        return url

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _prompt(self, task: str, mode: str) -> str:
        instructions = {
            "breakdown": "Break the task into practical implementation steps.",
            "subtasks": "Suggest small actionable subtasks.",
            "summarize": "Summarize the task in one concise Vietnamese sentence.",
            "productivity": "Suggest productivity tips for finishing this task efficiently.",
        }
        return (
            f"{instructions.get(mode, instructions['breakdown'])}\n"
            "Return only JSON with shape {\"suggestions\": [\"...\"]}.\n"
            f"Task: {task}"
        )

    def _payload(self, task: str, mode: str) -> dict[str, Any]:
        # Many AI API providers expose an OpenAI-compatible chat endpoint.
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a concise productivity assistant. Respond in Vietnamese.",
                },
                {"role": "user", "content": self._prompt(task, mode)},
            ],
            "temperature": 0.3,
        }

    def _chat_payload(self, system_prompt: str, user_prompt: str, temperature: float = 0.25) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError)),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        stop=stop_after_attempt(settings.ai_max_retries),
        reraise=True,
    )
    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(self.api_url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    def _extract_text(self, data: dict[str, Any]) -> str:
        if "choices" in data and data["choices"]:
            message = data["choices"][0].get("message", {})
            return message.get("content", "") or data["choices"][0].get("text", "")
        if "suggestions" in data:
            return json.dumps(data)
        if "content" in data:
            return str(data["content"])
        if "text" in data:
            return str(data["text"])
        return json.dumps(data)

    def _parse_suggestions(self, raw_text: str) -> list[str]:
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            parsed = json.loads(text)
            suggestions = parsed.get("suggestions", parsed if isinstance(parsed, list) else [])
            return [str(item).strip() for item in suggestions if str(item).strip()]
        except json.JSONDecodeError:
            start_candidates = [index for index in (text.find("{"), text.find("[")) if index != -1]
            end_candidates = [index for index in (text.rfind("}"), text.rfind("]")) if index != -1]
            if start_candidates and end_candidates:
                try:
                    parsed = json.loads(text[min(start_candidates) : max(end_candidates) + 1])
                    suggestions = parsed.get("suggestions", parsed if isinstance(parsed, list) else [])
                    return [str(item).strip() for item in suggestions if str(item).strip()]
                except json.JSONDecodeError:
                    pass

        lines = [line.strip(" -•\t") for line in text.splitlines()]
        cleaned = []
        for line in lines:
            if not line or line in {"```", "```json", "{", "}", '"suggestions": ['}:
                continue
            cleaned.append(line.rstrip(",").strip().strip('"'))
        return cleaned[:8]

    def _strip_code_fence(self, raw_text: str) -> str:
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return text

    def _normalize_text(self, text: str) -> str:
        ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"\s+", " ", ascii_text.lower()).strip()

    def _plain_chat_text(self, text: str) -> str:
        cleaned = self._strip_code_fence(text)
        cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"^\s{0,3}>\s?", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.replace("**", "").replace("__", "").replace("`", "")
        cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def rule_based_chat(self, question: str) -> str | None:
        text = self._normalize_text(question)
        if not text:
            return None

        if text in {"hi", "hello", "xin chao", "chao"} or any(word in text for word in ("xin chao", "hello", "chao")):
            return (
                "Chào bạn. Mình có thể giải thích kiến trúc MindDeckNote, các lớp IaaS, PaaS, SaaS, "
                "Docker, FastAPI, PostgreSQL, AI API, hoặc cách phần quota 8 lượt chat hoạt động."
            )

        if "quota" in text or "8" in text or "gioi han" in text or "luot" in text:
            return (
                "Rule based: mỗi tài khoản có tối đa 8 lượt hỏi AI. Backend đếm số câu đã trả lời thành công "
                "trong bảng ai_chat_messages. Khi đã đủ 8 lượt, API sẽ trả lỗi 429 và giao diện khóa ô nhập."
            )

        if "iaas" in text and "saas" in text:
            return (
                "Rule based: hệ thống hiện đã thể hiện rõ IaaS và SaaS. IaaS là EC2 chạy Docker, Nginx, backend "
                "và PostgreSQL. SaaS là AI API bên ngoài dùng cho tóm tắt, flashcards và chat. Nếu cần chứng minh "
                "đủ cả IaaS, PaaS, SaaS thì nên bổ sung thêm một dịch vụ managed như database managed hoặc app runner "
                "để phần PaaS thật rõ."
            )

        if "iaas" in text or "ec2" in text or "infrastructure" in text:
            return (
                "IaaS của hệ thống là EC2: mình tự quản máy chủ, Docker, network, Nginx, security group "
                "và tiến trình deploy. Đây là tầng hạ tầng thuê theo nhu cầu."
            )

        if "paas" in text or "platform" in text:
            return (
                "PaaS có thể được thể hiện bằng cách dùng dịch vụ quản lý sẵn như database managed, app runner, "
                "hoặc một nền tảng deploy tự động. Bản hiện tại chủ yếu chạy IaaS trên EC2, còn PaaS là hướng mở rộng hợp lý."
            )

        if "saas" in text or "mimo" in text or "ai api" in text or "external ai" in text:
            return (
                "SaaS trong demo là phần AI API bên ngoài: ứng dụng gọi dịch vụ AI để tóm tắt note, sinh flashcards "
                "và trả lời chat. Người dùng chỉ dùng tính năng qua giao diện, không cần quản mô hình."
            )

        if "docker" in text or "container" in text or "compose" in text:
            return (
                "Docker Compose đóng gói frontend, backend, database và Nginx thành các container riêng. "
                "Cách này làm kiến trúc dễ demo, dễ rebuild và tách rõ trách nhiệm giữa các tầng."
            )

        if "admin" in text or "ip" in text or "khoa tai khoan" in text or "chan ip" in text:
            return (
                "Admin có thể xem user đang hoạt động, khóa tài khoản và chặn IP ở tầng ứng dụng. "
                "Mỗi request đăng nhập đều được kiểm tra trạng thái tài khoản và blocklist IP."
            )

        return None

    def _extract_json(self, raw_text: str) -> Any:
        text = self._strip_code_fence(raw_text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start_candidates = [index for index in (text.find("{"), text.find("[")) if index != -1]
            end_candidates = [index for index in (text.rfind("}"), text.rfind("]")) if index != -1]
            if start_candidates and end_candidates:
                return json.loads(text[min(start_candidates) : max(end_candidates) + 1])
            raise

    async def _complete(self, payload: dict[str, Any]) -> str:
        if not self.api_url or not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI provider is not configured. Set MIMO_API_URL and MIMO_API_KEY.",
            )

        try:
            data = await self._post(payload)
        except httpx.HTTPStatusError as exc:
            detail = f"AI provider returned HTTP {exc.response.status_code}"
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI provider request failed") from exc

        text = self._extract_text(data).strip()
        if not text:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider returned empty output")
        return text

    async def suggest(self, task: str, mode: str = "breakdown") -> list[str]:
        suggestions = self._parse_suggestions(await self._complete(self._payload(task, mode)))
        if not suggestions:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider returned empty output")
        return suggestions

    async def summarize_note(self, title: str, content: str) -> str:
        prompt = (
            "Tom tat note sau bang tieng Viet trong 4-6 cau ngan. "
            "Neu co viec can lam, them 3 bullet action items. "
            "Khong viet mo dau chung chung.\n\n"
            f"Title: {title}\n\nContent:\n{content[:12000]}"
        )
        return await self._complete(
            self._chat_payload(
                "You are an assistant for a student note and spaced repetition app. Respond in Vietnamese.",
                prompt,
                temperature=0.2,
            )
        )

    async def chat_answer(self, question: str) -> str:
        prompt = (
            "Tra loi cau hoi cua nguoi dung bang tieng Viet, ngan gon va ro rang. "
            "Neu cau hoi lien quan den MindDeckNote, cloud, note, flashcard, AI API, FastAPI, React, Docker, Nginx "
            "thi uu tien cau tra loi thuc te va co cau truc. "
            "Khong dung markdown, khong dung heading ##, khong boc chu bang **. "
            "Khong bia dat thong tin rieng tu hoac cau hinh khong co trong cau hoi.\n\n"
            f"Question: {question}"
        )
        answer = await self._complete(
            self._chat_payload(
                "You are a friendly in-app AI assistant for MindDeckNote. Respond in Vietnamese plain text.",
                prompt,
                temperature=0.3,
            )
        )
        return self._plain_chat_text(answer)

    async def generate_flashcards(self, title: str, content: str, max_cards: int = 8) -> list[dict[str, str]]:
        prompt = (
            f"Hay tao toi da {max_cards} flashcards chat luong tu note sau. "
            "Moi card nen hoi mot y ro rang, dap an ngan gon nhung du y. "
            "Chi tra ve JSON hop le theo shape "
            "{\"cards\":[{\"front\":\"question\",\"back\":\"answer\",\"source_text\":\"source excerpt\"}]}.\n\n"
            f"Title: {title}\n\nContent:\n{content[:12000]}"
        )
        raw_text = await self._complete(
            self._chat_payload(
                "You generate clean JSON flashcards for Vietnamese students. Return JSON only.",
                prompt,
                temperature=0.25,
            )
        )
        try:
            parsed = self._extract_json(raw_text)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider returned invalid JSON") from exc

        cards = parsed.get("cards", parsed if isinstance(parsed, list) else [])
        cleaned = []
        for card in cards:
            if not isinstance(card, dict):
                continue
            front = str(card.get("front", "")).strip()
            back = str(card.get("back", "")).strip()
            source_text = str(card.get("source_text", "")).strip() or None
            if front and back:
                cleaned.append({"front": front, "back": back, "source_text": source_text})
        if not cleaned:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI provider returned no flashcards")
        return cleaned[:max_cards]


ai_service = AIService()
