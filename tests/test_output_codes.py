from fungtion.output_codes import format_output_code


def test_format_output_code_uses_four_digits_for_small_runs():
    assert format_output_code(1, 12) == "0001"
    assert format_output_code(9999, 9999) == "9999"


def test_format_output_code_expands_for_large_runs():
    assert format_output_code(1, 10000) == "00001"
    assert format_output_code(10000, 10000) == "10000"
    assert format_output_code(1, 100000) == "000001"
