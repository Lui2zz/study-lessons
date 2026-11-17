# Mindful Scroll lesson format

This repo holds the study courses for the Mindful Scroll app, one file per course:

| Course | File | Opened from | Lesson/unit ids |
|---|---|---|---|
| Physics | `physics.json` | Activities → Math → Physics | anything unique (existing ones have no prefix) |
| Calculus | `calc.json` | Activities → Math → Calculus | **must start with `calc-`**, e.g. `calc-u6-riemann-sums` |

The app downloads a course file (and every image it uses) each time that course is
opened, so anything pushed here shows up on the phone without reinstalling. Both files
use the same format, described below.

Give this file to whoever (or whatever agent) writes lessons. It is the whole contract.

## Rules that matter most

1. **Never change or reuse an `id` that already exists**, in any course file.
   Progress is saved by lesson `id`. Renaming one makes that lesson look unfinished;
   reusing one marks a new lesson as already done. Titles can change freely.
2. **Add new chapters as new units at the end** of `units` (and new lessons at the end
   of a unit). Lessons unlock in order, so inserting one in the middle locks
   everything after it until it's done.
3. **Never change an image file in place.** The phone saves images by file name. To fix
   a picture, upload it under a new name (e.g. `fig2b.png`) and point the step at that.
4. **Run the validator before every push:**
   `python3 validate.py <file> --previous <copy of the file before your edit>`.
   It must say `0 errors`. If a broken file gets pushed anyway, the app ignores it and
   keeps the last good version: nothing breaks, but the new chapter won't appear.
5. Keep `format` at `1`. The repo is **public**: don't upload anything with names,
   grades or other personal info.

## From packet to unit (workflow)

When given a new packet or chapter (photos or PDF):

1. Make **one unit per packet/chapter**: `id` like `ch4-momentum` or `calc-u6`,
   `title` from the chapter, `subtitle` with the main topics. For Calculus, set
   `number` to the class's unit number.
2. Split it into **lessons of one idea each**, following the packet's order. Each
   lesson teaches with `read` steps and checks with questions. Length can vary
   (a short idea might be 4 steps, a dense one 15+), but long text is hard to read on a
   phone, so prefer more lessons over very long ones.
3. Turn the packet's own questions into steps, keeping their wording and numbers
   where possible:
   - one correct option → `choice`; "select all" → `multi`
   - calculation with one number → `number`
   - a word or short phrase → `blank`
   - multi-step problems, explanations, derivations, drawing → `free` with a full worked `solution`
4. **Figures:** crop each diagram or graph the questions need from the packet (just
   the figure, not the whole page), save it as PNG or JPG under
   `images/<unit-id>/`, e.g. `images/ch4-momentum/fig3.png`, under ~1.5 MB, and
   reference it with `image` plus a short `alt`. Redrawing a simple diagram is fine
   too.
5. Add a **Khan Academy link** for the unit in `resources` (see "Resources").
6. End every unit with a **chapter quiz** (`"kind": "quiz"`): 8–20 mixed questions
   covering the whole chapter, packet-style, no `read` steps.
7. Update `updated` to today's date, run the validator, then push the course file and
   the new images together.

## Shape

```json
{
  "format": 1,
  "id": "calc",
  "title": "Calculus",
  "updated": "2026-11-17",
  "resources": [ { "title": "Khan Academy · AP Calculus AB", "url": "https://www.khanacademy.org/math/ap-calculus-ab" } ],
  "units": [
    {
      "id": "calc-u6",
      "number": 6,
      "title": "Integration",
      "subtitle": "Riemann sums, definite integrals, FTC",
      "color": "teal",
      "resources": [ { "title": "Khan Academy · Unit 6", "url": "https://www.khanacademy.org/search?page_search_query=riemann%20sums" } ],
      "lessons": [
        { "id": "calc-u6-riemann", "title": "Riemann sums", "symbol": "chart.bar", "steps": [ ... ] },
        { "id": "calc-u6-quiz", "title": "Unit 6 quiz", "kind": "quiz", "steps": [ ... ] }
      ]
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `id` (top level) | yes | `physics` or `calc`. Never change it. |
| `units[].id`, `lessons[].id` | yes | Lowercase words joined by `-`, unique across **all** course files. In `calc.json` they must start with `calc-`. Never change after publishing. |
| `units[].number` | no | The number shown as "Unit N". Use the class's unit number (Calculus started at Unit 5). Defaults to the unit's position in the file. |
| `units[].resources` | no | Extra practice links shown under the unit, e.g. the matching Khan Academy unit. See "Resources". |
| `resources` (top level) | no | Links for the whole course, shown at the bottom. If missing, the app shows Khan Academy's course page. |
| `units[].color` | no | `blue`, `green`, `orange`, `purple`, `teal` or `pink`. Default `blue`. Vary it between units. |
| `lessons[].kind` | no | `lesson` (default) or `quiz`. In a lesson, missed questions repeat at the end. A quiz doesn't repeat them; it ends with a score and a review of the misses. |
| `lessons[].symbol` | no | An [SF Symbol](https://developer.apple.com/sf-symbols/) name, e.g. `atom`, `bolt`, `scalemass`, `waveform`, `function`, `chart.xyaxis.line`, `chart.bar`, `sum`, `lightbulb`, `arrow.right`. Wrong names show nothing, so stick to common ones. Quizzes default to a checkered flag. |
| `lessons[].xp` | no | Default 10 (quiz 20). Replays earn half. |

## Resources (Khan Academy links)

```json
"resources": [
  { "title": "Khan Academy · Unit 5", "subtitle": "Analytical applications of differentiation",
    "url": "https://www.khanacademy.org/math/ap-calculus-ab/ab-diff-analytical-applications-new" }
]
```

Give every new unit a link to the matching Khan Academy unit. They open in Safari.
**Only use a Khan URL you're sure exists.** If you're not sure, use a search link instead,
which always works:
`https://www.khanacademy.org/search?page_search_query=mean%20value%20theorem`

