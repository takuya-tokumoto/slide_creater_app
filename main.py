"""
スライド作成アプリ - FastAPI Backend
ES入力 → AI構成案生成 → チャット編集 → PPTX出力
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
import os
import uuid
from datetime import datetime
from anthropic import Anthropic
import json
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

app = FastAPI(title="Slide Creator App")

# 静的ファイル配信
app.mount("/static", StaticFiles(directory="static"), name="static")

# エクスポートディレクトリ
EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

# Anthropic クライアント初期化
anthropic_client = None
try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and api_key != "your_api_key_here":
        anthropic_client = Anthropic(api_key=api_key)
except Exception as e:
    print(f"Warning: Anthropic client initialization failed: {e}")
    print("Falling back to rule-based slide generation")


# データモデル
class Section(BaseModel):
    """ES入力のセクション"""
    title: str
    content: str


class Slide(BaseModel):
    """スライド構成"""
    title: str
    bullets: List[str]


class SlidesState(BaseModel):
    """スライド群の状態"""
    slides: List[Slide]


class GenerateRequest(BaseModel):
    """構成案生成リクエスト"""
    sections: List[Section]


class PatchRequest(BaseModel):
    """差分編集リクエスト"""
    slides: List[Slide]
    prompt: str


class ExportRequest(BaseModel):
    """PPTX出力リクエスト"""
    slides: List[Slide]


# ルートエンドポイント
@app.get("/")
async def root():
    """ES入力フォームページを返す"""
    return FileResponse("static/index.html")


async def generate_slides_with_llm(sections: List[Section]) -> List[Slide]:
    """
    LLMを使用してスライド構成を生成
    """
    # セクション情報を整形
    sections_text = "\n\n".join([
        f"【{section.title}】\n{section.content}"
        for section in sections
    ])

    prompt = f"""以下の自己PR・ES情報から、効果的なプレゼンテーションスライドの構成を作成してください。

# 入力情報
{sections_text}

# スライド構造の要件
各スライドは以下の構造にしてください：

**メッセージライン（必須・太字表示）:**
- bullets[0]: 1行のメッセージライン（40文字以内）
  - このスライドで伝えたい核心メッセージを簡潔に表現
  - 事実と示唆を統合した形で記述（「〇〇なので△△が必要」など）
  - プレフィックス（「事実:」「示唆:」など）は不要

**ボディ部分（メッセージラインを裏付ける詳細）:**
- bullets[1以降]: メッセージラインの内容を補足・説明・裏付ける具体的な箇条書き（3-5個）
  - メッセージの根拠となるデータや背景情報
  - 具体的な事例や詳細説明
  - 行動項目や検討ポイント

# 出力形式
以下のJSON配列形式で返してください：

```json
[
  {{
    "title": "スライドのタイトル",
    "bullets": [
      "核心メッセージを1行で表現（プレフィックスなし）",
      "メッセージを裏付ける背景情報",
      "具体的なデータや事例",
      "詳細な説明や分析",
      "行動項目や検討ポイント"
    ]
  }}
]
```

# 全体要件
1. 最初のスライドはタイトルスライドにする（メッセージラインで全体の目的を明示）
2. 各スライドは4-6個の箇条書き（メッセージライン1行 + ボディ3-5行）
3. 最後にまとめスライドを追加（メッセージラインで結論と次アクション）
4. 全体で5-8枚程度のスライドにする
5. 情報を適切にグループ化し、ストーリー性を持たせる
6. ボディ部分は必ずメッセージラインの内容を具体化・裏付けするものにする

JSON配列のみを返してください（説明文は不要）。"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # レスポンスからJSONを抽出
        content = response.content[0].text

        # ```json ``` で囲まれている場合は抽出
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # JSONをパース
        slides_data = json.loads(content)

        # Slideオブジェクトに変換
        slides = [Slide(**slide) for slide in slides_data]
        return slides

    except Exception as e:
        print(f"LLM generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"スライド生成中にエラーが発生しました: {str(e)}"
        )


@app.post("/generate")
async def generate_slides(request: GenerateRequest) -> SlidesState:
    """
    ES入力から構成案を生成（LLMのみ使用）
    """
    if not anthropic_client:
        raise HTTPException(
            status_code=500,
            detail="Anthropic API キーが設定されていません。.envファイルにANTHROPIC_API_KEYを設定してください。"
        )

    slides = await generate_slides_with_llm(request.sections)
    return SlidesState(slides=slides)


@app.post("/patch")
async def patch_slides(request: PatchRequest) -> SlidesState:
    """
    チャット入力でスライドを編集
    簡易実装：プロンプトに応じた操作を解析
    """
    slides = request.slides.copy()
    prompt = request.prompt.lower()

    # プロンプト解析（簡易版）
    if "削除" in prompt or "消して" in prompt or "delete" in prompt:
        # 最後のスライドを削除（タイトル以外）
        if len(slides) > 1:
            slides.pop()

    elif "追加" in prompt or "add" in prompt:
        # 新しいスライドを追加
        slides.append(Slide(
            title="新しいスライド",
            bullets=["内容を編集してください"]
        ))

    elif "タイトル" in prompt and "変更" in prompt:
        # 最初のスライドのタイトルを変更
        if slides and "→" in prompt:
            new_title = prompt.split("→")[1].strip()
            slides[0].title = new_title

    elif "箇条書き" in prompt or "内容" in prompt:
        # 箇条書きを追加
        if len(slides) > 1:
            new_bullet = prompt.replace("箇条書き", "").replace("追加", "").strip()
            if new_bullet:
                slides[-1].bullets.append(new_bullet)

    else:
        # デフォルト：最後のスライドに内容を追加
        if slides:
            slides[-1].bullets.append(f"💡 {request.prompt}")

    return SlidesState(slides=slides)


@app.post("/export")
async def export_pptx(request: ExportRequest) -> dict:
    """
    PPTXファイルを生成してダウンロードURLを返す
    """
    # プレゼンテーション作成
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    for slide_data in request.slides:
        # タイトルと内容のレイアウト
        slide_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(slide_layout)

        # タイトル設定
        title = slide.shapes.title
        title.text = slide_data.title

        # 箇条書き設定
        if slide_data.bullets:
            body = slide.placeholders[1]
            text_frame = body.text_frame
            text_frame.clear()

            for i, bullet in enumerate(slide_data.bullets):
                if i == 0:
                    text_frame.text = bullet
                    run = text_frame.paragraphs[0].runs[0]
                    run.font.bold = True  # 1行目（メッセージライン）を太字
                else:
                    p = text_frame.add_paragraph()
                    p.text = bullet
                    p.level = 0

    # ファイル保存
    filename = f"slide_{uuid.uuid4().hex[:8]}.pptx"
    filepath = os.path.join(EXPORT_DIR, filename)
    prs.save(filepath)

    return {
        "download_url": f"/download/{filename}",
        "filename": filename
    }


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    生成されたPPTXファイルをダウンロード
    """
    filepath = os.path.join(EXPORT_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")

    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=filename
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
