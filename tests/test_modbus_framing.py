"""Tests for the Modbus TCP framing option (standard Modbus TCP or RTU over TCP)."""

# ruff: noqa: PT009

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pymodbus import FramerType

from custom_components.systemair.api import SystemairModbusClient
from custom_components.systemair.const import FRAMING_RTU_OVER_TCP, FRAMING_TCP


class ModbusFramingTest(unittest.IsolatedAsyncioTestCase):
    """Verify the TCP client is created with the framer matching the configured framing."""

    async def _connect_and_get_framer(self, client: SystemairModbusClient) -> FramerType:
        transport = MagicMock()
        transport.connected = False
        transport.connect = AsyncMock(return_value=True)
        with patch("custom_components.systemair.api.AsyncModbusTcpClient", return_value=transport) as tcp_client:
            await client._ensure_connected()  # noqa: SLF001
        return tcp_client.call_args.kwargs["framer"]

    async def test_default_framing_is_modbus_tcp(self) -> None:
        """Existing config entries without a framing setting keep using standard Modbus TCP."""
        client = SystemairModbusClient(host="127.0.0.1", port=502, slave_id=1)
        self.assertEqual(await self._connect_and_get_framer(client), FramerType.SOCKET)

    async def test_tcp_framing(self) -> None:
        """Explicit Modbus TCP framing uses the socket (MBAP) framer."""
        client = SystemairModbusClient(host="127.0.0.1", port=502, slave_id=1, framing=FRAMING_TCP)
        self.assertEqual(await self._connect_and_get_framer(client), FramerType.SOCKET)

    async def test_rtu_over_tcp_framing(self) -> None:
        """RTU over TCP sends raw RTU frames over the TCP socket."""
        client = SystemairModbusClient(host="127.0.0.1", port=8888, slave_id=1, framing=FRAMING_RTU_OVER_TCP)
        self.assertEqual(await self._connect_and_get_framer(client), FramerType.RTU)


if __name__ == "__main__":
    unittest.main()
