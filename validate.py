#!/usr/bin/env python3
"""Check a Mindful Scroll lesson file before pushing it.

    python3 validate.py physics.json
    python3 validate.py physics.json --previous old-physics.json   # also checks no ids were removed

Exits with status 1 if there are errors (the app would reject the file or skip
steps). Warnings are things that load fine but are probably mistakes.
See SCHEMA.md for the format.
"""
import json
import os
import re
import sys

COLORS = {"blue", "green", "orange", "purple", "teal", "pink"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".heic", ".gif", ".webp"}
STEP_TYPES = ("read", "choice", "multi", "truefalse", "number", "blank", "free")
BASE_DIR = "."  # folder of the JSON file; image paths are relative to it
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KHAN_PATH = re.compile(r"^https://www\.khanacademy\.org/(math|science|test-prep|computing|economics-finance-domain|humanities)/[a-z0-9-]+(/[a-z0-9-]+)*$")

errors, warnings = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def is_text(v):
    return isinstance(v, str) and v.strip() != ""


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def check_image(where, path):
    if not is_text(path):
        return err(where, "image must be a path like \"images/ch3/fig1.png\" or an https link")
    if "://" in path:
        if not path.startswith("https://"):
            err(where, f"image link must start with https:// ({path})")
        return
    if path.startswith("/") or "\\" in path or " " in path:
        err(where, f"image path {path!r}: use forward slashes, no leading /, no spaces")
        return
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMAGE_EXTS:
        err(where, f"image {path!r} must be one of {sorted(IMAGE_EXTS)}")
    full = os.path.join(BASE_DIR, path)
    if not os.path.isfile(full):
        err(where, f"image {path!r} not found next to the JSON file (upload it to the repo too)")
    elif os.path.getsize(full) > 1_500_000:
        warn(where, f"image {path!r} is {os.path.getsize(full) // 1000} KB; keep images under ~1.5 MB (crop or shrink)")


def check_step(where, s, quiz=False):
    if not isinstance(s, dict):
        return err(where, "step must be an object")
    t = s.get("type")
    for key in ("image", "solutionImage"):
        if key in s:
            check_image(f"{where} › {key}", s[key])
    if "image" in s and not is_text(s.get("alt")):
        warn(where, "image has no \"alt\" (a short description of the picture)")
    if t == "read":
        if quiz:
            warn(where, "read step inside a quiz; quizzes are usually questions only")
        if not is_text(s.get("text")) and "image" not in s:
            err(where, "read step needs \"text\" or \"image\"")
        elif is_text(s.get("text")) and len(s["text"].split()) > 250:
            warn(where, "read text is very long (over 250 words); it's a phone screen, consider splitting")
        return
    if t not in STEP_TYPES:
        return err(where, f"unknown type {t!r} (use {', '.join(STEP_TYPES)})")
    if not is_text(s.get("prompt")):
        err(where, "needs \"prompt\"")
    if t != "free" and not is_text(s.get("explain")):
        warn(where, "no \"explain\"; it's shown after each answer")
    if t in ("choice", "multi") and "choiceImages" in s:
        ci, c = s["choiceImages"], s.get("choices")
        if not isinstance(ci, list) or not isinstance(c, list) or len(ci) != len(c):
            err(where, "\"choiceImages\" must be a list with one image per choice")
        else:
            for i, img in enumerate(ci):
                check_image(f"{where} › choiceImages[{i}]", img)
    if t == "multi":
        c, a = s.get("choices"), s.get("answers")
        if not (isinstance(c, list) and 2 <= len(c) and all(is_text(x) for x in c)):
            err(where, "\"choices\" must be a list of at least 2 strings")
        elif not (isinstance(a, list) and a and all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < len(c) for i in a)):
            err(where, f"\"answers\" must be a non-empty list of positions from 0 to {len(c) - 1}")
        elif len(set(a)) != len(a):
            warn(where, "duplicate positions in \"answers\"")
        if "correct" in s:
            warn(where, "multi uses \"answers\" (a list), not \"correct\"; \"correct\" is ignored")
    elif t == "blank":
        a = s.get("accept")
        if not (isinstance(a, list) and a and all(is_text(x) for x in a)):
            err(where, "\"accept\" must be a non-empty list of accepted answers")
        if "___" not in (s.get("prompt") or ""):
            warn(where, "blank prompt has no ___ to show where the blank is")
    elif t == "free":
        if not is_text(s.get("solution")) and "solutionImage" not in s:
            err(where, "free step needs \"solution\" (worked answer) or \"solutionImage\"")
    elif t == "choice":
        c, k = s.get("choices"), s.get("correct")
        if not (isinstance(c, list) and 2 <= len(c) and all(is_text(x) for x in c)):
            err(where, "\"choices\" must be a list of at least 2 strings")
        elif not (isinstance(k, int) and not isinstance(k, bool) and 0 <= k < len(c)):
            err(where, f"\"correct\" must be a position from 0 to {len(c) - 1}")
        elif len(set(c)) != len(c):
            warn(where, "duplicate choices")
        if isinstance(c, list) and len(c) > 5:
            warn(where, "more than 5 choices is hard to read on a phone")
    elif t == "truefalse":
        if not isinstance(s.get("isTrue"), bool):
            err(where, "needs \"isTrue\": true or false")
    elif t == "number":
        if not is_num(s.get("value")):
            err(where, "needs a numeric \"value\"")
        tol = s.get("tolerance")
        if tol is not None and (not is_num(tol) or tol < 0):
            err(where, "\"tolerance\" must be a number ≥ 0")
        v = s.get("value")
        if is_num(v) and v != int(v) and (tol is None or tol < 0.01):
            warn(where, "decimal answer with a tiny tolerance; allow for rounding (e.g. 0.05)")


