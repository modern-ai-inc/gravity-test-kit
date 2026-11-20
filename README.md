# Gravity test kit

Ask your AI assistant twelve ordinary business questions about your own data, and count how many figures it gets wrong.

It is meant to fit in one sitting and needs no IT work and no install beyond Python 3. The kit itself sends nothing anywhere. You ask the AI you already use, under your company's own rules for it, and you score the answers on your own computer.

## Why the figures go wrong

An AI assistant can write a correct query and still give the wrong figure. Most business questions hide a choice that your company made long ago: what "active" means, which quarter is "last quarter", which orders do not count, what comes off to get to net. Your finance team knows these choices. The AI does not, and it rarely says it is guessing. The kit counts how often that happens on your own data.

## What you need

- An AI assistant that can answer questions about your data (for example one connected to your warehouse, a BI tool's AI, or a coding agent with database access).
- One person who knows the right figures, from a source your company already trusts (the finance close, the board pack, a signed-off report).
- Python 3.9 or later, to run `score.py`. Nothing else to install.

## The five steps

1. **Fill in the blanks.** Open `QUESTIONS.md`. Replace each blank, such as `{customers}` and `{month}`, with your own words. Copy the filled-in questions into the `question` column of both `answer_key.csv` and `ai_answers.csv`, word for word.

2. **Write the right answers first.** The person who knows the figures fills in `answer_key.csv`: the `right_figure`, the `definition` used, and the `source`. Keep this file away from whoever asks the AI, so the test stays blind. `tolerance` is how far off a figure may be and still count as right, in the same units (for example `0`, `$100` or `0.1%`).

3. **Ask the AI.** In a fresh conversation, ask each question exactly as written, one at a time, and give no hints. Ask on the same day the right answers were written, because "last quarter" and "so far this month" depend on the date. In `ai_answers.csv`, write the one figure the AI gave in `ai_figure` as a plain figure (`1,190`, `$18,400`, `2.4%`, or `up`/`down`). Q09 and Q10 ask for several figures in one reply: write each figure the AI gave in its own row, with the same ids as in the answer key (`Q09-<group>`, `Q09-total`, `Q10-direction`, `Q10-change`). For any row where the AI gave no figure, leave `ai_figure` empty. Paste its whole reply into `full_answer` if you want a record.

4. **Score.**

   ```
   python3 score.py answer_key.csv ai_answers.csv
   ```

   It prints how many figures were right, wrong, or missing, and writes `results.csv`. It never overwrites one: a later run writes `results-2.csv`, and so on. A figure written with a different currency sign ($, £ or €) from the right answer counts as wrong. Write figures with a sign or with none, not with a currency code such as EUR: a code is not read as a figure.

5. **Find the causes.** For each wrong figure, write in the `cause` column why it went wrong: `definition`, `time window`, `double counted`, `filter`, `missing data` or `other`. The `definition` column in your answer key usually shows it.

Try it first on the made-up company in `example/`:

```
python3 score.py example/answer_key.csv example/ai_answers.csv
```

## Rules that keep the result fair

- Write the right answers before anyone asks the AI, and do not show them to the person asking.
- Use the same words in both files. `score.py` stops if they differ.
- Do not rephrase a question after the AI answers it, and do not drop a question because the AI got it wrong.
- Ask each question more than once, in fresh conversations, if you can. An AI can be right once and wrong the next time. Record each try as its own row (for example `Q01-a`, `Q01-b`) with the same right answer.
- Say what you counted, not a percentage: "4 of 14 figures were wrong."

## What the kit does not do

It does not connect to your data, call any AI, or send results anywhere. It does not find the causes for you or fix the wrong figures: it shows which figures are wrong, and you find why, using the definitions in your answer key.

## About

Made by Modern AI. Modern Gravity, our paid product, gives an AI your company's own definitions and checks each figure before anyone sees it. This kit works without it.

## License

MIT for the code and the questions. See `LICENSE`, `NOTICE` and `TRADEMARKS.md`.
