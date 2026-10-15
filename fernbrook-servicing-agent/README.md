# Fernbrook Member Services Agent: Snowflake layer

Snowflake is the system of record. Data 360 federates it (zero copy) and Agentforce reads it.
This folder holds the Snowflake side: DDL, a reproducible synthetic data generator, a loader and
verification queries. All data is synthetic.

## Step-by-step setup

### 1. Snowflake trial
1. Sign up for a Snowflake trial, **Enterprise** edition ($400 credit, 30 days).
2. Note your **account identifier** (`orgname-accountname`: Admin, Accounts, hover over the account) and region.

### 2. Create warehouse, database, roles (about 5 minutes)
1. Open `data/ddl.sql` in a Snowflake worksheet.
2. Replace `<YOUR_SNOWFLAKE_USER>` and `<STRONG_PASSWORD>`.
3. Run the whole script. It creates:
   - `FERNBROOK_WH`: XSMALL, `AUTO_SUSPEND = 60`
   - `FERNBROOK.SERVICE` and nine tables (uppercase columns; **do not rename them later**, federation can't follow)
   - `FERNBROOK_LOADER` (writes) and `FERNBROOK_D360_RO` + `D360_RO_USER` (read-only, for Data 360)

### 3. Generate the data
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python data/generate.py          # writes data/out/*.csv and plan_rules.json
```
Deterministic (seed 42, fixed "today" of 2026-10-01). The generator plants the five seed stories:

| # | Story | Where |
|---|---|---|
| 1 | Claim denied for missing prior auth | `M0000001`, appeal path |
| 2 | 3 contacts in 7 days about one claim | `M0000002` |
| 3 | Same imaging benefit, different PA rules | `M0000003` (HMO: PA needed) vs `M0000004` (PPO: not needed) |
| 4 | Case note contradicts the plan document | note says "no PA for MRI on Silver HMO"; the document will say PA is required |
| 5 | Intent volume skewed to 4 intents | `INTERACTIONS` |

Also planted: two prompt-injection case notes for the adversarial eval cases.
Demo IDs are in `data/out/plan_rules.json`.

### 4. Load into Snowflake
```bash
cp .env.example .env     # fill in account, user, password (git-ignored)
python data/load_snowflake.py
```

### 5. Verify
Run `data/verify.sql` in a worksheet and compare the counts and story checks with the comments in it.
It also checks the read-only role can SELECT but cannot write.

### 6. Connect Data 360 (the risky step, do it first on the Salesforce side)
1. Data 360 Setup, Other Connectors, Snowflake. Use `D360_RO_USER`, `FERNBROOK_WH`, `FERNBROOK`, `SERVICE`.
2. Create **query federation** data streams for the structured tables. Done when you can query `CLAIMS` from Data 360.
3. For `CALL_TRANSCRIPTS` and `CASE_NOTES`, turn **acceleration** on (needed for a search index).
4. Blocked by mid-afternoon? Fall back to `sf data import` into custom objects.

## Notes
- `INTERACTIONS.CLAIM_ID` is an addition to the planned schema. The "3 contacts about the same claim in 7 days" rule needs it.
- Warehouse auto-suspends after 60 seconds to protect trial credits.
- Never commit `.env` or passwords.
