# AI Outfit

This version includes a Python backend so the project can be demoed as a small full-stack app.

## Stack

- Frontend: plain HTML, CSS, JavaScript
- Backend: Python standard library HTTP server
- Storage: local JSON file for saved outfits
- AI image call: backend proxy to OpenAI Images API

## Features

- Inventory area
- Drag-and-drop styling canvas
- Prompt assembly
- Saved outfit list
- Python API endpoints for items, outfits, and image generation

## Run

Use Python 3.10+.

```bash
python server.py
```

Then open:

```text
http://127.0.0.1:8000
```

## API endpoints

- `GET /api/items`
- `GET /api/outfits`
- `POST /api/outfits`
- `POST /api/generate`

## Demo flow

1. Start the Python server.
2. Open the app in the browser.
3. Drag items from the inventory to the canvas.
4. Add style notes.
5. Save the outfit.
6. Add an OpenAI API key and generate an image.

If no API key is provided, the backend returns a demo message so you can still present the workflow.
