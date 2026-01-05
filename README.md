## Summary
Given a topic as input, the system performs the following steps:
1) Generates a scene wise narration script using an AI model (with a safe fallback).
2) Converts the script into a machine readable animation blueprint.
3) Renders a single MP4 explainer video using programmatic animations.
4) The visual style is manually analyzed from a reference explainer video and encoded as reusable rules.

### Topic

- Script Generation (Groq LLM or mock fallback)
- script.json
- Blueprint Generation (rule-based)
- blueprint.json
- Manim Rendering
- MP4 Video

