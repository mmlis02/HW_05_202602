ntegrative Project: From Voice to Record — Interview Intake and Sales Call Capture
Total value: 20 points

This project consists of two connected tasks that apply automatic speech recognition (ASR) to the same problem: audio that nobody processes.

Task 1 answers "What did this candidate actually say?" — you turn a recorded job interview into a structured candidate record.
Task 2 answers "Did the order come through correctly?" — you turn a sales call into an order record that checks itself, reusing the engine you built in Task 1.
The project is presented through a single video.

Innovation: points earned for innovation are additional to the 20 base points.

General Information
Deadline: Friday, October 30, 2026

Repository submission: register your repository in the course spreadsheet.

No starter code is provided. This assignment tells you what your system must achieve and how it will be checked. The design is yours, and you will defend it in the video.

This assignment is strictly individual
No groups. No shared repositories. No videos with more than one person presenting. Each student registers their own repository, writes their own code, and records their own video.

You record your own audio. This is the condition of the assignment
There is no corpus to download. You and a classmate record the interviews and the sales calls yourselves, taking turns as speaker A and speaker B.

This is not a logistical detail: it is what guarantees the work is yours. Your corpus does not exist on the internet. It cannot be downloaded, inherited from a previous term, or produced by an agent. Every number in your report comes from audio you made.

Rules for recording:

You appear in every clip of your own corpus. You may record with different classmates, but you are always one of the two voices.
No two students may submit the same audio files. You and your recording partner each build your own set. Overlap in participants is fine; identical corpora are not.
Everything said is invented. No real salaries, no real addresses, no real personal data, from anyone. State this in your README.
Everyone who appears agreed to it. Add one line to your README confirming it, and name no one who did not agree to be named.
Record with whatever you have. A phone is fine and is in fact the realistic case.
Use of AI coding agents: Claude Code, Codex and similar tools are allowed and encouraged. Submitting code you cannot explain is not. In the video you will be asked to explain your pipeline, and you may be asked to modify a part of your code live.

Repository submission:
https://docs.google.com/spreadsheets/d/1CdYa-YDoPvhCm1MvD1j7ISDLRvByqbQLgn1I42dLTyY/edit?usp=sharing
The Problem — The audio nobody processes
Your phone already transcribes voice notes. Every student here knows that. So the first question this assignment must answer is why you would build anything at all.

What already exists	What it does	What is missing
Keyboard dictation	Short phrases while you speak	Nothing is stored
WhatsApp voice-note transcription	Shows you the text	No row in a database
YouTube auto-captions	Subtitles long video	No speakers, nothing measurable
Zoom, Teams, Meet captions	Meeting subtitles	The audio leaves your organization
Otter.ai, Fireflies	Meeting notes	Paid per minute, data abroad
Transcription is where the work starts, not where it ends. What an organization needs is not text: it is fields, verified, in a table, with a measurement of how much to trust them.

Feasibility Evidence
Verified by the teaching team before publishing. These are conditions you will meet. Handling them is the assignment.

Finding	Implication for you
Synthesized audio is too clean: a large model transcribes it almost perfectly	A corpus of synthetic speech has nothing to measure. Real recordings are required
With faster-whisper, Whisper large measured 2,926 MB of VRAM at int8 against 4,525 MB at float16	Quantization decides whether the large model fits your card
ASR stacks fall back to CPU silently when the GPU is unavailable: no error, everything works, forty times slower	You must prove the GPU was used with a measurement, not with a configuration file
GitHub Actions standard runners have no GPU	Any workflow must evaluate cached transcriptions, never re-transcribe
YouTube auto-captions are the output of another ASR system	Using them as ground truth measures agreement with Google, not accuracy
Edge TTS offers Peruvian Spanish voices with no API key	Available for optional augmentation, clearly separated from your real recordings
The circular-evaluation trap. If you score your transcription against machine-made captions, you are not measuring accuracy: you are measuring how much your model resembles another model. If both are wrong in the same way, your error rate reads as zero. Ground truth must be written by a human or authored by you.

Mandatory Scope
The corpus
Task 1 — Interviews	Task 2 — Sales calls
Clips	4 to 5	4 to 5
Length each	2 to 4 minutes	2 to 4 minutes
Roles	A interviews, B is the candidate	A sells, B is the customer
Source	Your own recordings	Your own recordings
That is roughly 16 to 20 minutes of interview audio and 16 to 20 minutes of call audio. Plan one recording session per task.