## Text formatting

`text`, `prompt`, `explain`, `solution` and `choices` support `**bold**`, `*italic*` and
line breaks (`\n`; `\n\n` for a new paragraph). Write math in plain text with Unicode:
`v² = u² + 2as`, `Δp = F·Δt`, `f′(x)`, `f″(x)`, `√x`, `∫₀² x² dx`, `lim x→0`, `θ`, `π`, `≤`, `∞`.
LaTeX is **not** rendered. For a formula that can't be written that way, use an image.

## Pictures

Any step can have:

```json
"image": "images/ch4-momentum/fig3.png",
"alt": "Two carts on a track, 2 kg moving right at 3 m/s toward a 1 kg cart at rest"
```

The path is relative to the course file in this repo (a full `https://` link also
works). Pictures show on a white card, and you can tap one to zoom. `choice` and `multi`
can also have one picture per option, shown in a 2-column grid. This is good for
"which graph shows…":

```json
"choices": ["A", "B", "C", "D"],
"choiceImages": ["images/calc-u5/graph-a.png", "images/calc-u5/graph-b.png", "images/calc-u5/graph-c.png", "images/calc-u5/graph-d.png"]
```

## Step types

### `read`: teach an idea
```json
{ "type": "read", "title": "Impulse", "text": "Impulse is force × time…", "image": "images/ch4/impulse.png", "alt": "…" }
```
Needs `text` or `image`.

### `choice`: one correct option
```json
{ "type": "choice", "prompt": "A runner covers 100 m in 20 s. Average speed?",
  "choices": ["2 m/s", "5 m/s", "20 m/s"], "correct": 1,
  "explain": "100 m ÷ 20 s = 5 m/s." }
```
`correct` is the **position starting at 0** (here `1` = "5 m/s").

### `multi`: select all that apply
```json
{ "type": "multi", "prompt": "Which are vector quantities?",
  "choices": ["Speed", "Velocity", "Mass", "Force"], "answers": [1, 3],
  "explain": "Velocity and force have direction." }
```
`answers` lists **every** correct position. All of them, and only them, must be picked.

### `truefalse`
```json
{ "type": "truefalse", "prompt": "A parked car has kinetic energy.", "isTrue": false,
  "explain": "v = 0, so KE = 0." }
```

### `number`: type a number
```json
{ "type": "number", "prompt": "What net force accelerates a 2 kg ball at 5 m/s²?",
  "value": 10, "tolerance": 0.01, "unit": "N", "explain": "F = 2 × 5 = 10 N." }
```
Correct if within `tolerance` of `value` (default 0.001). Give rounding room for
decimals (e.g. `0.05`, or about 1% of the answer), and say in the prompt which `g`
to use. `unit` is optional and shown next to the box. The learner doesn't type it.

### `blank`: fill in a word or phrase
```json
{ "type": "blank", "prompt": "An object's resistance to changes in motion is called ___.",
  "accept": ["inertia"], "explain": "Newton's first law is also called the law of inertia." }
```
Case, extra spaces and a final period are ignored. List spelling variants and
synonyms in `accept`; the first one is shown as the answer. If an answer is a number,
it's also compared as a number (using `tolerance`).

### `free`: show-your-work / free response (self-graded)
```json
{ "type": "free",
  "prompt": "A 0.15 kg ball hits a wall at 20 m/s and bounces back at 15 m/s. Find the impulse on the ball.",
  "image": "images/ch4/ball-wall.png", "alt": "Ball bouncing off a wall",
  "solution": "Take toward the wall as +.\n\nΔp = m(v_f − v_i) = 0.15 × (−15 − 20) = **−5.25 N·s**\n\nSo 5.25 N·s directed away from the wall.",
  "solutionImage": "images/ch4/ball-wall-solution.png" }
```
The learner works it on paper, taps **Show solution**, then taps **I got it** or
**I missed it**. Write the solution step by step, like a worked example. It needs
`solution` or `solutionImage`; `explain` isn't used.

Every question except `free` should have `explain`. It's shown after every answer,
right or wrong.

Unknown `type`s and steps missing a required field are skipped by the app (the
validator reports them as errors), so a typo costs one step, not the lesson.

## Publishing

The phone already has this repo's link (Settings → Lessons, the Physics link).
`calc.json` is found automatically in the same folder as `physics.json`. Every push
shows up the next time that course is opened, or when you pull down on the course
screen. GitHub can take up to ~5 minutes to serve a new version. Images are downloaded
and saved at the same time, so lessons with pictures work offline afterwards.
