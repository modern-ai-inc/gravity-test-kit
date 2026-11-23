# Gravity test kit

Ask your AI assistant twelve ordinary business questions about your own data, and count how many figures it gets wrong.

It is meant to fit in one sitting and needs no IT work and no install beyond Python 3. The kit itself sends nothing anywhere. You ask the AI you already use, under your company's own rules for it, and you score the answers on your own computer.

## Why the figures go wrong

An AI assistant can write a correct query and still give the wrong figure. Most business questions hide a choice that your company made long ago: what "active" means, which quarter is "last quarter", which orders do not count, what comes off to get to net. Your finance team knows these choices. The AI does not, and it rarely says it is guessing. The kit counts how often that happens on your own data.

## Is this safe to run?

Do not take our word for it: check it. Below is everything the kit does, so you (or your own AI assistant) can check each point against the code before anyone runs it.

**What is in this repository**

- Text files: this README, `QUESTIONS.md`, and the license and policy files.
- Two blank spreadsheets (`answer_key.csv`, `ai_answers.csv`) and a filled-in example in `example/` for a made-up company.
- `score.py`: one Python script, 136 lines, that uses only Python's standard library (`csv`, `re`, `sys`, `decimal`, `pathlib`). Its tests are in `tests/`.

**What `score.py` touches**

- It reads the two spreadsheet files you name on the command line, and nothing else.
- It writes one new file, `results.csv`, in the same folder as `ai_answers.csv`. If that name is taken, it writes `results-2.csv`, and so on. It never overwrites or deletes a file. Any cell that a spreadsheet could read as a formula (one that starts with `=`, `+`, `@` or a stray `-`) is written as plain text.
- It does not open a network connection, call any AI, read your data, read other files, run other programs, or need an install or admin rights.

**What the kit does not do**

- It calls no AI. You ask your own AI assistant the questions yourself, the same way you already use it.
- It sends nothing anywhere. Nothing goes to Modern AI or to anyone else. Your answer key and results stay on your computer.
- It does not connect to your data. When you ask your AI a question about your data, your AI reads that data under your company's existing setup and rules for it. The kit adds no new access. Use an AI assistant your company already allows for this data.

**Keep your filled-in files private**

Your answer key and results hold real business figures (revenue, churn, headcount). Keep the filled-in files on your company's own storage. Do not paste the answer key into a chat with the AI, and do not commit the filled-in files to any repository. `.gitignore` already leaves out every `results*.csv` file.

**How much of your AI usage a run takes**

A full run is twelve questions, each asked in a normal chat with your AI assistant. That is about the same as twelve ordinary questions a manager might ask it in a day. An assistant that looks things up in a database usually takes several steps per question (read the table list, write a query, read the result); in our own tests this was about 5 to 8 steps each. The quick version (below) is 3 to 5 questions. Costs are in "What this costs you", below.

## What this costs you

The kit itself is free and costs nothing to run: `score.py` is simple arithmetic on your own computer.

The only cost is the questions you ask your own AI assistant:

| How you pay for your AI | Quick version (3 to 5 questions, once) | Full run (12 questions, once) | Full run, each question asked 3 times |
|---|---|---|---|
| A flat monthly plan (for example a ChatGPT or Claude subscription) | No extra cost | No extra cost | No extra cost |
| Paid per use, a leading model | About $0.15 to $1 | About $0.60 to $2.50 | About $2 to $7 |
| Paid per use, a lower-cost model | Under $0.25 | About $0.30 to $0.70 | About $1 to $2 |

These are estimates from our own tests on a small sample database, not a quote. Each question costs more when your AI reads a large table list or large query results, so on a big database a run can cost two to five times more. If your AI runs live queries on a data warehouse that bills per query (for example Snowflake or BigQuery), each question also costs a little warehouse time; ask the person who owns the warehouse if you are unsure. To keep it low: start with the quick version, ask each question once, and use a flat-plan assistant for a first try.

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

**Short on time?** Use the quick version in `QUESTIONS.md`: 3 to 5 of the questions, each asked once. The steps are the same.

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