On the small sample. Twelve interviews times six fields gives around seventy field observations. That is enough to see an effect and not enough to be precise. Report confidence intervals and say plainly what your sample cannot support. Pretending a sample of twelve settles a question is a worse error than having twelve.

Optional augmentation. You may add synthesized clips to increase statistical power, with two conditions: they are reported as a separate group, never mixed into your main numbers, and you state how many. A public corpus such as OpenSLR 73 may be used for a real-human-voice baseline, also reported separately.

Everything else
Ground truth. For every clip you hold both the exact transcript and the correct field values. Writing the script before recording is what makes this free.
ASR model. Any Whisper family model or a justified alternative. The model must support Spanish — several models at the top of public ASR leaderboards are English-only.
GPU is required for at least one measured comparison. Google Colab's free tier is enough. Not having a local GPU is not an exemption.
One engine, two tasks. All transcription and extraction logic lives in one module exposing one function that takes an audio path and returns a structured result: the transcript, the fields, which fields were verified, the device used, the elapsed time and any error. The app only calls that function, and the engine must not import any UI library. State in your README the command you use to verify this.
Configuration outside the code. Every path, model name, threshold and prompt lives in config.yaml. Credentials live in .env and never reach the repository.
TASK 1 — Interview Intake
Value: 6.0 points

Objective
Turn a recorded job interview into a candidate record with six fields, and report how much you can trust each one.

Field	Type	Why it is here
anios_experiencia	Numeric	The same target as the CV assignment, now spoken
ultimo_puesto	Text	Free text, hardest to verify
tecnologias	List	Proper nouns the model has never heard inside Spanish
pretension_salarial	Numeric with currency	The most fragile: "seis mil quinientos" against 6500
disponibilidad	Date or category	Said relatively, stored absolutely
nivel_ingles	Categorical	Few classes, so it is scored with macro F1
The mix of types is deliberate. A categorical field survives a high error rate; a salary figure does not. Explaining that asymmetry is part of the grade.

Phase 1 — Corpus and ground truth
Value: 1.5 points

Write the scripts before recording. A sample script is provided in the appendix. Use it as a model for how to formalize the questions, then write your own with your own invented data. You are free to change the questions, the order and the wording; what you may not do is submit the appendix unchanged.
Vary where each field appears. A corpus where every candidate says the same sentence in the same position teaches your extractor nothing, and your results will not transfer. Report how you varied it.
Record 4 to 5 interviews of 2 to 4 minutes, following the recording rules above.
Produce the ground-truth table: one row per clip, the six correct field values, plus the reference transcript.
Report the distribution of each field.
Phase 2 — Transcription on GPU
Value: 1.5 points

Transcribe with at least two model sizes. Report word error rate (WER), character error rate (CER), seconds per minute of audio, and peak VRAM measured.
Compare CPU against GPU on the same clips, and at least two numeric precisions (for example float16 against int8). Report whether the transcription text changed, not only whether it got faster. Faster and worse is not an improvement.
Prove the GPU was used. Report the device read from the library at run time, not from your configuration, and the measured VRAM that backs it. A pipeline that silently ran on CPU and a pipeline that used the GPU look identical in the output text; only the measurement separates them.
Domain glossary. Transcribe once plain and once passing your domain vocabulary to the model, and measure the difference with a confidence interval. Check your library's documentation for which mechanism it supports and in which version: the public documentation on this point is inconsistent, and resolving it is part of the work.
Before comparing any two texts, normalize both the same way. Otherwise a full stop or a capital letter counts as an error and your rate is inflated. State your normalization rule.

Phase 3 — From text to record
Value: 2.0 points

Implement two extraction paths and compare them on the same clips: rules (regular expressions) and a language model returning structured JSON.

The verification rule. Every extracted value must exist literally in the transcript. If it does not, the field is marked sin_verificar. A model that silently corrects what the ASR misheard and happens to be right is as dangerous as one that invents, because next time it will correct and be wrong.

Numbers spoken as words. "seis mil quinientos" in the transcript against 6500 in the record fails literal verification even when everything is right. Build the normalization layer that resolves this and document its rules. This problem does not exist on paper; it is specific to audio.

Two layers of metrics, reported separately:

