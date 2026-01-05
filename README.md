Given a topic as input, the system performs the following steps:

Generates a scene-wise narration script using an AI model (with a safe fallback).

Converts the script into a machine-readable animation blueprint.

Renders a single MP4 explainer video using programmatic animations.

The visual style is manually analyzed from a reference explainer video and encoded as reusable rules.

Topic
  → Script Generation (Groq LLM or mock fallback)
  → script.json
  → Blueprint Generation (rule-based)
  → blueprint.json
  → Manim Rendering
  → MP4 Video
