import os
import json
import queue as _queue
import threading
import requests
from dotenv import load_dotenv

load_dotenv()


class HiAgentClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("HITSZ_API_KEY")
        self.base_url = "http://zhiwen.hitsz.edu.cn:10211/api/proxy/api/v1/"
        self.user_id = "ikrokx_001"

    def _get_headers(self, is_chat=False):
        headers = {
            "Apikey": self.api_key,
            "Content-Type": "application/json",
        }
        if is_chat:
            headers["Accept"] = "text/event-stream"
        return headers

    # ── SSE 解析（chat_query_v2 / workflow_run 共用） ──────────────────────────
    def _parse_sse(self, response) -> dict:
        thought_acc, reply_acc, conv_id = "", "", ""
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8").strip()
            if not decoded.startswith("data:"):
                continue
            json_str = decoded[len("data:"):].strip()
            if json_str == "[DONE]":
                break
            try:
                d = json.loads(json_str)
                event = d.get("event", "")
                content = d.get("answer", "")
                if event == "think_message":
                    thought_acc += content
                elif event == "message":
                    reply_acc += content
                if not conv_id:
                    conv_id = d.get("conversation_id", "")
            except (json.JSONDecodeError, IndexError):
                continue
        return {
            "conversation_id": conv_id,
            "thought": thought_acc.strip(),
            "reply": reply_acc.strip() if reply_acc else "",
        }

    # ── 对话型 Agent：创建会话 ─────────────────────────────────────────────────
    def create_conversation(self, inputs: dict = None, user_id: str = None) -> str:
        url = self.base_url + "create_conversation"
        data = {"UserID": (user_id or self.user_id)[:20], "Inputs": inputs or {}}
        try:
            resp = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            if not resp.ok:
                body = ""
                try:
                    body = resp.json()
                except Exception:
                    body = resp.text[:300]
                print(f"[create_conversation] {resp.status_code} 错误 | 请求体: {data} | 响应: {body}")
                return None
            return resp.json().get("Conversation", {}).get("AppConversationID")
        except Exception as e:
            print(f"[create_conversation] 异常: {e}")
            return None

    # ── 对话型 Agent：发起查询 ─────────────────────────────────────────────────
    def ask_ai(self, prompt: str, conversation_id: str = None) -> dict:
        conv_id = conversation_id or self.create_conversation()
        if not conv_id:
            return {"thought": "", "reply": "系统初始化失败", "conversation_id": ""}
        url = self.base_url + "chat_query_v2"
        data = {
            "UserID": self.user_id,
            "AppConversationID": conv_id,
            "Query": prompt,
            "ResponseMode": "streaming",
        }
        try:
            resp = requests.post(
                url, headers=self._get_headers(is_chat=True),
                json=data, stream=True, timeout=60
            )
            result = self._parse_sse(resp)
            result["conversation_id"] = conv_id
            if not result["reply"]:
                result["reply"] = "AI 响应解析异常"
            return result
        except Exception as e:
            return {"thought": "", "reply": f"请求崩溃: {e}", "conversation_id": conv_id}

    # ── 对话型 Agent：流式生成（yield SSE 事件） ──────────────────────────────
    def stream_ask_ai(self, prompt: str, conversation_id: str = None, user_id: str = None):
        """Yield (event_type, data_str) pairs from HiAgent SSE stream."""
        uid = (user_id or self.user_id)[:20]  # HiAgent 限制 1-20 字符
        conv_id = conversation_id or self.create_conversation(user_id=uid)
        if not conv_id:
            yield ("error", json.dumps({"error": "系统初始化失败"}))
            return

        url = self.base_url + "chat_query_v2"
        payload = {
            "UserID": uid,
            "AppConversationID": conv_id,
            "Query": prompt,
            "ResponseMode": "streaming",
        }

        line_queue = _queue.Queue()

        def _reader():
            try:
                resp = requests.post(
                    url, headers=self._get_headers(is_chat=True),
                    json=payload, stream=True, timeout=60
                )
                for line in resp.iter_lines():
                    line_queue.put(line)
            except Exception as exc:
                line_queue.put(exc)
            finally:
                line_queue.put(None)

        threading.Thread(target=_reader, daemon=True).start()

        thought_acc = ""
        seen_message = False
        stream_end_sent = False

        while True:
            # token 流结束后用短超时：静默超过 2.5s 立即发 stream_end
            wait = 2.5 if (seen_message and not stream_end_sent) else 60.0
            try:
                item = line_queue.get(timeout=wait)
            except _queue.Empty:
                if seen_message and not stream_end_sent:
                    stream_end_sent = True
                    yield ("stream_end", "")
                continue  # 继续等待 think_message / [DONE]

            if item is None:
                break
            if isinstance(item, Exception):
                if seen_message:
                    if not stream_end_sent:
                        yield ("stream_end", "")
                    yield ("done", json.dumps({"thought": thought_acc.strip(), "conversation_id": conv_id}))
                else:
                    yield ("error", json.dumps({"error": str(item)}))
                return

            decoded = item.decode("utf-8").strip() if isinstance(item, bytes) else item.strip()
            if not decoded.startswith("data:"):
                continue
            json_str = decoded[5:].strip()
            if json_str == "[DONE]":
                break
            try:
                d = json.loads(json_str)
                event = d.get("event", "")
                content = d.get("answer", "")
                if event == "message":
                    seen_message = True
                    yield ("token", content)
                elif event == "think_message":
                    if seen_message and not stream_end_sent:
                        stream_end_sent = True
                        yield ("stream_end", "")
                    thought_acc += content
            except (json.JSONDecodeError, IndexError):
                continue

        if seen_message and not stream_end_sent:
            yield ("stream_end", "")
        yield ("done", json.dumps({
            "thought": thought_acc.strip(),
            "conversation_id": conv_id,
        }))

    # ── 纯工作流 Agent：sync_run_app_workflow ─────────────────────────────────
    def run_workflow(self, inputs: dict) -> dict:
        """
        调用纯工作流 App 专用接口 sync_run_app_workflow。
        InputData 必须是 JSON 双编码字符串（json.dumps(inputs)）。
        结果从 response["output"] 读取，可能是纯文本或 JSON 字符串。
        """
        url = self.base_url + "sync_run_app_workflow"
        data = {
            "UserID":    self.user_id,
            "InputData": json.dumps(inputs, ensure_ascii=False),
            "NoDebug":   True,
        }
        try:
            resp = requests.post(
                url, headers=self._get_headers(), json=data, timeout=120
            )
            if not resp.ok:
                body = ""
                try:    body = resp.json()
                except: body = resp.text[:300]
                print(f"[run_workflow] {resp.status_code} | {body}")
                return {"thought": "", "reply": "工作流调用失败", "conversation_id": ""}

            result = resp.json()
            print(f"[run_workflow] 原始响应: {str(result)[:300]}")

            if result.get("status") != "success":
                msg = result.get("message", "未知错误")
                print(f"[run_workflow] 工作流失败: {msg}")
                return {"thought": "", "reply": f"工作流错误: {msg}", "conversation_id": ""}

            output_raw = result.get("output", "")
            parsed = self._parse_workflow_output(output_raw)
            return {
                "conversation_id":    result.get("runId", ""),
                "thought":            "",
                "reply":              parsed["emotional_response"],
                "emotional_response": parsed["emotional_response"],
                "weekly_summary":     parsed["weekly_summary"],
            }
        except Exception as e:
            print(f"[run_workflow] 异常: {e}")
            return {"thought": "", "reply": f"工作流请求崩溃: {e}", "conversation_id": ""}

    def _parse_workflow_output(self, output_raw: str) -> dict:
        """
        结束节点 output 可能多层嵌套 JSON，递归解包。
        返回 {"emotional_response": "...", "weekly_summary": "..."}
        """
        def extract(val) -> str:
            if not isinstance(val, str):
                return str(val).strip()
            try:
                inner = json.loads(val)
                if isinstance(inner, dict):
                    for key in ("response", "result", "output", "content", "text"):
                        if inner.get(key):
                            return extract(inner[key])
                    return "\n\n".join(extract(v) for v in inner.values() if v)
                return extract(inner)
            except (json.JSONDecodeError, TypeError):
                return val.strip()

        emotional, weekly = "", ""
        try:
            top = json.loads(output_raw)
            if isinstance(top, dict):
                emotional = extract(top.get("emotional_response", ""))
                weekly    = extract(top.get("weekly_summary", ""))
        except (json.JSONDecodeError, TypeError):
            emotional = extract(output_raw)

        return {"emotional_response": emotional, "weekly_summary": weekly}
