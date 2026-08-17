import os
from pathlib import Path
from tools.file_tools import create_file, read_file_content, list_directory


def test_create_and_read_file(tmp_path):
    test_file = tmp_path / "sample.py"
    content = "print('Hello Captain')"

    res = create_file(str(test_file), content)
    assert res["status"] == "success"
    assert test_file.exists()

    read_res = read_file_content(str(test_file))
    assert read_res["status"] == "success"
    assert read_res["content"] == content


def test_list_directory(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    res = list_directory(str(tmp_path))
    assert res["status"] == "success"
    assert len(res["items"]) >= 1
