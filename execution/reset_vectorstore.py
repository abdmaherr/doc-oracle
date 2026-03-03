"""
CLI script: Reset (delete) a vector store collection.

Usage:
    python -m execution.reset_vectorstore <collection_name>
    python -m execution.reset_vectorstore --all  # Delete all collections
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.vectorstore import VectorStore


def main() -> None:
    vs = VectorStore()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m execution.reset_vectorstore <collection_name>")
        print("  python -m execution.reset_vectorstore --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        collections = vs.list_collections()
        if not collections:
            print("No collections to delete.")
            return
        for name in collections:
            vs.delete_collection(name)
            print(f"Deleted: {name}")
        print(f"Deleted {len(collections)} collection(s).")
    else:
        name = sys.argv[1]
        if not vs.collection_exists(name):
            print(f"Collection '{name}' not found.")
            sys.exit(1)
        vs.delete_collection(name)
        print(f"Deleted: {name}")


if __name__ == "__main__":
    main()
