from __future__ import annotations
import tempfile
import os
import pytest
from jwbuddy.tools.document import DocumentTool


@pytest.mark.asyncio
async def test_document_txt():
    """Test parsing a plain text file"""
    tool = DocumentTool(upload_dir="/tmp/jwb_test")
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write("Hello JWBuddy")
    f.close()
    result = await tool.execute(file_path=f.name)
    os.unlink(f.name)
    assert result.success
    assert "Hello JWBuddy" in result.data["content"]


@pytest.mark.asyncio
async def test_document_file_not_found():
    """Test handling of non-existent file"""
    tool = DocumentTool(upload_dir="/tmp/jwb_test")
    result = await tool.execute(file_path="/tmp/nonexistent_file_xyz.txt")
    assert not result.success
    assert "文件不存在" in result.error


@pytest.mark.asyncio
async def test_document_unsupported_format():
    """Test handling of unsupported file format"""
    tool = DocumentTool(upload_dir="/tmp/jwb_test")
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False)
    f.write("some content")
    f.close()
    result = await tool.execute(file_path=f.name)
    os.unlink(f.name)
    assert not result.success
    assert "不支持的文件格式" in result.error


@pytest.mark.asyncio
async def test_document_image():
    """Test parsing an image file (should indicate OCR needed)"""
    tool = DocumentTool(upload_dir="/tmp/jwb_test")
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".png", delete=False)
    f.write("fake png content")
    f.close()
    result = await tool.execute(file_path=f.name)
    os.unlink(f.name)
    assert result.success
    assert "需要 OCR 服务" in result.data["content"]
    assert result.data["filename"] == os.path.basename(f.name)
