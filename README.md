# Call Insights – AI Call Analysis & Admin Portal
Run: `pip install -r requirements.txt` → (optional) copy `.env.example` to `.env` and add a free Gemini key → `python app.py` → open http://localhost:5000
Audio is pre-generated in `audio/`; regenerate with `python generate_audio.py` (needs espeak-ng).

## Approach
**Sentiment:** customer-only utterances are scored with a polarity lexicon: (pos − neg)/(pos + neg + 2) ∈ [−1, 1]. >0.25 Positive, <−0.1 Negative, else Neutral. With a Gemini key, the LLM also labels sentiment and writes insights from the full transcript.
**Purchase probability:** logistic model z = −0.5 + 0.2·buying_signals − 0.35·objections + 1.5·polarity + 0.1·questions, p = σ(z), clamped to 3–95%. With Gemini, the final value is 0.6·LLM + 0.4·local model (ensemble reduces LLM variance). Weights are hand-calibrated; with labelled outcomes they could be fitted via logistic regression.
**API:** GET /api/calls, /api/calls/<id>, /api/calls/<id>/analysis, /api/calls/<id>/report (PDF), /audio/<file>.
"# call-analytics" 