def check_resources(where, res):
    if not isinstance(res, list):
        return err(where, "\"resources\" must be a list")
    for i, r in enumerate(res):
        w = f"{where} › resources[{i}]"
        if not isinstance(r, dict):
            err(w, "must be an object with \"title\" and \"url\"")
            continue
        if not is_text(r.get("title")):
            err(w, "needs \"title\"")
        url = r.get("url")
        if not (isinstance(url, str) and url.startswith("https://")):
            err(w, "\"url\" must start with https://")
        elif "khanacademy.org" in url and "/search" not in url and not KHAN_PATH.match(url):
            warn(w, f"check this Khan Academy link opens the right page: {url}")


def ids_in(course):
    out = set()
    for u in course.get("units", []) or []:
        for l in (u or {}).get("lessons", []) or []:
            if isinstance(l, dict) and isinstance(l.get("id"), str):
                out.add(l["id"])
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    global BASE_DIR
    path = argv[1]
    BASE_DIR = os.path.dirname(os.path.abspath(path))
    try:
        with open(path, encoding="utf-8") as f:
            course = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR {path}: not valid JSON (line {e.lineno}, column {e.colno}): {e.msg}")
        return 1

    if not isinstance(course, dict):
        print("ERROR: top level must be an object")
        return 1
    if course.get("format") != 1:
        err("top", "\"format\" must be 1")
    for key in ("id", "title"):
        if not is_text(course.get(key)):
            err("top", f"needs \"{key}\"")
    if "resources" in course:
        check_resources("top", course["resources"])
    prefix = None if course.get("id") == "physics" else f"{course.get('id')}-"
    units = course.get("units")
    if not isinstance(units, list) or not units:
        err("top", "\"units\" must be a non-empty list")
        units = []

    seen = {}
    lesson_count = 0
    for ui, u in enumerate(units):
        uw = f"unit {ui + 1}"
        if not isinstance(u, dict):
            err(uw, "must be an object")
            continue
        uid = u.get("id")
        uw = f"unit {uid or ui + 1}"
        if not (isinstance(uid, str) and ID_RE.match(uid)):
            err(uw, "\"id\" must be lowercase-with-dashes")
        elif uid in seen:
            err(uw, f"id also used by {seen[uid]}")
        else:
            seen[uid] = uw
        if not is_text(u.get("title")):
            err(uw, "needs \"title\"")
        if prefix and isinstance(uid, str) and not uid.startswith(prefix):
            err(uw, f"ids in this course must start with {prefix!r} so they never clash with another course")
        if "number" in u and not (isinstance(u["number"], int) and not isinstance(u["number"], bool) and u["number"] > 0):
            err(uw, "\"number\" must be a positive whole number")
        if "resources" in u:
            check_resources(uw, u["resources"])
        if "color" in u and u["color"] not in COLORS:
            warn(uw, f"color {u['color']!r} isn't one of {sorted(COLORS)}; blue will be used")
        lessons = u.get("lessons")
        if not isinstance(lessons, list) or not lessons:
            err(uw, "\"lessons\" must be a non-empty list")
            continue
        for li, l in enumerate(lessons):
            lw = f"{uw} › lesson {li + 1}"
            if not isinstance(l, dict):
                err(lw, "must be an object")
                continue
            lesson_count += 1
            lid = l.get("id")
            lw = f"{uw} › {lid or li + 1}"
            if not (isinstance(lid, str) and ID_RE.match(lid)):
                err(lw, "\"id\" must be lowercase-with-dashes")
            elif prefix and not lid.startswith(prefix):
                err(lw, f"ids in this course must start with {prefix!r}")
            elif lid in seen:
                err(lw, f"id also used by {seen[lid]}")
            else:
                seen[lid] = lw
            if not is_text(l.get("title")):
                err(lw, "needs \"title\"")
            if "xp" in l and not (isinstance(l["xp"], int) and l["xp"] > 0):
                err(lw, "\"xp\" must be a positive whole number")
            kind = l.get("kind", "lesson")
            if kind not in ("lesson", "quiz"):
                err(lw, f"\"kind\" must be \"lesson\" or \"quiz\", not {kind!r}")
            steps = l.get("steps")
            if not isinstance(steps, list) or not steps:
                err(lw, "\"steps\" must be a non-empty list")
                continue
            for si, s in enumerate(steps):
                check_step(f"{lw} › step {si + 1}", s, quiz=(kind == "quiz"))
            questions = [s for s in steps if isinstance(s, dict) and s.get("type") != "read"]
            if not questions:
                warn(lw, "no questions")
            if len(steps) > 40:
                warn(lw, f"{len(steps)} steps is very long; consider splitting it into two lessons")

    if len(argv) >= 4 and argv[2] == "--previous":
        with open(argv[3], encoding="utf-8") as f:
            old = json.load(f)
        gone = ids_in(old) - ids_in(course)
        for g in sorted(gone):
            err("ids", f"lesson id {g!r} was removed or renamed; saved progress for it will be lost")

    for w in warnings:
        print("warning", w)
    for e in errors:
        print("ERROR  ", e)
    print(f"{len(units)} units, {lesson_count} lessons, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
