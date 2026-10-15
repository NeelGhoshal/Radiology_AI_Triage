"""Load the generated tables into Snowflake (FERNBROOK.SERVICE) with write_pandas.

Run data/ddl.sql first (it creates the tables). Credentials come from .env.
Usage: python data/load_snowflake.py [--csv-dir data/out]
"""
import argparse
import os
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

LOAD_ORDER = ["PLANS", "MEMBERS", "ACCUMULATORS", "CLAIMS", "PRIOR_AUTHS",
              "SERVICE_REQUESTS", "INTERACTIONS", "CALL_TRANSCRIPTS", "CASE_NOTES"]
DATE_COLS = {"MEMBERS": ["DOB"], "CLAIMS": ["SERVICE_DATE"]}
TS_COLS = {"ACCUMULATORS": ["AS_OF"], "CLAIMS": ["UPDATED_AT"], "PRIOR_AUTHS": ["SUBMITTED_AT", "DECIDED_AT"],
           "SERVICE_REQUESTS": ["OPENED_AT", "CLOSED_AT"], "INTERACTIONS": ["STARTED_AT"], "CASE_NOTES": ["CREATED_AT"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv-dir", default=str(Path(__file__).parent / "out"))
    csv_dir = Path(ap.parse_args().csv_dir)
    load_dotenv()
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"], role=os.environ.get("SNOWFLAKE_ROLE", "FERNBROOK_LOADER"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "FERNBROOK_WH"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "FERNBROOK"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "SERVICE"))
    try:
        for name in LOAD_ORDER:
            df = pd.read_csv(csv_dir / f"{name}.csv")
            for c in DATE_COLS.get(name, []):
                df[c] = pd.to_datetime(df[c]).dt.date
            for c in TS_COLS.get(name, []):
                df[c] = pd.to_datetime(df[c])
            # Tables already exist from ddl.sql; overwrite=True truncates, keeping grants/types.
            ok, _, nrows, _ = write_pandas(conn, df, name, auto_create_table=False, overwrite=True,
                                           use_logical_type=True)
            print(f"{name:18s} {nrows:>7,d} rows  ok={ok}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
