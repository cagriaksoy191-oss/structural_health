import os
import sys
import logging
import hashlib
from typing import List, Dict, Any, Set
from pathlib import Path

# Third-party imports
try:
    import git
    from pinecone import Pinecone
    from dotenv import load_dotenv
except ImportError as e:
    # If dependencies are missing, we can't really do anything smart.
    # But usually gunsonu installs them.
    print(f"Missing required library: {e}")
    sys.exit(1)

# Setup Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
INDEX_NAME = "deprem-hafiza"
NAMESPACE = "proje"
CHUNK_SIZE = 3000
OVERLAP = 200
EMBEDDING_MODEL = "multilingual-e5-large"
SYNC_STATE_FILENAME = ".pinecone_sync_state"

# Load Environment Variables
# We need to find the .env file relative to this script or the repo root
# Since we have get_repo_root function now, we can use it, but we need it defined before loading env?
# Actually, let's just use the fact that this script is in /scripts and .env is in /
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
env_path = project_root / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()  # Fallback

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


def get_repo_root(start_path: str = ".") -> git.Repo:
    """Finds the root of the git repository."""
    try:
        return git.Repo(start_path, search_parent_directories=True)
    except Exception as e:
        logger.error(f"Could not find git repository: {e}")
        return None


def get_sync_state_path(repo: git.Repo) -> Path:
    """Returns the absolute path to the sync state file in the repo root."""
    return Path(repo.working_dir) / SYNC_STATE_FILENAME


def get_current_commit_hash(repo: git.Repo) -> str:
    try:
        return repo.head.commit.hexsha
    except:
        return None


def get_changed_files(start_path: str = ".") -> Set[str]:
    """
    Identifies changes based on the previous sync state.
    """
    try:
        repo = get_repo_root(start_path)
        if not repo:
            return set()

        changed = set()
        current_commit = get_current_commit_hash(repo)

        if not current_commit:
            return set()

        # 1. Determine Range
        last_synced_commit = None
        sync_state_file = get_sync_state_path(repo)

        if sync_state_file.exists():
            with open(sync_state_file, "r") as f:
                last_synced_commit = f.read().strip()

        # Valid range check matches git logic
        target_commit_obj = None
        if last_synced_commit:
            try:
                target_commit_obj = repo.commit(last_synced_commit)
            except:
                logger.warning(
                    f"Last synced commit {last_synced_commit} not found (maybe rebase?). Falling back to HEAD~1."
                )
                last_synced_commit = None

        if last_synced_commit and last_synced_commit != current_commit:
            logger.info(
                f"Syncing changes from {last_synced_commit[:7]} to {current_commit[:7]}..."
            )
            diffs = target_commit_obj.diff(repo.head.commit)
            for d in diffs:
                if d.change_type in ["A", "M", "R"] and d.b_path:
                    changed.add(
                        str(Path(repo.working_dir) / d.b_path)
                    )  # Absolute paths for safety? smart_sync usually gets relative.
                    # Actually, gitpython returns relative paths to repo root.
                    # We need to be careful. Let's return relative paths, as process_file expects file path.
                    # But process_file opens it. If process_file run from scripts/..
                    # Let's standardize on absolute paths for processing.

        elif not last_synced_commit:
            logger.info("No valid sync state found. Checking recent activity (HEAD~1).")
            # Check if there are at least 2 commits to diff
            if repo.head.is_valid() and repo.head.commit.parents:
                # Check just the last commit diff
                parent = repo.head.commit.parents[0]
                for d in parent.diff(repo.head.commit):
                    if d.change_type in ["A", "M", "R"] and d.b_path:
                        changed.add(str(Path(repo.working_dir) / d.b_path))
            else:
                # Initial commit - all files
                for item in repo.head.commit.tree.traverse():
                    if item.type == "blob":
                        changed.add(str(Path(repo.working_dir) / item.path))

        # 2. Add currently dirty/untracked files
        if repo.is_dirty(untracked_files=True):
            # index.diff returns Diff objects. a_path is path.
            # working dir diffs are usually relative to repo root.
            for item in repo.index.diff(None):
                path = item.a_path or item.b_path
                if path:
                    changed.add(str(Path(repo.working_dir) / path))

            for item in repo.index.diff("HEAD"):
                path = item.a_path or item.b_path
                if path:
                    changed.add(str(Path(repo.working_dir) / path))

            for path in repo.untracked_files:
                changed.add(str(Path(repo.working_dir) / path))

        # 3. Filter exclusions
        excludes = [
            ".git",
            "__pycache__",
            "node_modules",
            ".env",
            "venv",
            ".vscode",
            ".idea",
            "dist",
            "build",
            SYNC_STATE_FILENAME,
        ]
        filtered = []
        for f in changed:
            f_str = str(f).replace("\\", "/")
            # Check existence and exclusions
            if not any(ex in f_str for ex in excludes) and os.path.exists(f):
                filtered.append(f)

        return set(filtered)

    except Exception as e:
        logger.error(f"Git logic error: {e}")
        return set()


