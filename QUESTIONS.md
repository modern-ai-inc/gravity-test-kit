# The questions

Twelve questions. Each is a plain business question of the kind a manager types into an AI assistant. Each one also hides a choice that your company has already made and that the AI cannot see: which records count, which dates, which definition. That hidden choice is what the kit tests.

## Before you start: fill in the blanks

Each question has blanks in curly brackets. Fill each blank once, with your own words, before anyone asks the AI anything. Use the words your managers use, not table or column names.

| Blank | What to write | Example |
|---|---|---|
| `{customers}` | What you call the people or companies who buy from you | customers, accounts, members, clients |
| `{orders}` | What you call one sale | orders, deals, bookings, invoices |
| `{revenue}` | Your main money figure | revenue, sales, bookings |
| `{people}` | People you count over time | employees, staff, subscribers, members |
| `{segment}` | One group of customers you report on | enterprise customers, the West region |
| `{group}` | A way you split a figure in reports | region, product line, sales channel |
| `{month}` | The last full calendar month | October 2026 |
| `{earlier_month}` | The month before it | September 2026 |

Write the filled-in questions into `answer_key.csv` (column `question`) and `ai_answers.csv` (column `question`). The words must be the same in both files.

## The twelve

| id | Question | The hidden choice |
|---|---|---|
| Q01 | How many active {customers} did we have at the end of {month}? | What "active" means at your company |
| Q02 | How many {people} did we start {month} with? | Count on the first day of the month, not the number who joined in it |
| Q03 | What was our {revenue} last quarter? | Calendar quarter or your fiscal quarter |
| Q04 | What is our {revenue} so far this month? | Today's date, and that the month is not over |
| Q05 | What was our total {revenue} from {segment} in {month}? | Counting each sale once when one sale has many lines or many matches |
| Q06 | How many {orders} did we have in {month}? | Leaving out cancelled, test, internal or returned {orders} |
| Q07 | What was our churn rate for {customers} in {month}? | Which {customers} form the base, and whether the rate is monthly or yearly |
| Q08 | What was the average {revenue} per {orders} in {month}? | Which {orders} count, and whether zero-value ones are included |
| Q09 | What was {revenue} by {group} in {month}? Give each {group} and the total. | Records with no {group}, and whether the parts add up to the total |
| Q10 | Did {revenue} go up or down from {earlier_month} to {month}, and by how much? | Both months on the same definition |
| Q11 | How many different {customers} bought from us in the last 12 months? | Each customer once, and which 12 months |
| Q12 | What was our net {revenue} in {month}, after refunds and discounts? | What your finance team takes off to get to net |

## The quick version

Short on time, or want to try it at the lowest cost first? Use 3 to 5 of these five questions, each asked once:

| id | Why it is in the quick version |
|---|---|
| Q01 | "Active" is defined differently at almost every company |
| Q03 | Calendar quarter or fiscal quarter |
| Q06 | Which orders do not count |
| Q11 | Each customer once, over which 12 months |
| Q12 | What comes off to get to net |

Each gives one figure, so it is one row in each file. Leave the other questions out of both files. Everything else works the same way.

## The right answers

For each question, a person who knows your numbers writes the right figure into `answer_key.csv` from the source your company already trusts: the finance close, the board pack, a signed-off report. Not from the AI, and not from a new query written for the test.

Also write, in a few words, the definition you used (`definition` column). It turns a wrong figure into a fix.

Q09 has one figure per {group} plus a total. Give it one row per figure, with ids `Q09-<group>` and `Q09-total`. Q10 has two figures: the direction (`up` or `down`) as `Q10-direction` and the change as `Q10-change`. Use the same ids in `ai_answers.csv`, one row for each figure the AI gave.

## If a question does not fit

Leave it out of both files. Fewer questions is fine. Do not swap in a question you already know your AI gets right: the kit is meant to find what your AI cannot know.
