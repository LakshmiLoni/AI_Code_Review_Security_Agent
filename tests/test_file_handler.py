from config import settings
from submission.file_handler import check_text, read_uploaded_file
from submission.pipeline import submit_pasted_code, submit_uploaded_file


def test_read_valid_python_file():
    result = read_uploaded_file("a.py", b"print('hi')\n")
    assert result.ok and "print" in result.text


def test_utf8_bom_is_accepted():
    assert read_uploaded_file("a.py", b"\xef\xbb\xbfx = 1\n").ok


def test_unsupported_extension():
    result = read_uploaded_file("notes.txt", b"hello")
    assert not result.ok and "Unsupported file type" in result.error


def test_missing_extension():
    assert not read_uploaded_file("Makefile", b"all:").ok


def test_empty_file():
    assert not read_uploaded_file("a.py", b"").ok
    assert not read_uploaded_file("a.py", b"   \n").ok


def test_oversized_file():
    data = b"x = 1\n" * (settings.MAX_FILE_SIZE_BYTES // 6 + 10)
    result = read_uploaded_file("big.py", data)
    assert not result.ok and "exceeds" in result.error


def test_encoding_error():
    result = read_uploaded_file("a.py", b"x = '\xff\xfe\xfa'")
    assert not result.ok and "UTF-8" in result.error


def test_binary_file_rejected():
    assert not read_uploaded_file("a.py", b"\x00\x01\x02").ok


def test_empty_paste():
    assert not check_text("").ok
    assert not check_text(None).ok


def test_pipeline_paste_python():
    sub = submit_pasted_code("def f():\n    return 1\n")
    assert sub.accepted and sub.language == "python"
    assert sub.validation.status == "valid"


def test_pipeline_ambiguous_paste_asks_for_clearer_sample():
    sub = submit_pasted_code("hello there")
    assert not sub.accepted
    assert any("clearer" in e for e in sub.errors)
    assert sub.validation.status == "skipped"


def test_pipeline_upload_mismatch():
    java = "public class A {\n    public static void main(String[] a) {\n        System.out.println(1);\n    }\n}\n"
    sub = submit_uploaded_file("wrong.py", java.encode())
    assert sub.language is None and sub.errors


def test_pipeline_upload_invalid_python():
    sub = submit_uploaded_file("bad.py", b"def f(:\n    pass\n")
    assert sub.language == "python"
    assert sub.validation.status == "invalid"


def test_submitted_code_serialises():
    assert submit_pasted_code("def f():\n    pass\n").to_dict()["language"] == "python"
