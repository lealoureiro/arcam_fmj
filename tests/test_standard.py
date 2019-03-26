"""Standard tests for component"""
import asyncio
from arcam.fmj import _read_packet, ResponsePacket, InvalidPacket, _write_packet, CommandPacket
import pytest
from unittest.mock import MagicMock, call

async def test_reader_valid(event_loop):
    reader = asyncio.StreamReader(loop=event_loop)
    reader.feed_data(b'\x21\x01\x08\x00\x02\x10\x10\x0D')
    reader.feed_eof()
    packet = await _read_packet(reader)
    assert packet == ResponsePacket(1, 8 , 0, b'\x10\x10')


async def test_reader_invalid_data(event_loop):
    reader = asyncio.StreamReader(loop=event_loop)
    reader.feed_data(b'\x21\x01\x08\x00\x02\x10\x0D')
    reader.feed_eof()
    with pytest.raises(InvalidPacket):
        await _read_packet(reader)


async def test_reader_short(event_loop):
    reader = asyncio.StreamReader(loop=event_loop)
    reader.feed_data(b'\x21\x10\x0D')
    reader.feed_eof()
    with pytest.raises(InvalidPacket):
        await _read_packet(reader)


async def test_writer_valid(event_loop):
    writer = MagicMock()
    writer.write.return_value = None
    writer.drain.return_value = asyncio.Future()
    writer.drain.return_value.set_result(None)
    await _write_packet(writer, CommandPacket(1, 8, b'\x10\x10'))
    writer.write.assert_has_calls([
        call(b'\x21\x01\x08\x02\x10\x10\x0D'),
    ])