from pathlib import Path

from connection import get_conn

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

def run_migrations():
    with get_conn() as conn:
        with conn.cursor() as cur:

            # Get all SQL files in order
            sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

            # If not SQL files, return.
            if not sql_files:
                print("No migration files found.")
                return
            
            # Run migration for all SQL files listed
            for sql_file in sql_files:
                print(f"Running migration: {sql_file}")
                with open(sql_file, "r") as f:
                    sql = f.read()
                try:
                    cur.execute(sql)
                    # Commit happens automatically in context manager
                except Exception as e:
                    # Roll back happens in context manager
                    print(f"Error running migration: {sql_file}")
                    raise e
    print("Migrations complete.")

def drop_tables():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS candidates CASCADE")
            cur.execute("DROP TABLE IF EXISTS candidate_profiles CASCADE")
            cur.execute("DROP TABLE IF EXISTS candidate_resume CASCADE")
    print("Tables dropped.")

if __name__ == "__main__":
    run_migrations()
    #drop_tables()
    
