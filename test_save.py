
import asyncio
from backend.services.redis_service import cache
from backend.agents.agent_graph import _save_history, _load_history

async def test_save():
    await cache.connect()
    session_id = "test_session_123"
    print(f"Testing session: {session_id}")
    
    # 1. Clear existing
    await cache.delete(f"docforge:agent:history:{session_id}")
    
    # 2. Save a turn
    history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]
    await _save_history(session_id, history)
    print("Saved 1 turn.")
    
    # 3. Load back
    loaded = await _load_history(session_id)
    print(f"Loaded: {loaded}")
    
    if len(loaded) == 2:
        print("✅ Save/Load successful!")
    else:
        print("❌ Save/Load failed!")
    
    await cache.disconnect()

if __name__ == "__main__":
    asyncio.run(test_save())
