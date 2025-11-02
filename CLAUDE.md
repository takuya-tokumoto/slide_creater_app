# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A web application that generates PowerPoint presentations from ES (Entry Sheet / 自己PR) text input. Users input their content, an AI-like logic generates a slide structure, and users can refine it through chat before exporting to PPTX format. The entire application runs locally without external databases or cloud services.

## Architecture

### Backend (Python + FastAPI)

**Location:** `main.py`

**Core responsibilities:**
- Slide structure generation from ES input (`/generate`)
- Slide editing via chat prompts (`/patch`)
- PPTX file generation (`/export`)
- Serving static HTML/CSS/JS files

**Key libraries:**
- `fastapi` - Web framework
- `python-pptx` - PowerPoint file generation
- `pydantic` - Data validation and models
- `uvicorn` - ASGI server

**Data Models:**
- `Section`: ES input unit (title + content)
- `Slide`: Single slide (title + bullet points list)
- `SlidesState`: Collection of slides

**State Management:**
- All state is managed server-side
- Frontend sends complete slide arrays with each request
- Server returns updated slide arrays after modifications
- No persistent database - in-memory only

### Frontend (Static HTML/CSS/JS)

**Files:**
- `static/index.html` - ES input form (page 1)
- `static/slides.html` - Slide preview and chat editor (page 2)
- `static/style.css` - Shared styles

**State Flow:**
1. User inputs ES sections on `index.html`
2. POST to `/generate` returns initial slides
3. Slides stored in `localStorage` and navigate to `slides.html`
4. User edits via chat or direct manipulation
5. Chat edits POST to `/patch` with current slides + prompt
6. Export button POST to `/export` triggers PPTX download

**No Framework:** Vanilla JavaScript only - state management through localStorage and direct DOM manipulation

## Development Commands

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run development server
```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

### Access the application
Open browser to `http://127.0.0.1:8000`

## Key Design Decisions

### 1. Server-Side State Management
All slide modifications happen server-side. Frontend always sends the complete current state and receives the complete new state. This simplifies the architecture but means:
- Each `/patch` request includes all slides
- Server logic is stateless between requests
- Easy to extend with proper AI/LLM integration later

### 2. Chat Prompt Parsing (main.py:95-135)
The `/patch` endpoint uses simple keyword matching for MVP:
- "削除" / "delete" → removes last slide
- "追加" / "add" → adds new slide
- Pattern matching for title changes ("タイトル" + "変更")
- Default: appends prompt content to last slide

**Future extension point:** Replace with MCP or skills interface

### 3. Slide Generation Logic (main.py:66-93)
The `/generate` endpoint uses rule-based logic:
- First section → title slide
- Each section with content → content slide (max 5 bullets)
- Automatic bullet point extraction from paragraph text
- Final "まとめ" (summary) slide added automatically

**Future extension point:** Replace with LLM-based generation

### 4. File Structure
```
main.py                    # Single backend file (FastAPI app + all logic)
static/
  ├── index.html          # Page 1: ES input form
  ├── slides.html         # Page 2: Preview + chat editor
  └── style.css           # Shared styles
exports/                   # Generated PPTX files (gitignored)
```

### 5. PPTX Generation (main.py:138-177)
Uses `python-pptx` with:
- Standard slide size: 10×7.5 inches
- Layout: Title and Content (layout index 1)
- Each slide: title + bulleted list
- Files saved with UUID prefix to `exports/` directory

## Common Development Patterns

### Adding a new slide generation rule
Edit `generate_slides()` function in `main.py:66-93`

### Extending chat commands
Edit `patch_slides()` function in `main.py:95-135`

### Modifying slide layout/styling
Edit PPTX generation in `export_pptx()` function in `main.py:138-177`

### Changing UI layout
- ES form: `static/index.html`
- Preview/chat: `static/slides.html`
- Styles: `static/style.css`

## Future Extension Points

### MCP/Skills Integration
The `/patch` and `/generate` endpoints are designed to be replaceable:
- `/generate`: Can delegate to MCP server for AI-powered structure generation
- `/patch`: Can delegate to skills for natural language understanding

Current implementation provides clear I/O contracts (Pydantic models) that external systems can implement.

### Planned Enhancements
- Replace keyword matching with LLM-based editing
- Add slide templates and themes
- Support image insertion
- Multi-language support

## Important Files Reference

- `main.py:66-93` - Slide generation logic
- `main.py:95-135` - Chat-based editing logic
- `main.py:138-177` - PPTX export logic
- `static/slides.html:93-180` - Client-side slide rendering
- `static/slides.html:226-257` - Chat message handling

## Testing Notes

Currently no automated tests. Manual testing workflow:
1. Start server: `python main.py`
2. Navigate to `http://127.0.0.1:8000`
3. Input ES content with 2-3 sections
4. Verify slide generation
5. Test chat commands (add, delete)
6. Test direct editing (title, bullets)
7. Test PPTX export and verify file opens in PowerPoint