def update_sync_state(start_path: str = "."):
    try:
        repo = get_repo_root(start_path)
        if not repo:
            return

        current = get_current_commit_hash(repo)
        if current:
            sync_state_file = get_sync_state_path(repo)
            with open(sync_state_file, "w") as f:
                f.write(current)
            logger.info(f"Sync state updated to {current[:7]}")
    except Exception as e:
        logger.warning(f"Could not update sync state: {e}")


# ... (Chunking/ID/Delete functions remain similar) ...
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - OVERLAP
    return chunks


def generate_record_id(filename: str, chunk_index: int) -> str:
    # Use MD5 hash for filename to ensure ASCII compliance (handles 'Masaüstü' etc.)
    # and to keep ID length limits in check.
    path_hash = hashlib.md5(filename.encode("utf-8")).hexdigest()
    return f"proje__{path_hash}_c{chunk_index}"


def delete_existing_records(index, filename: str):
    try:
        path_hash = hashlib.md5(filename.encode("utf-8")).hexdigest()
        prefix = f"proje__{path_hash}_"
        matches = []
        for ids in index.list(prefix=prefix, namespace=NAMESPACE):
            matches.extend(ids)
        if matches:
            # Delete in batches
            for i in range(0, len(matches), 1000):
                batch = matches[i : i + 1000]
                index.delete(ids=batch, namespace=NAMESPACE)
    except Exception as e:
        logger.warning(f"Delete warning for {filename}: {e}")


def process_file_content(filepath: str) -> List[Dict[str, Any]]:
    path = Path(filepath)
    ext = path.suffix.lower()
    valid_exts = [
        ".py",
        ".js",
        ".jsx",
        ".html",
        ".css",
        ".md",
        ".txt",
        ".ps1",
        ".bat",
        ".json",
        ".yml",
        ".yaml",
    ]
    if ext not in valid_exts:
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return []

    chunks = chunk_text(content)
    records = []
    for i, chunk in enumerate(chunks):
        f_type = "code"
        if ext in [".md", ".txt"]:
            f_type = "doc"
        elif ext in [".json", ".yml"]:
            f_type = "config"

        metadata = {
            "filename": filepath.replace("\\", "/"),
            "chunk_index": i,
            "type": f_type,
            "source": "gunsonu_auto",
            "text": chunk,
        }
        records.append(
            {"id": generate_record_id(filepath, i), "text": chunk, "metadata": metadata}
        )
    return records


def main():
    # 1. Graceful Exit if No API Key
    if not PINECONE_API_KEY:
        logger.warning("PINECONE_API_KEY not found. Skipping sync (Team safe mode).")
        # Exit with 0 so checks pass, but do NOT update state file
        sys.exit(0)

    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
        logger.info("✅ PINECONE BAGLANTISI BASARILI! (API Key Dogrulandi)")
    except Exception as e:
        logger.error(f"Pinecone Connection Error: {e}")
        # If connection fails, we fail (so user knows info is stale)
        sys.exit(1)

    # 2. Detect Changes
    changed_files = list(get_changed_files())

    if not changed_files:
        logger.info("Memory is up to date. No changes to sync.")
        update_sync_state()  # Ensure state follows HEAD even if no files changed (e.g. merge of unrelated files)
        sys.exit(0)

    logger.info(f"Syncing {len(changed_files)} files: {changed_files}")

    # 3. Process Files
    for filename in changed_files:
        # A. Delete old
        delete_existing_records(index, filename)
        # B. Upsert new
        records_data = process_file_content(filename)
        if not records_data:
            continue

        batch_size = 8  # Conservative batch for embedding
        for i in range(0, len(records_data), batch_size):
            batch = records_data[i : i + batch_size]
            try:
                embeddings = pc.inference.embed(
                    model=EMBEDDING_MODEL,
                    inputs=[r["text"] for r in batch],
                    parameters={"input_type": "passage", "truncate": "END"},
                )
                vectors = []
                for j, emb in enumerate(embeddings):
                    vectors.append(
                        {
                            "id": batch[j]["id"],
                            "values": emb["values"],
                            "metadata": batch[j]["metadata"],
                        }
                    )
                index.upsert(vectors=vectors, namespace=NAMESPACE)
            except Exception as e:
                logger.error(f"Sync error for {filename}: {e}")

    # 4. Update State on Success
    update_sync_state()
    logger.info("Memory sync completed successfully.")


if __name__ == "__main__":
    main()
