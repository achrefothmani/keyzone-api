import pytest
from app.utils.reference import format_reference, generate_reference

def test_format_reference():
    assert format_reference(1000) == "P1000"
    assert format_reference(9999) == "P9999"
    assert format_reference(10000) == "P10000"

def test_generate_reference():
    ref = generate_reference()
    assert isinstance(ref, str)
    assert ref.startswith("P-")

def test_format_reference_validation():
    with pytest.raises(ValueError, match="Number must be a positive integer"):
        format_reference(0)
    with pytest.raises(ValueError, match="Number must be a positive integer"):
        format_reference(-1)
