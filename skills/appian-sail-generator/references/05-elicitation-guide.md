# Elicitation Guide — When and How to Ask

The single biggest failure mode of a SAIL generator is **inventing details that the user didn't specify**: making up record-type names, guessing field types, assuming form intent, picking a layout the user didn't want. The fix is asking — but asking *well*. This file is the playbook.

The principle: **ask once, ask the right things, default the rest, and proceed**. Don't bombard. Don't ask trivia. Don't ask things you can decide yourself with a reasonable default. Inventing a record-type UUID is unacceptable; inventing a colour scheme is fine.

---

## What to ask vs what to default

### Always ask (these matter, defaults are unsafe)

| Question | Why it can't be defaulted |
|---|---|
| What record type(s) and fields? (functional only) | UUIDs are environment-specific and unknowable from context. |
| Is this a CREATE form, UPDATE form, or both? | Affects button labels, control flow, and the `ri!isUpdate` pattern. |
| Is this a start form for a process model? | If yes, `ri!` names must match `process_variables` exactly. |
| Specific business rules (validations, conditional display) | "Validate email" is too vague — get the actual rule. |
| Relationships traversed (when the UI shows data from related records) | Confirm the relationship name before using `[relationship].fields.X`. |
| Layout when the user is explicit ("split view", "wizard with 5 steps") | The user has a mental model; honour it. |

### Ask if non-trivial, otherwise default

| Question | Default | When to ask |
|---|---|---|
| Single component or full page? | Read the request literally — "a grid" → component, "a dashboard" → page | When it's genuinely ambiguous (e.g. "a case management interface") |
| Mockup or functional? | Mockup, unless the user said "functional"/"dynamic"/"connect to" | When the user clearly wants something working but didn't say which step |
| How many sample rows for a grid? | 5–8 (enough to show variety, not so many the file balloons) | If the user says "show me what 100 rows looks like" |
| Sort order, pagination size, filter defaults | Match standard conventions (newest first, 25 per page) | If the user mentioned a specific UX expectation |
| Audience / persona | Generic business-user assumptions | When the user says the audience matters (executives, claims adjusters, etc.) |

### Never ask (you can decide)

- Exact sample-data values (case numbers, names, dates) — pick realistic-looking values.
- Exact pixel widths or spacing values — follow the layout guidelines.
- Specific colours within the default palette (`#F5F6F8`, `#1C2C44`, `#FFFFFF`, `"ACCENT"`, `"STANDARD"`).
- Whether to use `a!cardLayout` vs `a!sectionLayout` for a section — follow patterns.
- Whether to use icons — add a few in obviously appropriate places (status indicators, action buttons).

---

## How to ask

### One short batch, not a stream

If three things need asking, ask all three together — not three turns of one question each. Use a clear, scannable list. Numbering helps.

**Bad** (sequential):
> Q1: Is this a create form or update form?
> [user answers]
> Q2: What record type?
> [user answers]
> Q3: Is this a start form?

