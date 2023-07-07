from builder.build import extract_subdistrict_name


def test_extract_tumbon():
    data = "ตำบลหัวเสือ"

    result = extract_subdistrict_name(data)

    assert result == "หัวเสือ"


def test_extract_subdistrict():
    data = "แขวงบ้านบาตร"

    result = extract_subdistrict_name(data)

    assert result == "บ้านบาตร"


def test_extract_nonsubdistrict():
    data = "ไปรษณีย์ไทย"

    result = extract_subdistrict_name(data)

    assert result == ""