Layer	Metrics	Question answered
Transcription	WER, CER	Did it hear the words?
Record	Per-field accuracy, macro F1 on the categorical field, absolute error on the numeric fields	Is the data usable?
The question you must answer with your own numbers: can you tell whether the record is usable by looking at WER alone? Show one clip with a high error rate and a perfect record, and one with a low error rate and a broken record. Explain what that means for anyone who reports only WER.

Phase 4 — Application
Value: 1.0 point

A Streamlit app with four tabs: problem and method; the corpus, with an audio player and the transcript beside it; results, with both metric layers; and an interactive tester where you upload a clip and see the transcript, the record and which fields were verified.

The app loads precomputed results. It must not re-transcribe the corpus at start-up.

TASK 2 — Sales Call Capture
Value: 6.0 points

Objective
Turn a sales call into an order record that checks itself, and measure how it degrades as the audio gets worse.

Choose one domain and state it in your README:

Domain	What is sold
Restaurant	Dishes, sizes, quantities, promotions, delivery address
Mobile telephony	Plan, data allowance, handset in instalments, promotion, contract term
Both have the same shape: items with prices, a promotion, and a total said out loud. Pick the one you can act out convincingly.

Field	Type
items	List of objects: product, size or tier, quantity, unit price
promocion	Text or null
direccion_entrega or plazo_contrato	Text
metodo_pago	Categorical
total_dicho	Numeric
Phase 1 — Call corpus
Value: 1.0 point

4 to 5 calls of 2 to 4 minutes, recorded with a classmate, following the rules above. A sample script is in the appendix; write your own from it.

Your corpus must deliberately contain:

At least 3 calls where the customer corrects themselves mid-order. The record must hold the final order, not the first one.
At least 3 calls where the stated total is wrong on purpose. Your validator in Phase 3 needs real mistakes to catch, and if every call adds up you have measured nothing.
At least one address or contract number containing digits.
Mark in your ground-truth table which calls carry which trap. You will need it to score the validator.

Phase 2 — Robustness: the degradation ladder
Value: 1.5 points

A real call is not a quiet room. Build a reproducible ladder and measure both metric layers at every level.

Level	Simulates	Transformation
L0	As recorded	Unmodified
L1	WhatsApp voice note	Low-bitrate compression, mono
L2	Phone call	Band-limited to roughly 300–3400 Hz, resampled to 8 kHz
L3	Noisy environment	L1 plus ambient noise at a stated signal-to-noise ratio
Choose and justify the signal-to-noise ratio, and state how you measured it rather than saying you "added noise".

Report the curve of WER and of field accuracy across the ladder. If your record is still perfect at L3, your ladder is not degrading enough: say so and harden it.

Phase 3 — The order record and arithmetic validation
Value: 2.0 points

This is where this task differs from Task 1 and from every tutorial on the subject.

Extract the order record with the engine from Task 1.
Cross-check the fields against each other. Quantity times unit price, summed, minus the promotion, must equal total_dicho. When it does not, your system has found a problem with no ground truth at all.
Diagnose the mismatch. A failed check has at least two causes: the ASR misheard a number, or the speaker made a mistake. Propose a rule that tells them apart, apply it, and report how often it is right.
Report, per level of the ladder, how many broken records your check caught and how many it missed, using the traps you planted in Phase 1.
This is the step where the system stops transcribing and starts understanding. A record that cannot be checked is only a guess written down neatly.

Phase 4 — Engine reuse and pipeline documentation
Value: 1.5 points

Task 2 must call the same engine function as Task 1. Show in your README how one module serves two different record schemas. If you copied and edited it instead, say so and explain what that costs when the model changes.

Extend the app with the order view: the ladder, the validation results, and the caught-against-missed table.

Pipeline documentation in a visual tool. This is required, not optional. Your pipeline must be documented in Notion, Miro or an equivalent, publicly viewable and linked from your README. Markdown with a Mermaid diagram is the fallback only if the tool fails you, and you must explain why.

The document must show what runs once (scripts, recording, transcription, caching) and what runs on every new audio file (transcription, extraction, verification, validation), plus the decisions you took at each step and what you rejected.

Why this is required: a pipeline you can draw is a pipeline you understand. When an agent writes part of your code, the diagram is what proves you know the order of the steps and why each one exists.

Declare your tools. A short README section listing which AI agents you used and which MCP servers you connected in Claude Code, one line on what each did for you.

Presentation
Value: 8.0 points

A single video, maximum 8 minutes, recorded by you alone.