**Good** (batched):
> Before I generate, a few things:
> 1. Is this a CREATE form, an UPDATE form, or both?
> 2. What record type does it write to? (Give me the name; if you have UUIDs/field IDs handy, paste them. Otherwise I'll need you to either export the record from Appian or describe the fields.)
> 3. Is this a start form for a process model? (If yes, do you have the model.json so I can match the process variables?)

### Default-then-confirm when defaults are obvious

Better than asking is *proposing* — give a default, ask the user to override only if they want something else.

**Default-then-confirm:**
> I'll generate a static mockup (Phase 1) first — `a!headerContentLayout` with a KPI row, filter strip, and a grid of cases with 8 sample rows. If you want a different layout or want to skip straight to a functional version connected to your Case record type, tell me before I start.

This is faster for the user than answering five questions and lets them stay in flow. Use it whenever the defaults are sensible.

### Don't ask questions you can answer with a look at the existing artifacts

If a `.sail` mockup already exists in `output/`, read it before asking what fields it has, what record type it's for, or what status values it uses. The user shouldn't have to repeat themselves.

If `context/data-model-context.md` exists, read it before asking about record-type structure.

---

## Trigger phrases — what they typically mean

A short mental model of common user phrasings, to inform when to ask vs proceed:

| Phrase | Typically means | Default action |
|---|---|---|
| "Make a [thing]" | Mockup of [thing] | Phase 1 |
| "Create a dashboard for X" | Full-page mockup, dashboard layout | Phase 1, `a!headerContentLayout` |
| "Build a form to capture X" | Form mockup with create intent | Phase 1, `a!formLayout`, ask if also update |
| "Wizard for X" | Multi-step form mockup | Phase 1, `a!wizardLayout`, ask about steps |
| "Hook it up to our X records" | Phase 2 conversion | Check preconditions; ask for context if missing |
| "Make it dynamic" / "Make it functional" / "Use real data" | Phase 2 conversion | Same as above |
| "Connect to <RecordTypeName>" | Phase 2 conversion targeting a specific record type | Confirm the record type is in `context/data-model-context.md` |
| "Now do X" (after generating something) | Iteration on the existing file | Edit, don't regenerate |
| "Split this into components" / "Refactor" | Invoke `sail-interface-splitter` | See `agents/sail-interface-splitter.md` |
| "Add validations from <screen def>" | Invoke `sail-validation-implementer` | See `agents/sail-validation-implementer.md` |
| "Paste this Appian error: …" | Fix the existing file based on the error | Edit, don't regenerate |

---

## When NOT to ask — proceed and surface assumptions

Sometimes the right move is to generate something reasonable and *show* the assumptions in the output (via `REQUIREMENT` comments, TODO comments, and a short note to the user). This is right when:

- The request is small and clarifying would feel pedantic ("make a stamp field for user initials" — just do it).
- The user is exploring and wants something to react to.
- The user said something like "just generate something, I'll iterate."

In these cases:
- Pick sensible defaults.
- Annotate the code with `/* ASSUMPTION: ... */` comments at the relevant locations, or add a small "Assumptions I made" section under the file path in your response.
- Make it easy to change ("if you want X different, tell me and I'll update").

---

## Example dialogues

### Example 1 — Ambiguous request, ask one good question

**User:** "I need an interface for managing claims."

**Bad reply:** [generates a full case management dashboard with invented field names]

**Good reply:**
> Two quick things to get this right:
> 1. Single page or a set (e.g. list page + detail page + intake form)?
> 2. Static mockup to review the UX, or functional with your real Claim records? (If functional, I'll need your `data-model-context.md` or the exported record-type XMLs.)

### Example 2 — Detailed request, just proceed

**User:** "Make a static dashboard for claims adjusters. Top row: 4 KPI cards for total open, total closed, average resolution time, and overdue. Below: a grid with claim ID, customer name, status, priority, due date, assigned to. Add a status filter dropdown above the grid."

**Reply:**
> Got it. Generating a static mockup. I'll put the 4 KPIs in a row, a filter strip with the status dropdown, then the grid with 8 sample rows showing the spread of statuses and priorities. Output in `output/claims-dashboard.sail` in a moment.

No questions needed — the request is precise.

### Example 3 — Functional request without context

**User:** "Now hook this up to our Claim records."

**Reply:**
> To convert it functional, I need the data-model context for your Claim record type. Three options:
> 1. You paste / point me to a `context/data-model-context.md` if you have one.
> 2. You paste the `recordTypeHaul` XML export of the Claim record (and any related records like Customer, ClaimDocument) — I'll run the script to generate the markdown.
> 3. You give me the record-type name, UUIDs, and field UUIDs by hand (slowest, error-prone).
>
> Which works?

### Example 4 — Partial info, ask only what's missing

**User:** "Make it functional. We use the Case record type, UUID `{abc-123}`, with fields title (Text), status (Text), and dueDate (Date). The status field has a UUID `{def-456}`."

**Reply:**
> Thanks — I have title and status but I need the UUIDs for `title` and `dueDate` to write valid field references. Can you paste those, or share the `recordTypeHaul` XML and I'll extract them?

---

## Anti-patterns

- ❌ Asking five questions when two would do.
- ❌ Asking for information that's already in `context/data-model-context.md` or the existing `.sail` file.
- ❌ Asking for things you can default sensibly (colours, exact sample values, sort orders).
- ❌ Generating with invented UUIDs and saying "you can replace these with your real UUIDs later" — this is the #1 way to ship broken SAIL.
- ❌ Generating with invented business rules and presenting them as if the user requested them.
- ❌ Endlessly clarifying without producing anything — at some point, the right answer is "let me default these and you tell me what to change."
