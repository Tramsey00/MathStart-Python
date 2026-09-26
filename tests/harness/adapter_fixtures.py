"""Deterministic adapter fixtures for runner boundaries; no sleep or network."""
from __future__ import annotations

from unittest.mock import Mock

from harness.adapters.fake import FakeAdapter
from harness.contracts.adapter import AdapterIdentity


class UnsupportedProtocolAdapter(FakeAdapter):
    @property
    def identity(self) -> AdapterIdentity:
        return AdapterIdentity(name="unsupported-fixture", version="1",
                               protocol_version="adapter-protocol-unknown")


class ScriptedAdapter(FakeAdapter):
    def __init__(self, events, on_return=lambda step: None):
        super().__init__()
        self.events = iter(events)
        self.step = 0
        self.on_return = on_return
        self.start = Mock(side_effect=self._return_event)
        self.continue_with_tool_result = Mock(side_effect=self._return_event)
        self.continue_after_message = Mock(side_effect=self._return_event)

    def _return_event(self, request):
        self.step += 1
        event = next(self.events)
        self.on_return(self.step)
        return event
