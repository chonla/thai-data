from builder.build import extract_district_name


def test_extract_tumbon():
    data = "ตำบลหัวเสือ"

    result = extract_district_name(data)

    assert result == "หัวเสือ"


def test_extract_district():
    data = "แขวงบ้านบาตร"

    result = extract_district_name(data)

    assert result == "บ้านบาตร"


def test_extract_nondistrict():
    data = "ไปรษณีย์ไทย"

    result = extract_district_name(data)

    assert result == ""
