import os
import streamlit as st
from openai import OpenAI

# Renderの設定画面（Environment）から直接APIキーを読み込みます
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ APIキーが設定されていません。RenderのEnvironment設定を確認してください。")
    st.stop()

client = OpenAI(api_key=api_key)

# アプリのタイトルと設定
st.title("💬 AIチャットインタビュー")
st.caption("あなたの考えやエピソードをAIが深掘りします。")

MAX_QUESTIONS = 5  # インタビューの最大質問回数

# セッション状態（会話の記憶）の初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "あなたはプロのインタビュアーです。ユーザーの本音や具体的なエピソードを引き出すのが目的です。"
                "1回の発言につき、質問は必ず「1つ」に絞ってください。"
                "フレンドリーかつ丁寧なトーンで、ユーザーの回答を肯定しつつ、さらに深く掘り下げる質問をしてください。"
            )
        },
        {
            "role": "assistant",
            "content": "こんにちは！本日はインタビューにお時間をいただきありがとうございます。早速ですが、あなたが今一番情熱を注いでいることについて教えていただけますか？"
        }
    ]

# 現在の質問回数をカウント
user_reply_count = sum(1 for m in st.session_state.messages if m["role"] == "user")

# 過去のチャット履歴を画面に表示
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# インタビュー進行ロジック
if user_reply_count < MAX_QUESTIONS:
    if user_input := st.chat_input("ここに回答を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        current_count = user_reply_count + 1

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                if current_count >= MAX_QUESTIONS:
                    st.session_state.messages.append({
                        "role": "system",
                        "content": "これでインタビューは終了です。これまでのユーザーの回答を総合的に分析し、彼らの強みや特徴をポジティブにまとめた「インタビューレポート」を作成して、感謝の言葉とともに締めくくってください。"
                    })
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                output_text = response.choices[0].message.content
                
                st.session_state.messages.append({"role": "assistant", "content": output_text})
                st.write(output_text)
                
                if current_count >= MAX_QUESTIONS:
                    st.rerun()
else:
    st.success("🎉 インタビューが終了しました！お疲れ様でした。")
    if st.button("もう一度最初から始める"):
        st.session_state.clear()
        st.rerun()