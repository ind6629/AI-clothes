from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
from urllib.parse import quote


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
OUTFITS_FILE = DATA_DIR / "outfits.json"
ITEMS_FILE = DATA_DIR / "items.json"


def garment_image(title: str, color: str, accent: str, kind: str) -> str:
    shape_map = {
        "top": f'<rect x="118" y="120" width="164" height="130" rx="28" fill="{color}"/><rect x="88" y="125" width="54" height="102" rx="24" fill="{color}"/><rect x="258" y="125" width="54" height="102" rx="24" fill="{color}"/><rect x="152" y="96" width="96" height="42" rx="20" fill="{accent}"/>',
        "shirt": f'<rect x="112" y="108" width="176" height="148" rx="18" fill="{color}"/><path d="M150 104h100l22 36-34 28H162l-34-28z" fill="{accent}"/><rect x="194" y="118" width="12" height="136" rx="6" fill="#f7f1ea"/>',
        "pants": f'<path d="M132 92h136l18 208h-68l-14-116h-16l-14 116h-68z" fill="{color}"/><path d="M132 92h136l-14 58H146z" fill="{accent}" opacity="0.72"/>',
        "skirt": f'<path d="M148 104h104l42 190H106z" fill="{color}"/><rect x="148" y="92" width="104" height="28" rx="14" fill="{accent}"/><path d="M170 120v152M200 120v164M230 120v152" stroke="#f6eee6" stroke-width="10" opacity="0.36"/>',
        "jacket": f'<rect x="108" y="110" width="184" height="156" rx="24" fill="{color}"/><rect x="98" y="122" width="58" height="118" rx="26" fill="{color}"/><rect x="244" y="122" width="58" height="118" rx="26" fill="{color}"/><path d="M154 108h92l24 34-36 34h-48l-36-34z" fill="{accent}"/>',
        "blazer": f'<rect x="118" y="106" width="164" height="160" rx="24" fill="{color}"/><path d="M164 106h72l30 56-46 28-18-32-18 32-46-28z" fill="{accent}"/><rect x="194" y="146" width="12" height="116" rx="6" fill="#d4c2aa"/>',
        "boots": f'<path d="M112 156h72v92c0 24-18 44-42 44h-30z" fill="{color}"/><path d="M216 156h72v92c0 24-18 44-42 44h-30z" fill="{color}"/><rect x="100" y="280" width="100" height="26" rx="13" fill="{accent}"/><rect x="204" y="280" width="100" height="26" rx="13" fill="{accent}"/>',
        "sneaker": f'<path d="M92 236h120l44 36h54c16 0 28 12 28 26v8H92z" fill="{color}"/><path d="M112 254h86l26 18" stroke="{accent}" stroke-width="10" stroke-linecap="round"/><rect x="86" y="302" width="254" height="12" rx="6" fill="#d8cdc0"/>',
        "tote": f'<rect x="118" y="122" width="164" height="156" rx="24" fill="{color}"/><path d="M152 138c0-34 18-52 48-52s48 18 48 52" fill="none" stroke="{accent}" stroke-width="14" stroke-linecap="round"/>',
        "shoulder": f'<rect x="116" y="150" width="168" height="112" rx="32" fill="{color}"/><path d="M146 154c10-44 42-70 88-70 34 0 58 14 76 42" fill="none" stroke="{accent}" stroke-width="14" stroke-linecap="round"/>',
        "earring": f'<circle cx="156" cy="154" r="34" fill="{accent}"/><circle cx="244" cy="154" r="34" fill="{accent}"/><circle cx="156" cy="234" r="48" fill="{color}"/><circle cx="244" cy="234" r="48" fill="{color}"/>',
        "belt": f'<rect x="84" y="176" width="252" height="44" rx="22" fill="{color}"/><rect x="132" y="162" width="64" height="72" rx="12" fill="{accent}"/><rect x="148" y="178" width="32" height="40" rx="8" fill="#f7f1ea"/>',
    }
    shape = shape_map[kind]
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
      <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fdf8f2"/>
          <stop offset="100%" stop-color="#efe1d4"/>
        </linearGradient>
      </defs>
      <rect width="400" height="400" rx="36" fill="url(#bg)"/>
      <circle cx="322" cy="78" r="34" fill="{accent}" opacity="0.12"/>
      <rect x="38" y="36" width="324" height="328" rx="28" fill="#fffdfa"/>
      {shape}
      <text x="40" y="346" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#3d2f29">{title}</text>
      <text x="40" y="374" font-family="Arial, sans-serif" font-size="16" fill="#8d7a6d">demo display image</text>
    </svg>
    """.strip()
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


INVENTORY = [
    {"id": "top-01", "name": "Cream Knit Top", "category": "tops", "categoryLabel": "Top", "desc": "soft texture for smart casual looks", "badge": "T", "color": "#d18b57", "imageUrl": garment_image("Cream Knit Top", "#d8b18c", "#b68154", "top")},
    {"id": "top-02", "name": "Blue Structured Shirt", "category": "tops", "categoryLabel": "Top", "desc": "clean office-ready silhouette", "badge": "S", "color": "#6887a7", "imageUrl": garment_image("Blue Shirt", "#8aa7c2", "#5b7f9f", "shirt")},
    {"id": "bottom-01", "name": "Wide Tailored Trousers", "category": "bottoms", "categoryLabel": "Bottom", "desc": "elongated leg line and refined shape", "badge": "P", "color": "#705b50", "imageUrl": garment_image("Tailored Trousers", "#857366", "#6b584c", "pants")},
    {"id": "bottom-02", "name": "Dusty Pleated Skirt", "category": "bottoms", "categoryLabel": "Bottom", "desc": "light movement and feminine finish", "badge": "K", "color": "#ba7f76", "imageUrl": garment_image("Pleated Skirt", "#c9a49c", "#ab7268", "skirt")},
    {"id": "outer-01", "name": "Short Utility Jacket", "category": "outerwear", "categoryLabel": "Outerwear", "desc": "layered autumn styling", "badge": "J", "color": "#9b7247", "imageUrl": garment_image("Utility Jacket", "#a98762", "#7f5e3d", "jacket")},
    {"id": "outer-02", "name": "Ivory Blazer", "category": "outerwear", "categoryLabel": "Outerwear", "desc": "sharp polished business look", "badge": "B", "color": "#ccb48c", "imageUrl": garment_image("Ivory Blazer", "#ded0b6", "#bca682", "blazer")},
    {"id": "shoe-01", "name": "Pointed Ankle Boots", "category": "shoes", "categoryLabel": "Shoes", "desc": "city-focused shape with presence", "badge": "H", "color": "#4f4847", "imageUrl": garment_image("Ankle Boots", "#5a524f", "#383231", "boots")},
    {"id": "shoe-02", "name": "White Trainer", "category": "shoes", "categoryLabel": "Shoes", "desc": "relaxed everyday street styling", "badge": "R", "color": "#8c8d81", "imageUrl": garment_image("White Trainer", "#b8b8ae", "#909184", "sneaker")},
    {"id": "bag-01", "name": "Caramel Tote", "category": "bags", "categoryLabel": "Bag", "desc": "practical volume with mature tone", "badge": "G", "color": "#a65632", "imageUrl": garment_image("Caramel Tote", "#bb744d", "#8d4829", "tote")},
    {"id": "bag-02", "name": "Black Shoulder Bag", "category": "bags", "categoryLabel": "Bag", "desc": "compact and crisp for office wear", "badge": "B", "color": "#272524", "imageUrl": garment_image("Shoulder Bag", "#44403f", "#24211f", "shoulder")},
    {"id": "acc-01", "name": "Pearl Earrings", "category": "accessories", "categoryLabel": "Accessory", "desc": "clean face-brightening detail", "badge": "A", "color": "#d6c0a4", "imageUrl": garment_image("Pearl Earrings", "#eadfce", "#c7b59b", "earring")},
    {"id": "acc-02", "name": "Metal Belt", "category": "accessories", "categoryLabel": "Accessory", "desc": "defines the waist and adds finish", "badge": "M", "color": "#8f7846", "imageUrl": garment_image("Metal Belt", "#a69262", "#776238", "belt")},
]

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}


def ensure_outfits_file() -> None:
    if not OUTFITS_FILE.exists():
        OUTFITS_FILE.write_text("[]", encoding="utf-8")


def ensure_items_file() -> None:
    if not ITEMS_FILE.exists():
        ITEMS_FILE.write_text(json.dumps(INVENTORY, ensure_ascii=False, indent=2), encoding="utf-8")


def load_outfits() -> list[dict]:
    ensure_outfits_file()
    try:
        return json.loads(OUTFITS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_outfits(outfits: list[dict]) -> None:
    OUTFITS_FILE.write_text(json.dumps(outfits, ensure_ascii=False, indent=2), encoding="utf-8")


def load_items() -> list[dict]:
    ensure_items_file()
    try:
        return json.loads(ITEMS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return INVENTORY.copy()


def save_items(items: list[dict]) -> None:
    ITEMS_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def category_label(category: str) -> str:
    labels = {
        "tops": "Top",
        "bottoms": "Bottom",
        "outerwear": "Outerwear",
        "shoes": "Shoes",
        "bags": "Bag",
        "accessories": "Accessory",
    }
    return labels.get(category, "Item")


def category_badge(category: str) -> str:
    badges = {
        "tops": "T",
        "bottoms": "B",
        "outerwear": "O",
        "shoes": "S",
        "bags": "G",
        "accessories": "A",
    }
    return badges.get(category, "I")


class OutfitDemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/items":
            self.send_json({"items": load_items()})
            return

        if self.path == "/api/outfits":
            self.send_json({"outfits": load_outfits()})
            return

        if self.path in STATIC_FILES:
            file_name, content_type = STATIC_FILES[self.path]
            self.serve_file(BASE_DIR / file_name, content_type)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        if self.path == "/api/items":
            payload = self.read_json()
            if not payload.get("name") or not payload.get("imageUrl"):
                self.send_json({"error": "name and imageUrl are required"}, status=HTTPStatus.BAD_REQUEST)
                return

            items = load_items()
            item = {
                "id": f"uploaded-{len(items) + 1}",
                "name": payload.get("name", "Uploaded Item"),
                "category": payload.get("category", "tops"),
                "categoryLabel": category_label(payload.get("category", "tops")),
                "desc": payload.get("desc", "uploaded garment photo"),
                "badge": category_badge(payload.get("category", "tops")),
                "color": "#8a6f54",
                "imageUrl": payload.get("imageUrl"),
            }
            items.insert(0, item)
            save_items(items)
            self.send_json({"ok": True, "items": items})
            return

        if self.path == "/api/outfits":
            payload = self.read_json()
            outfits = load_outfits()
            outfit = {
                "name": payload.get("name", "Untitled Outfit"),
                "summary": payload.get("summary", ""),
                "stylingPrompt": payload.get("stylingPrompt", ""),
                "items": payload.get("items", []),
            }
            outfits.insert(0, outfit)
            save_outfits(outfits[:10])
            self.send_json({"ok": True, "outfits": load_outfits()})
            return

        if self.path == "/api/generate":
            payload = self.read_json()
            api_key = payload.get("apiKey") or os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                self.send_json(
                    {
                        "ok": True,
                        "demo_message": "Backend is running. Add an API key to enable real image generation.",
                    }
                )
                return

            try:
                reference_images = payload.get("referenceImages") or []
                model_image = payload.get("modelImage", "")
                if reference_images or model_image:
                    image_url = generate_image_with_references(
                        api_key=api_key,
                        model=payload.get("model", "gpt-image-1"),
                        prompt=payload.get("prompt", ""),
                        reference_images=reference_images,
                        model_image=model_image,
                    )
                else:
                    image_url = generate_image(
                        api_key=api_key,
                        model=payload.get("model", "gpt-image-1"),
                        prompt=payload.get("prompt", ""),
                    )
            except RuntimeError as exc:
                self.send_json({"error": str(exc)}, status=HTTPStatus.BAD_GATEWAY)
                return

            self.send_json({"ok": True, "image_url": image_url})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_common_headers()
        self.end_headers()

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_common_headers(content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_common_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_common_headers(self, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def log_message(self, format: str, *args) -> None:
        return


def generate_image(api_key: str, model: str, prompt: str) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "size": "1024x1536"}).encode("utf-8")
    http_request = request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=60) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI request failed: HTTP {exc.code} {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc

    first = (body.get("data") or [{}])[0]
    if first.get("b64_json"):
        return "data:image/png;base64," + first["b64_json"]
    if first.get("url"):
        return first["url"]
    raise RuntimeError("OpenAI response did not include an image.")


def generate_image_with_references(
    api_key: str,
    model: str,
    prompt: str,
    reference_images: list[dict],
    model_image: str = "",
) -> str:
    content = [{"type": "input_text", "text": prompt}]

    if model_image:
        content.append({"type": "input_text", "text": "Primary person reference image. Preserve identity, pose, and framing as much as possible."})
        content.append(
            {
                "type": "input_image",
                "image_url": model_image,
                "detail": "high",
            }
        )

    for image in reference_images[:6]:
        image_url = image.get("imageUrl")
        if not image_url:
            continue
        label = image.get("name") or "garment reference"
        content.append({"type": "input_text", "text": f"Reference garment: {label}"})
        content.append(
            {
                "type": "input_image",
                "image_url": image_url,
                "detail": "low",
            }
        )

    payload = json.dumps(
        {
            "model": "gpt-5",
            "input": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "tools": [
                {
                    "type": "image_generation",
                    "model": model,
                    "action": "edit",
                    "input_fidelity": "high",
                    "size": "1024x1536",
                }
            ],
        }
    ).encode("utf-8")

    http_request = request.Request(
        "https://api.openai.com/v1/responses",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI request failed: HTTP {exc.code} {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error: {exc.reason}") from exc

    for item in body.get("output", []):
        if item.get("type") == "image_generation_call" and item.get("result"):
            return "data:image/png;base64," + item["result"]

    raise RuntimeError("OpenAI response did not include an edited image.")


def main() -> None:
    ensure_outfits_file()
    ensure_items_file()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), OutfitDemoHandler)
    print("Demo server running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
