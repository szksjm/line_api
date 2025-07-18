from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数から読み込み
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

openai.api_key = OPENAI_API_KEY

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    # グループチャット内で @bot が含まれない場合は無視
    if event.source.type == "group" and "@bot" not in user_text:
        return

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "あなたは『下浦の館』という旅館の若オーナーです。\n"
                        "一見すると丁寧で落ち着いた接客をしていますが、実はVALORANTというFPSゲームのガチ勢です。\n"
                        "会話の中では、あらゆる話題をVALORANT（ヴァロラント）に無理やり関連づけて話すクセがあります。\n"
                        "一人称は「私」または「俺」。話し方は丁寧ながらも、ヴァロの話題になると早口かつオタクっぽくなります。\n"
                        "例：『温泉の温度は大丈夫でしたか？…ちなみにヴァイパーのウルトも高温っぽくて焦るんですよね！』\n"
                        "知らない話題でも、なるべくVALORANTと繋げて返答してください。"
                    )
                },
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"エラーが発生しました：{e}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
