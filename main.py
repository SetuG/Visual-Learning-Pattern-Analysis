"""
Visual Learning Pattern Analysis + AI Video Synthesis System
End-to-end prototype with Groq LLM (REST API + safe fallback)
"""

import json
import os
import re
import requests
from typing import Dict
from dotenv import load_dotenv
from manim import *

load_dotenv()



OUTPUT_DIR = "outputs"
FINAL_VIDEO_PREFIX = "final_"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"



STYLE_PROFILE = {
    "style": "2D explainer",
    "line_width": 4,
    "font_size_title": 48,
    "font_size_body": 28,
    "colors": {
        "primary": "blue",
        "neutral": "white"
    }
}

COLOR_MAP = {
    "blue": BLUE,
    "white": WHITE
}

#generate script

def generate_script(topic: str) -> Dict:
    print("[SCRIPT] Generating script using Groq REST API")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("[SCRIPT] No API key found, using mock")
        return mock_script(topic)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You generate short educational explanations."
            },
            {
                "role": "user",
                "content": f"Explain '{topic}' in 3 to 5 short sentences each sentence no more that 8 words, one per line."
            }
        ],
        "temperature": 0.2,
        "max_tokens": 200
    }

    try:
        r = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        if r.status_code != 200:
            print("[SCRIPT] Groq returned non-200:")
            print(r.text)
            raise RuntimeError("Groq request failed")

        content = r.json()["choices"][0]["message"]["content"]
        lines = [l.strip() for l in content.split("\n") if l.strip()][:5]

        return {
            "topic": topic,
            "scenes": [
                {"scene_id": i + 1, "text": line}
                for i, line in enumerate(lines)
            ]
        }

    except Exception as e:
        print("[SCRIPT] Groq failed, falling back to mock:", e)
        return mock_script(topic)


def mock_script(topic: str) -> Dict:
    lines = [
        f"{topic} is an important concept in modern systems.",
        f"It enables efficient communication between components.",
        f"In {topic}, entities remain connected for continuous interaction.",
        f"This improves real-time performance and reliability."
    ]

    return {
        "topic": topic,
        "scenes": [
            {"scene_id": i + 1, "text": line}
            for i, line in enumerate(lines)
        ]
    }

#generate blueprint

def generate_blueprint(script: Dict) -> Dict:
    print("[BLUEPRINT] Generating animation blueprint")
    scenes = []

    for scene in script["scenes"]:
        text = scene["text"].lower()
        elements = []

        if scene["scene_id"] == 1:
            elements.append({"type": "title"})
        elif "connection" in text or "request" in text:
            elements += [
                {"type": "circle", "label": "Client", "pos": "left"},
                {"type": "circle", "label": "Server", "pos": "right"},
                {"type": "arrow", "from": "left", "to": "right"}
            ]
        else:
            elements.append({"type": "rectangle", "label": "Concept"})

        scenes.append({
            "scene_id": scene["scene_id"],
            "text": scene["text"],
            "elements": elements
        })

    return {
        "topic": script["topic"],
        "style_profile": STYLE_PROFILE,
        "scenes": scenes
    }

#manim video generation

class FullExplainer(Scene):
    def __init__(self, blueprint, **kwargs):
        self.blueprint = blueprint
        super().__init__(**kwargs)

    def construct(self):
        pos = {"left": LEFT * 3, "right": RIGHT * 3}

        for scene in self.blueprint["scenes"]:
            objs = []
            caption = Text(scene["text"], font_size=STYLE_PROFILE["font_size_body"]).to_edge(DOWN)
            self.play(FadeIn(caption))

            for el in scene["elements"]:
                if el["type"] == "title":
                    t = Text(self.blueprint["topic"], font_size=STYLE_PROFILE["font_size_title"])
                    self.play(Write(t))
                    objs.append(t)

                elif el["type"] == "circle":
                    c = Circle(color=COLOR_MAP["blue"]).move_to(pos[el["pos"]])
                    l = Text(el["label"], font_size=24).move_to(c)
                    self.play(Create(c), Write(l))
                    objs += [c, l]

                elif el["type"] == "arrow":
                    a = Arrow(pos["left"], pos["right"])
                    self.play(Create(a))
                    objs.append(a)

                elif el["type"] == "rectangle":
                    r = Rectangle()
                    l = Text(el["label"], font_size=24).move_to(r)
                    self.play(Create(r), Write(l))
                    objs += [r, l]

            self.wait(2)
            self.play(FadeOut(caption), *[FadeOut(o) for o in objs])

#pipeline

def sanitize_filename(text):
    return re.sub(r"[^a-zA-Z0-9]", "_", text.lower())


def run_pipeline(topic: str):
    print("[PIPELINE] Starting pipeline")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    script = generate_script(topic)
    json.dump(script, open(f"{OUTPUT_DIR}/script.json", "w"), indent=2)

    blueprint = generate_blueprint(script)
    json.dump(blueprint, open(f"{OUTPUT_DIR}/blueprint.json", "w"), indent=2)

    print("[MANIM] Rendering video")
    FullExplainer(blueprint).render()

    for root, _, files in os.walk("media"):
        for f in files:
            if f.endswith(".mp4"):
                os.replace(os.path.join(root, f),
                           FINAL_VIDEO_PREFIX + sanitize_filename(topic) + ".mp4")
                print("[DONE] Video generated")
                return

#input

if __name__ == "__main__":
    run_pipeline("How websockets work")
