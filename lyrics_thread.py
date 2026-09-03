from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Iterable


@dataclass(frozen=True)
class Pattern:
    language: str
    pattern_id: str
    label: str
    template: str
    function: str
    regex: re.Pattern[str]


@dataclass(frozen=True)
class Match:
    text: str
    language: str
    pattern_id: str
    label: str
    template: str
    function: str
    slots: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["slots"] = list(self.slots)
        return data


PATTERNS: tuple[Pattern, ...] = (
    Pattern(
        "ko", "ko.condition_response", "조건 → 반응",
        "[A]가 X하면 [B]는 Y", "조건/결심",
        re.compile(r"^\s*(네가|니가|너가)\s+(.+?)(?:면|다면)\s+(나는|난|내가)\s+(.+?)[.!?…]*\s*$"),
    ),
    Pattern(
        "ko", "ko.expectation_reversal", "기대 → 반전",
        "X라고 생각했지만 Y", "반전/깨달음",
        re.compile(r"^\s*(.+?)(?:라고|다고)\s*생각했(?:지만|는데|더니)\s+(.+?)[.!?…]*\s*$"),
    ),
    Pattern(
        "ko", "ko.desire_contrast", "욕망 → 장애",
        "X하고 싶지만 Y", "갈등/좌절",
        re.compile(r"^\s*(.+?)(?:고|하고)\s*싶(?:지만|은데|어도)\s+(.+?)[.!?…]*\s*$"),
    ),
    Pattern(
        "ko", "ko.question_regret", "질문 → 후회",
        "왜 X했을까", "후회/자문",
        re.compile(r"^\s*왜\s+(.+?)(?:했을까|한\s*걸까|그랬을까)[.!?…]*\s*$"),
    ),
    Pattern(
        "ko", "ko.prohibition_request", "금지 → 요청",
        "X하지 마, Y해 줘", "요청/호소",
        re.compile(r"^\s*(.+?)하지\s*마(?:,|\s)+(.+?)(?:해\s*줘|해줘|해)[.!?…]*\s*$"),
    ),

    Pattern(
        "ja", "ja.condition_response", "条件 → 反応",
        "[A]がXなら [B]はY", "条件/決意",
        re.compile(r"^\s*(君|きみ|あなた)が(.+?)(?:なら|たら)\s*(僕|ぼく|私|わたし)は(.+?)[。！？…]*\s*$"),
    ),
    Pattern(
        "ja", "ja.expectation_reversal", "期待 → 反転",
        "Xと思っていたのに Y", "反転/気づき",
        re.compile(r"^\s*(.+?)と思っていた(?:のに|けど|けれど)\s*(.+?)[。！？…]*\s*$"),
    ),
    Pattern(
        "ja", "ja.desire_contrast", "欲求 → 障害",
        "Xしたいけど Y", "葛藤/挫折",
        re.compile(r"^\s*(.+?)したい(?:けど|けれど|のに)\s*(.+?)[。！？…]*\s*$"),
    ),
    Pattern(
        "ja", "ja.question_regret", "問い → 後悔",
        "どうしてXんだろう", "後悔/自問",
        re.compile(r"^\s*どうして(.+?)(?:んだろう|のだろう|んだろ)[。！？…]*\s*$"),
    ),

    Pattern(
        "en", "en.condition_response", "condition → response",
        "If you X, I Y", "condition/resolve",
        re.compile(r"^\s*If\s+you\s+(.+?)[,\s]+I\s+(.+?)[.!?…]*\s*$", re.I),
    ),
    Pattern(
        "en", "en.expectation_reversal", "expectation → reversal",
        "I thought X, but Y", "reversal/realization",
        re.compile(r"^\s*I\s+thought\s+(.+?)[,\s]+but\s+(.+?)[.!?…]*\s*$", re.I),
    ),
    Pattern(
        "en", "en.desire_contrast", "desire → obstacle",
        "I want to X, but Y", "conflict/frustration",
        re.compile(r"^\s*I\s+want\s+to\s+(.+?)[,\s]+but\s+(.+?)[.!?…]*\s*$", re.I),
    ),
)


def detect_language(text: str) -> str:
    if re.search(r"[\u3040-\u30ff]", text):
        return "ja"
    if re.search(r"[\uac00-\ud7a3]", text):
        return "ko"
    return "en"


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def analyze_sentence(text: str, language: str | None = None) -> list[Match]:
    text = normalize_space(text)
    if not text:
        return []
    language = language or detect_language(text)

    matches: list[Match] = []
    for pattern in PATTERNS:
        if pattern.language != language:
            continue
        m = pattern.regex.match(text)
        if not m:
            continue
        slots = tuple(normalize_space(v) for v in m.groups())
        matches.append(
            Match(
                text=text,
                language=language,
                pattern_id=pattern.pattern_id,
                label=pattern.label,
                template=pattern.template,
                function=pattern.function,
                slots=slots,
            )
        )
    return matches


def analyze_lyrics(text: str, language: str | None = None) -> list[dict]:
    results: list[dict] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        matches = analyze_sentence(line, language)
        if matches:
            for match in matches:
                row = match.to_dict()
                row["line_no"] = line_no
                results.append(row)
        else:
            results.append({
                "line_no": line_no,
                "text": line,
                "language": language or detect_language(line),
                "pattern_id": None,
                "label": "미분류",
                "template": None,
                "function": None,
                "slots": [],
            })
    return results