The pipeline-first rule
The video must explain the complete pipeline of both tasks before showing a single line of code. If the first technical content of your video is code, the criterion Pipeline explained before code is graded zero.

Suggested structure
Time	Content	On screen
0:00–1:00	The problem, and why your phone is not enough	Slides
1:00–3:00	The pipeline of both tasks: what runs once, what runs per audio	Your Notion or Miro
3:00–5:00	Technical decisions with their numbers: corpus, GPU, glossary, ladder	Tables and charts
5:00–7:00	Live demonstration, including the arithmetic check catching a planted error	App running
7:00–8:00	Findings, limitations and what your sample cannot support	Report
While explaining, you must say
Where your ground truth came from, and why it cost nothing.
The evidence that the GPU was actually used.
Why word error rate does not predict whether the record is usable.
What your arithmetic check catches, and what it misses.
What your system must never be used for.
Criterion	Points
Pipeline of both tasks explained before any code	2.0
Live demonstration of the working application	2.5
Defence of technical decisions, with numbers	2.0
Findings, limitations and honest interpretation	1.5
Total	8.0
Deliverables

Own public GitHub repository, individual, worked through branches and pull requests, with commits distributed over time.

README.md: setup, run commands, the link to your pipeline document, both results tables, the declaration of AI tools and MCP servers, the consent and invented-data statements, and the limitations.

Your recording scripts, and the ground-truth table for both corpora.

Cached transcriptions committed. Audio files and model weights are not committed: explain how to regenerate or request them.

config.yaml, .env.example with names only, requirements.txt with pinned versions.

The shared engine module, plus extraction, metrics and validation modules.

Both metric layers for both tasks, and the degradation curve.

app.py, running with a single command after installing requirements.

Pipeline document in Notion, Miro or equivalent, publicly viewable.

A single video of up to 8 minutes, linked in the README.
Checkpoints
Day	Checkpoint
1	Repository created. Scripts written. Pipeline document started
2	Both recording sessions done. Two clips transcribed end to end
3	Full ground-truth tables. GPU comparison measured
4	Task 1 extraction working, both paths, verification rule and number normalization
5	Degradation ladder and arithmetic validation with its diagnosis rule
6	App, pipeline document finished, README
7	Video
Record on day two, not on day six. Recording depends on another person's schedule, which is the one thing you cannot fix at midnight. Transcribe two clips end to end before the full session, so you discover any problem while it is still cheap.

Evaluation Criteria
Task	Phase	Criterion	Points
1	1	Corpus, scripts and ground truth	1.5
1	2	Transcription on GPU, with measured evidence	1.5
1	3	Extraction, verification rule and the two metric layers	2.0
1	4	Application	1.0
2	1	Call corpus with planted traps	1.0
2	2	Degradation ladder	1.5
2	3	Order record and arithmetic validation	2.0
2	4	Engine reuse and pipeline documentation	1.5
—	—	Video	8.0
—	—	Innovation	+extra
Total	20.0
Code organization, respect for the one-engine architecture, absence of hardcoded values, credential security and reproducibility are assessed within each phase.

Innovation
Innovation	What it adds
A pipeline that writes to Notion	Not documenting in Notion, which is already required, but having each run post to it: its metrics, its decisions and its failures. The reasoning of the system becomes readable by someone who did not build it
GitHub Actions regression gate	A workflow that recomputes metrics from cached transcriptions and fails when quality drops below your threshold. The runners have no GPU: a workflow that tries to transcribe will not work, and understanding why is the point
Telegram bot	Send a voice note, receive the structured record. It must call the same engine function, with a user allowlist and a per-user limit
Your own MCP server	Expose your engine as a tool so an agent in Claude Code can transcribe and extract
Speaker separation	Who spoke when. In the sales calls it lets you attribute the correction to the customer rather than the operator. The common library requires accepting terms and a token
The accent axis	Generate the same script with synthesized voices from several Spanish locales and measure whether the error rate changes. State clearly that these are synthetic voices, not human speakers: the result describes how the model treats those voices, not real accents
Public deployment	The app reachable at a URL, with no cloning or configuration
Appendix — Sample scripts
These are models to show you the shape, not scripts to submit. Write your own, with your own invented data. You may change the questions, the order and the wording.

A.1 Interview (Task 1)
Note what the script is doing: every one of the six fields is said out loud, but none of them is said cleanly. That is on purpose, and your own scripts should do the same.