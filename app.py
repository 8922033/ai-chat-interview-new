import streamlit as st
from openai import OpenAI

# 1. APIキーの自動取得
# `.streamlit/secrets.toml` に保存したキーを自動的に読み込みます。
# これにより、コードの中に直接大切なキーを書かずに済み、安全です。
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ APIキーが見つかりません。`.streamlit/secrets.toml` ファイルを作成してキーを設定してください。")
    st.stop()

client = OpenAI(api_key=api_key)

# 2. アプリのタイトルと設定
st.title("💬 AIチャットインタビュー")
st.caption("あなたの考えやエピソードをAIが深掘りします。")

MAX_QUESTIONS = 5  # インタビューの最大質問回数

# 3. セッション状態（会話の記憶）の初期化
if "messages" not in st.session_state:
    # AIのキャラクターや役割（プロンプト）を設定
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

# 4. 現在の質問回数をカウント（ユーザーの発言回数ベース）
user_reply_count = sum(1 for m in st.session_state.messages if m["role"] == "user")

# 5. 過去のチャット履歴を画面に表示
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 6. インタビュー進行ロジック
if user_reply_count < MAX_QUESTIONS:
    # 規定回数未満なら、画面下部に入力欄を表示する
    if user_input := st.chat_input("ここに回答を入力してください..."):
        # ユーザーの発言を追加・表示
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # ユーザーの返信数が上限に達したかチェック
        current_count = user_reply_count + 1

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                if current_count >= MAX_QUESTIONS:
                    # 最後の質問が終わったら、まとめを要求する指示を裏で追加する
                    st.session_state.messages.append({
                        "role": "system",
                        "content": "これでインタビューは終了です。これまでのユーザーの回答を総合的に分析し、彼らの強みや特徴をポジティブにまとめた「インタビューレポート」を作成して、感謝の言葉とともに締めくくってください。"
                    })
                
                # OpenAI APIを呼び出してAIの返答を取得
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                output_text = response.choices[0].message.content
                
                # AIの発言を追加・表示
                st.session_state.messages.append({"role": "assistant", "content": output_text})
                st.write(output_text)
                
                # 終了した場合は画面をリフレッシュして入力欄を閉じる
                if current_count >= MAX_QUESTIONS:
                    st.rerun()
else:
    # インタビュー終了後の表示
    st.success("🎉 インタビューが終了しました！お疲れ様でした。")
    if st.button("もう一度最初から始める"):
        st.session_state.clear()
        st.rerun()