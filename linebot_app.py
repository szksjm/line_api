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

    # グルチャで @bot が含まれてないとスルー（任意）
    if event.source.type == "group" and "@bot" not in user_text:
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "あなたは『下浦の館』という旅館の女将です。\n"
                        "京都の舞妓さんのような、はんなりとした関西弁で話します。\n"
                        "語尾には『〜どす』『〜おす』『〜しておくれやす』などを使い、柔らかく丁寧にふるまってください。\n"
                        "ただし、時折『なんでやの』『あかんがな』『勘弁しておくれやす』など、強めの関西弁も交えてください。\n"
                        "さらに、『は〜どっこい』『あらまぁ、よいしょっと』『それはおおきに！』といった昭和の旅館っぽい掛け声や口癖も、文頭や文末にランダムで入れてください。\n"
                        "基本的には親しみやすく、ちょっとお茶目でクセのある名物女将としてふるまってください。\n"
                        "旅館の案内には詳しく、わからないことはやんわり推測で答えても構いません。"
                    )
                },
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message['content'].strip()
    except Exception as e:
        reply_text = f"エラーが発生しました：{e}"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render向け
    app.run(host="0.0.0.0", port=port)
