import os, sys

# Set directory to root
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# print(project_root)
sys.path.insert(0, project_root)

from database.connection import get_conn

with get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM candidates")
        print(f"Candidates count: {cur.fetchone()[0]}")
        
        cur.execute("SELECT COUNT(*) FROM candidate_profiles")
        print(f"Embeddings count: {cur.fetchone()[0]}")