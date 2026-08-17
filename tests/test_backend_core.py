import pytest
import asyncio
from src.backend.core.event_bus import AsyncEventBus, Event
from src.backend.core.permission_manager import PermissionManager, Permission
from src.backend.core.tool_manager import MCPToolManager
from src.backend.core.task_queue import BackgroundTaskQueue


def test_event_bus_pub_sub():
    async def _test():
        bus = AsyncEventBus()
        received_events = []

        async def sample_handler(event: Event):
            received_events.append(event)

        bus.subscribe("TestEvent", sample_handler)
        await bus.publish("TestEvent", "UnitTest", {"key": "value"})

        assert len(received_events) == 1
        assert received_events[0].event_type == "TestEvent"
        assert received_events[0].payload["key"] == "value"

    asyncio.run(_test())


def test_permission_manager():
    pm = PermissionManager()
    assert pm.check_permission(Permission.FS_READ) is True
    
    pm.revoke_permission(Permission.FS_READ)
    assert pm.check_permission(Permission.FS_READ) is False
    
    pm.grant_permission(Permission.FS_READ)
    assert pm.check_permission(Permission.FS_READ) is True


def test_mcp_tool_manager():
    async def _test():
        tm = MCPToolManager()

        def dummy_tool(x: int):
            return x * 2

        tm.register_tool("dummy", "Dummy tool", [Permission.FS_READ], dummy_tool)

        res = await tm.execute_tool("dummy", x=5)
        assert res["status"] == "success"
        assert res["result"] == 10

    asyncio.run(_test())


def test_background_task_queue():
    async def _test():
        tq = BackgroundTaskQueue()

        async def sample_coro(val: int):
            await asyncio.sleep(0.1)
            return val + 100

        task_id = tq.submit_task("SampleTask", sample_coro, val=50)
        assert task_id is not None

        status = tq.get_task_status(task_id)
        assert status.status in ["PENDING", "RUNNING"]

        await asyncio.sleep(0.2)
        final_status = tq.get_task_status(task_id)
        assert final_status.status == "COMPLETED"
        assert final_status.result == 150

    asyncio.run(_test())
