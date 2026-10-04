<!-- model=nvidia/nemotron-3.5-lightning:free channel=openrouter-free ts=20261003T2216Z -->
<!-- finalize-from-reasoning -->

### Verdict: WARN - Forbidden series names detected in addon scripts; CI check_names() will fail

### Findings: (markdown table with at least 2 rows)

| ID | Category | Description |
|----|----------|-------------|
| F1 | CI | `main.js` contains dragon names "Tairn", "Andarna", "Sgaeyl", "Xaden" as quiz choices, triggering `check_names()` forbidden phrase matches ("tairn", "anda rna", "sga eyl", "xaden") |
| F2 | Install/Build | `build_map.py` `chasm()` function issues duplicate fill commands for same coordinates (air then water), water overwrites air redundantly |
| F3 | Fan-work rules | `LISTING.md` contains series-referencing tags `#fourthwing #empyreanseries #rebeccayarros #dragonkind` violating IP-RULES.md rule 3 |

### Root cause
The `main.js` quiz choices include Empyrean series dragon names that are explicitly forbidden by `check_names()` in `test_release.py`. The `LISTING.md` tags and `build_map.py` duplicate fills are secondary issues.

### Confidence: High - The forbidden name matches are exact and would cause `check_names()` to fail, breaking CI.

### Unique angle
This fan-made Empyrean map must exclude all series character and dragon names from addon/script strings per IP-RULES.md, yet the signet quiz in `main.js` naturally uses those names as content, creating an unavoidable conflict requiring either name replacement or rule exception.

Actually, wait. Let me make sure the format is exactly right. The user said:

"First line must be ### Verdict"
"Then ### Findings with a markdown table (header + at least 2 finding rows)."
"Then ### Root cause, ### Confidence, ### Unique angle."
"Verdict line must be: PASS | WARN | FAIL — short reason."
"No tools. No preamble."

So the first line of the output should be `### Verdict`, then on the next line the verdict content. Then `### Findings`, then the table, then `### Root cause`, then `### Confidence`, then `### Unique angle`.

Let me format this properly.

Actually, re-reading: "First line must be ### Verdict" - so the very first line of the
