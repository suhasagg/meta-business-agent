import pytest
from meta_business.memory.store import MemoryStore
from meta_business.core.models import MemoryRecord
@pytest.mark.asyncio
async def test_tenant_isolation():
 s=MemoryStore();await s.put(MemoryRecord(layer="episodic",tenant_id="a",key="shoe",text="likes running shoe"))
 assert await s.search("a","shoe",layers=["episodic"])
 assert not await s.search("b","shoe",layers=["episodic"])
