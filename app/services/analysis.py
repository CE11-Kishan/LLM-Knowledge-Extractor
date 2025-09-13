from __future__ import annotations
from collections import Counter
import re
from typing import List, Tuple

SENTIMENT_POSITIVE = {"good","great","excellent","positive","love","like","success","improve","win","benefit"}
SENTIMENT_NEGATIVE = {"bad","poor","terrible","negative","hate","fail","problem","issue","risk","loss"}


def extract_keywords(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z\-']+", text.lower())
    stop = set("the a an and or but if while of for on in at to from with without within this that those these is are was were be being been it it's its as by we you they i he she them our your their can may might should would could will just".split())
    nouns = [t for t in tokens if t not in stop]
    counts = Counter(nouns)
    most_common = [w for w,_ in counts.most_common(50)]
    filtered = []
    for w in most_common:
        if len(filtered) >= 3:
            break
        if not re.search(r"(ing|ed|ly)$", w):
            filtered.append(w)
    return filtered[:3]

def confidence(summary: str, topics: List[str], keywords: List[str]) -> float:
    # naive heuristic: fraction of fields non-empty times a brevity bonus
    fullness = sum([bool(summary), bool(topics), bool(keywords)]) / 3
    brevity = min(1.0, len(summary.split()) / 30)
    return round((0.5 * fullness + 0.5 * brevity), 3)
