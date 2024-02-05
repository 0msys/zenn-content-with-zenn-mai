import streamlit as st
from openai import OpenAI
import os
import re
import tiktoken
from tiktoken.core import Encoding


def chat_reset():
    # チャット履歴をリセットする
    st.session_state.messages = []
    st.session_state.review_finished = False


def article_reset():
    # 記事をリセットする
    st.session_state.article_text = ""
    st.session_state.review_finished = False


def all_reset():
    # チャットと記事をリセットする
    chat_reset()
    article_reset()


@st.cache_data
def content_preview(content, show_raw_content):
    # コードブロックを検出する正規表現
    code_block_pattern = re.compile(r"```[\s\S]*?```")

    # コードブロックを抽出
    code_blocks = code_block_pattern.findall(content)

    # コードブロックを置き換えるための一時的なマーカーを生成
    code_marker = "<CODE_BLOCK>"
    marked_text = code_block_pattern.sub(code_marker, content)

    # コードブロックを含まない文章のリストを取得
    text_parts = marked_text.split(code_marker)

    # コードブロックと文章を元の順番通りに結合
    combined_list = []
    for text_part, code_block in zip(text_parts, code_blocks):
        combined_list.append(text_part)
        combined_list.append(code_block)

    # 最後の文章を追加
    combined_list.append(text_parts[-1])

    for part in combined_list:
        if not part:
            continue
        # 先頭行で特定のコードブロックを検出
        if part.startswith("```dot") or part.startswith("```graphviz"):
            if show_raw_content:
                st.code(part)
            else:
                st.graphviz_chart(
                    part.strip("```").replace("dot", "").replace("graphviz", "")
                )
        else:
            if show_raw_content:
                st.code(part)
            else:
                st.markdown(part)


st.set_page_config(
    page_title="ゼンマイちゃん", page_icon="images/zenn-mai-chan.jpg", layout="wide"
)

with st.sidebar:

    st.title("ゼンマイちゃん")

    st.image("images/zenn-mai-chan.jpg", use_column_width=True)

    # StreamlitのシークレットからOpenAIのAPIキーを設定する
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # チャット履歴を初期化する
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "review_finished" not in st.session_state:
        st.session_state.review_finished = False
    if "review_start" not in st.session_state:
        st.session_state.review_start = False

    st.radio(
        "モードを変更する", ["執筆支援", "レビュー"], key="mode", on_change=all_reset
    )

    st.selectbox(
        "OpenAIのモデルを選択する",
        [
            "gpt-3.5-turbo-0125",
            "gpt-4-0125-preview",
        ],
        key="openai_model",
        on_change=all_reset,
    )

    # システムプロンプトの用意
    system_prompt = ""
    prompt_path_dict = {
        "執筆支援": "src/prompts/support.md",
        "レビュー": "src/prompts/review.md",
    }

    # 記事を指定する
    article = st.text_input(
        "記事のslug(ファイル名)を入力してください", key="slug", on_change=all_reset
    ).replace(".md", "")

    if article:
        # 記事の存在確認
        if not os.path.exists(f"../articles/{article}.md"):
            st.error("指定された記事は存在しません")
            st.stop()

        # 記事を読み込む
        if st.button(
            "記事を読み込む",
            help="ファイルを更新を反映したい場合は再読み込みしてください",
            on_click=all_reset,
        ):
            with open(f"../articles/{article}.md", "r") as file:
                st.session_state.article_text = file.read()

        # 記事の読み込みチェック
        if not st.session_state.get("article_text"):
            st.error("記事を読み込んでください")
            st.stop()

        # 記事のタイトルを表示する
        title = (
            re.search(r"title: .*", st.session_state.article_text, re.MULTILINE)
            .group(0)
            .replace("title: ", "")
            .strip('" ')
        )
        st.caption(f"タイトル: {title}")

        # 記事のToken数を表示する
        encoding: Encoding = tiktoken.encoding_for_model(st.session_state.openai_model)
        token_count = len(encoding.encode(st.session_state.article_text))
        st.caption(f"Token数: {token_count}")

        # src/pronpts/にあるプロンプトファイルを読み込む
        with open(prompt_path_dict[st.session_state.mode], "r") as file:
            system_prompt = file.read()

        # system_prompt内の<ARTICLE>を記事の内容に置き換える
        system_prompt = system_prompt.replace(
            "<ARTICLE>", st.session_state.article_text
        )

        # レビューモードでは「レビューを開始する」を押すまで進まない
        if st.session_state.mode == "レビュー":
            st.button("レビューを開始する", key="review_start", on_click=chat_reset)
            if (
                not st.session_state.review_start
                and not st.session_state.review_finished
            ):
                st.stop()

        # メッセージを成形した形ではなく、そのまま表示するかどうかを選択する
        st.toggle("チャットのRaw表示", key="show_raw_content")


if system_prompt:

    # アプリを再実行した際にチャット履歴からメッセージを表示する
    for message in st.session_state.messages:
        with st.chat_message(
            message["role"],
            avatar=(
                "images/zenn-mai-chan.jpg" if message["role"] == "assistant" else None
            ),
        ):
            content_preview(message["content"], st.session_state.show_raw_content)

    # ユーザーの入力を受け付ける
    if (
        st.chat_input("何か質問はありますか？", key="chat_input")
        or st.session_state.review_start
    ):
        prompt = (
            "レビューをお願いします"
            if st.session_state.review_start
            else st.session_state.chat_input
        )
        # ユーザーのメッセージをチャット履歴に追加する
        st.session_state.messages.append({"role": "user", "content": prompt})
        # ユーザーのメッセージをチャットメッセージコンテナに表示する
        with st.chat_message("user"):
            st.markdown(prompt)
        # アシスタントの応答をチャットメッセージコンテナに表示する
        with st.chat_message("assistant", avatar="images/zenn-mai-chan.jpg"):
            message_placeholder = st.empty()
            full_response = ""

        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            with message_placeholder.container():
                content_preview(full_response + "▌", st.session_state.show_raw_content)

        with message_placeholder.container():
            content_preview(full_response, st.session_state.show_raw_content)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        if st.session_state.review_start:
            st.session_state.review_finished = True

    # チャット履歴をクリアする
    if st.button("🗑️", help="チャット履歴のクリア"):
        chat_reset()
        st.rerun()
