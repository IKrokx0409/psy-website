import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class HiAgentClient:
    def __init__(self):
        self.api_key = os.getenv("HITSZ_API_KEY")
        # HITSZ 2.0 代理网关路径
        self.base_url = "http://zhiwen.hitsz.edu.cn:10211/api/proxy/api/v1/"
        self.user_id = "ikrokx_001"

    def _get_headers(self, is_chat=False):
        headers = {
            'Apikey': self.api_key,
            'Content-Type': 'application/json'
        }
        if is_chat:
            # 聊天接口声明接收流式
            headers['Accept'] = 'text/event-stream'
        return headers

    def create_conversation(self) -> str:
        """step1：创建会话"""
        url = self.base_url + "create_conversation"
        data = {
            "UserID": self.user_id,
            "Inputs": {}
        }
        try:
            response = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            # 返回逻辑：result -> Conversation -> AppConversationID
            return result.get("Conversation", {}).get("AppConversationID")
        except Exception as e:
            print(f"会话创建失败: {e}")
            return None

    def ask_ai(self, prompt: str, conversation_id: str = None):
        """step2：发起请求并解析流数据"""
        conv_id = conversation_id or self.create_conversation()
        if not conv_id:
            return {"thought": "", "reply": "系统初始化失败"}

        url = self.base_url + "chat_query_v2"
        data = {
            "UserID": self.user_id,
            "AppConversationID": conv_id,
            "Query": prompt,
            "ResponseMode": "streaming"
        }

        try:
            # 开启流式读取
            response = requests.post(
                url, 
                headers=self._get_headers(is_chat=True), 
                json=data, 
                stream=True, 
                timeout=60
            )
            
            thought_acc = ""
            reply_acc = ""

            for line in response.iter_lines():
                if not line:
                    continue
                
                decoded_line = line.decode('utf-8').strip()
                
                # chat_query_v2 标准 SSE 格式：data: {...}
                if decoded_line.startswith("data:"):
                    try:
                        json_str = decoded_line[len("data:"):].strip()
                        if json_str == "[DONE]":
                            break
                        
                        json_data = json.loads(json_str)
                        event_type = json_data.get("event") # 事件类型
                        content = json_data.get("answer", "") # 内容片段

                        # 分流逻辑
                        if event_type == "think_message":
                            # 属于 AI 的思考过程
                            thought_acc += content
                        elif event_type == "message":
                            # 属于正式给用户的回答
                            reply_acc += content
                            
                    except (json.JSONDecodeError, IndexError):
                        continue

            # ✨ 返回字典结构，方便前端区分
            return {
                "conversation_id": conv_id,
                "thought": thought_acc.strip(),
                "reply": reply_acc.strip() if reply_acc else "AI 响应解析异常"
            }
            
        except Exception as e:
            return {"thought": "", "reply": f"请求崩溃: {str(e)}"}