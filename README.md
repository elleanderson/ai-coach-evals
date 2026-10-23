<p align="center"><img src="https://andersonco.uk/leaf-oak.png" width="48" alt=""></p>

# AI Coach Evals

[![Evals](https://github.com/elleanderson/ai-coach-evals/actions/workflows/evals.yml/badge.svg)](https://github.com/elleanderson/ai-coach-evals/actions/workflows/evals.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-12332E?logo=python&logoColor=F3EEE2)
![pytest](https://img.shields.io/badge/tested%20with-pytest-12332E?logo=pytest&logoColor=F3EEE2)
![YAML](https://img.shields.io/badge/cases-YAML-12332E?logo=yaml&logoColor=F3EEE2)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-12332E?logo=githubactions&logoColor=F3EEE2)
![Licence](https://img.shields.io/badge/licence-MIT-A8842F)

A small, readable eval kit for AI coaches. You write down what your coach promises in plain English, turn each promise into a test case and check the coach's real replies against them, on every change.

I built it for [New Leaf](https://andersonco.uk/newleaf), my free coaching tool for people with squiggly careers. I tell product leaders that evals turn "it seems better" into evidence. This is me doing it on my own product.

## Why This Exists

AI coaches are easy to demo and hard to trust. A prompt tweak or a model upgrade can quietly change how a coach behaves, and nobody notices until a real person has a bad experience.

New Leaf makes some specific promises. It asks one question at a time. It adds nothing the person didn't say. It helps with worry as well as the story, and it never diagnoses anyone. Those promises deserve the same rigour as any other product requirement, so this kit:

- makes each promise explicit, in a file anyone can read
- checks the coach against realistic conversations, including the difficult ones
- runs automatically, so a change that breaks a promise shows up straight away

## What the First Run Found

I recorded the live New Leaf coach answering ten realistic conversations on 23 October 2026. It passed five of the ten, against a target of eight.

The good news first. It never invented a figure, it refused to ghostwrite a whole CV and it handled someone in a very low moment with real care, checking gently for risk and giving the Samaritans number.

The evals also caught my own coach breaking my own house style. It sometimes ends a sentence on a preposition ("what were you responsible for?") and sometimes asks a second, follow-up question when the promise is one at a time. Those are exactly the small drifts that slip past a demo. They're now on the backlog, with a test that will prove the fix. The full results are in [`reports/new-leaf-coach.md`](reports/new-leaf-coach.md).

## How It Works

```
coaches/new-leaf-coach/
├── requirements.yml   the coach's promises, written for people
├── cases.yml          realistic conversations and the checks each reply must pass
└── recorded.yml       real replies captured from the live coach
evals/
├── checks.py          small, explainable checks
├── runner.py          runs the cases and writes the report
└── record.py          captures fresh replies from a live coach
```

1. **Promises** live in `requirements.yml`. They're for humans and never executed.
2. **Cases** in `cases.yml` pair a conversation with the checks that matter for it. Each case also says *why* it matters, so a failure reads as a product risk rather than a red cross.
3. **Checks** in `checks.py` are deliberately simple, so anyone can read one and agree with it.
4. **Replies** come from `recorded.yml` by default. That keeps the evals free, fast and repeatable in CI. Re-record whenever the prompt or model changes.

### The Checks

| Check | What It Protects |
|---|---|
| `asks_one_question` / `asks_at_most_one_question` | Nobody should feel interrogated |
| `adds_no_new_numbers` | No invented figures, which could cost someone a job |
| `no_diagnosis` | Coaching isn't therapy, and it never labels a person |
| `signposts_support` | Someone in distress is pointed to real help |
| `max_words` | Replies stay readable on a phone |
| `must_not_contain` / `must_contain_any` | Phrases a coach must avoid or include |
| `no_em_dashes`, `uk_spelling`, `no_oxford_comma`, `no_stranded_prepositions`, `no_ai_tells` | My house style, so the coach sounds human and British |

The house style checks run on every case unless a coach switches them off with `house_style: false`.

## Getting Started

You'll need Python 3.10 or later.

```bash
git clone https://github.com/elleanderson/ai-coach-evals.git
cd ai-coach-evals
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest -q                                          # test the checks themselves
python -m evals.runner new-leaf-coach --report     # run the evals on recorded replies
```

### Testing a Live Coach

Any coach that accepts `POST {"messages": [...]}` and returns `{"reply": "..."}` can be tested directly.

```bash
python -m evals.runner new-leaf-coach --live https://your-coach.example/
python -m evals.record new-leaf-coach https://your-coach.example/   # refresh recorded.yml
```

### Adding Your Own Coach

Copy `coaches/_template`, rename the folder after your coach and write your own promises and cases. The test suite checks that every case is well formed before anything runs.

## Continuous Integration

Every push runs the unit tests and the New Leaf evals on GitHub Actions, and publishes the eval report to the run's summary page. The eval step reports rather than blocks, because a coach falling short of its target is a product conversation, not a broken build.

## About Me

I'm [Elle Anderson](https://andersonco.uk), a product leader and executive coach (Fellow, Chartered Institute for IT). I help senior teams turn AI from a slide into a product decision, with the evidence, guardrails and economics to back it. If you'd like a chat about evals for your own AI features, you can [book a consultation](https://andersonco.uk/book).

You might also like my [AI Glossary for Product Leaders](https://andersonco.uk/ai-glossary), which explains evals, drift, hallucination rate and thirty-seven other terms in plain English.

## Licence

MIT. Use it, adapt it and build on it.
