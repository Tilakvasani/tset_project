#!/usr/bin/env python3
"""Test ChromaDB initialization after config fix."""

import sys
from pathlib import Path

# Test 1: Import config
try:
    from backend.core.config import settings
    print(f"✅ Config loaded")
    print(f"   CHROMA_PATH={settings.CHROMA_PATH}")
except Exception as e:
    print(f"❌ Config error: {e}")
    sys.exit(1)

# Test 2: Check path  
try:
    path = Path(settings.CHROMA_PATH)
    print(f"✅ Path resolved: {path}")
    print(f"   Exists: {path.exists()}")
    print(f"   Is dir: {path.is_dir()}")
except Exception as e:
    print(f"❌ Path error: {e}")
    sys.exit(1)

# Test 3: Import ChromaDB service
try:
    from backend.rag.ingest_service import _get_collection
    col = _get_collection()
    print(f"✅ ChromaDB collection ready: {col.name}")
except Exception as e:
    print(f"❌ ChromaDB error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All ChromaDB initialization tests passed!")
