"""Static option lists for the Ming-3.0-tts web UI.

These mirror the exact values accepted by ``MingTTS.synthesize`` /
``tts_tasks`` so the front-end stays data-driven and the back-end can
validate requests against the same vocabulary.
"""

# Generation tasks exposed in the UI. Each maps to a ``task`` value accepted
# by ``MingTTS.synthesize``. ``STYLE`` is the runtime name for voice design.
TASKS = [
    {"value": "TTS", "label": "TTS (zero-shot / clone)", "needs_prompt": True,
     "language_optional": True, "controls": []},
    {"value": "MULTILINGUAL", "label": "Multilingual", "needs_prompt": True,
     "language_optional": False, "controls": []},
    {"value": "BASIC", "label": "Basic (speed/pitch/volume)", "needs_prompt": True,
     "language_optional": True, "controls": ["speed", "pitch", "volume"]},
    {"value": "EMOTION", "label": "Emotion", "needs_prompt": True,
     "language_optional": True, "controls": ["emotion"]},
    {"value": "DIALECT", "label": "Dialect (Cantonese / Sichuan)", "needs_prompt": True,
     "language_optional": True, "controls": ["dialect"]},
    {"value": "FREEFORM", "label": "Free-form instruction", "needs_prompt": False,
     "language_optional": True, "controls": ["instruction"]},
    {"value": "VOICE_DESIGN", "label": "Voice design (describe a voice)", "needs_prompt": False,
     "language_optional": True, "controls": ["style"]},
    {"value": "IP", "label": "Built-in voice", "needs_prompt": False,
     "language_optional": True, "controls": ["ip"]},
]

# Target languages. Chinese/English work without ``language_id``; the other
# five are required for MULTILINGUAL.
LANGUAGES = [
    {"value": "zh", "label": "Chinese (中文)"},
    {"value": "en", "label": "English"},
    {"value": "ja", "label": "Japanese (日本語)"},
    {"value": "ko", "label": "Korean (한국어)"},
    {"value": "de", "label": "German (Deutsch)"},
    {"value": "fr", "label": "French (Français)"},
    {"value": "es", "label": "Spanish (Español)"},
]

EMOTIONS = ["高兴", "悲伤", "愤怒", "恐惧", "厌恶", "惊讶", "中性"]

SPEED_VALUES = ["慢速", "中速", "快速"]
PITCH_VALUES = ["低", "中", "高"]
VOLUME_VALUES = ["低", "中", "高"]
DIALECT_VALUES = ["cantonese", "chuanyu dialect"]

# Inline paralinguistic tags (case-sensitive, include the brackets). They are
# typed directly into the text for any task.
PARALINGUISTIC_TAGS = [
    "[Breathing]", "[Cough]", "[Sigh]", "[Laughter]", "[Uhm]",
    "[Surprise-ah]", "[Surprise-oh]", "[Dissatisfaction-hnn]",
    "[Confirmation-en]", "[Question-ei]", "[Question-ah]",
    "[Question-en]", "[Question-oh]", "[Question-huh]",
]

# Built-in premium voices. English voices plus a curated set of the 100+
# Chinese voices. The ``ip`` field also accepts any other voice name from the
# catalog (e.g. ``灵信远_高兴``).
BUILTIN_VOICES = [
    # English
    {"value": "US_James", "label": "US_James (American male, narration)"},
    {"value": "US_Stella", "label": "US_Stella (American female, warm)"},
    {"value": "US_Emma", "label": "US_Emma (American female, assistant)"},
    {"value": "UK_George", "label": "UK_George (British male, audiobook)"},
    {"value": "UK_Charlotte", "label": "UK_Charlotte (British female, measured)"},
    # Recommended Chinese
    {"value": "灵小柔", "label": "灵小柔 (Chinese female, sweet/clear)"},
    {"value": "灵楷", "label": "灵楷 (Chinese male, warm/resonant)"},
    {"value": "灵小安", "label": "灵小安 (Chinese female, teen)"},
    {"value": "灵语汐", "label": "灵语汐 (Chinese female, bright)"},
    {"value": "灵朗", "label": "灵朗 (Chinese male, boyfriend)"},
    {"value": "灵叙柔", "label": "灵叙柔 (Chinese female, news anchor)"},
    {"value": "灵卓然", "label": "灵卓然 (Chinese male, documentary)"},
]

# Default generation parameters (see infer.py).
DEFAULTS = {
    "cfg": 2.0,
    "sigma": 0.25,
    "temperature": 0.0,
    "max_length": 24,
    "max_decode_steps": 1000,
    "seed": 1895,
}

# Which control keys belong to which structured task (must match
# ``tts_tasks._TASK_ALIASES`` / ``build_task_instruction``).
TASK_CONTROL_FIELDS = {
    "BASIC": ["speed", "pitch", "volume"],
    "EMOTION": ["emotion"],
    "DIALECT": ["dialect"],
    "VOICE_DESIGN": ["style"],
    "STYLE": ["style"],
    "IP": ["ip"],
}
