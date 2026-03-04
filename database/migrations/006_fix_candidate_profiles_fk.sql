BEGIN;

ALTER TABLE candidate_profiles
DROP CONSTRAINT IF EXISTS candidate_profiles_candidate_id_fkey;

ALTER TABLE candidate_profiles
ADD CONSTRAINT candidate_profiles_candidate_id_fkey
FOREIGN KEY (candidate_id)
REFERENCES candidates(id)
ON DELETE CASCADE;

COMMIT;
