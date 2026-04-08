import os
import json
import requests
from dotenv import load_dotenv

# 1. 确保精准加载保险箱（再次检查你的 .env 别加空格哦！）
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

api_key = os.getenv("HITSZ_API_KEY")
# 注意：这里用你 2.0 截图里的最新 APPID
app_id = "d775cuqut43chqmqv8vg" 

# 2.0 官方 Proxy 路径
url = "http://zhiwen.hitsz.edu.cn:10211/api/proxy/api/v1/chat_query"

# 方案：海陆空全方位轰炸，确保 AppID 无处不在
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-App-Id": app_id,   # 1.0 时代的暗号
    "AppID": app_id       # 备选暗号
}

params = {
    "AppID": app_id       # 2. 挂在 URL 后面（这是火山引擎网关最喜欢的姿势）
}

payload = {
    "Query": "先遣兵请求通话！2.0 平台能收到吗？",
    "AppID": app_id       # 3. 塞进信件内容里
}

print(f"🕵️‍♂️ 先遣兵正在出发，目标坐标: {url}")
print(f"使用 AppID: {app_id}")

try:
    # 模拟流式请求，因为平台回信是一个字一个字蹦的
    response = requests.post(
        url, 
        json=payload, 
        headers=headers, 
        params=params, 
        stream=True,
        timeout=15
    )

    print(f"📡 响应状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ 任务失败，服务器原话: {response.text}")
    else:
        print("✅ 连通成功！正在解码回信...")
        full_reply = ""
        # 像剥洋葱一样解析 data:data: 格式
        for line in response.iter_lines():
            if line:
                line_text = line.decode("utf-8")
                if "data:data:" in line_text:
                    try:
                        # 提取 JSON 部分
                        json_str = line_text.split("data:data:")[1].strip()
                        data_dict = json.loads(json_str)
                        # 只有 event 为 message 时才是 AI 说的台词
                        if data_dict.get("event") == "message":
                            answer = data_dict.get("answer", "")
                            print(answer, end="", flush=True) # 实时打印打字机效果
                            full_reply += answer
                    except:
                        continue
        print("\n\n🎉 任务圆满完成，拿到完整回复！")

except Exception as e:
    print(f"💥 先遣兵半路失踪（网络错误）: {str(e)}")