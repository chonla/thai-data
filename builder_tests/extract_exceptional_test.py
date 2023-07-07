from builder.build import extract_exceptional_zips


def test_extract_empty_exceptionals():
    data = ""

    result = extract_exceptional_zips(data)

    assert result == {}


def test_extract_data_with_post_office_noise():
    data = "(ไปรษณีย์นครนายก)"

    result = extract_exceptional_zips(data)

    assert result == {}


def test_extract_single_line_multiple_exceptional_zips_case_1():
    # 2 districts joined with และ
    data = "ยกเว้น ตำบลอออและตำบลขขข ใช้รหัส 12345"

    result = extract_exceptional_zips(data)

    assert result == {"อออ": "12345", "ขขข": "12345"}


def test_extract_single_line_multiple_exceptional_zips_case_2():
    # 3 or more districts joined with spaces and และ
    data = "ยกเว้น ตำบลอออ ตำบลขขข ตำบลจจจและตำบลกกก ใช้รหัส 12345"

    result = extract_exceptional_zips(data)

    assert result == {"อออ": "12345", "ขขข": "12345", "จจจ": "12345", "กกก": "12345"}


def test_extract_single_line_multiple_exceptional_zips_case_3():
    # 3 or more districts joined with spaces and และ preceded with space
    data = "ยกเว้น ตำบลอออ ตำบลขขข ตำบลจจจ และตำบลกกก ใช้รหัส 12345"

    result = extract_exceptional_zips(data)

    assert result == {"อออ": "12345", "ขขข": "12345", "จจจ": "12345", "กกก": "12345"}


def test_extract_single_line_single_exceptional_zip():
    # 1 district
    data = "ยกเว้น ตำบลลลล ใช้รหัส 12345"

    result = extract_exceptional_zips(data)

    assert result == {"ลลล": "12345"}


def test_extract_single_line_data_with_post_office_noise():
    data = "ยกเว้น ตำบลลลล ใช้รหัส 12345 (ไปรษณีย์นครนายก)"

    result = extract_exceptional_zips(data)

    assert result == {"ลลล": "12345"}


def test_extract_multiple_lines_exceptional_zips():
    # 3 or more districts joined with spaces and และ preceded with space
    data = "ยกเว้น  - ตำบลอออ ตำบลขขข ตำบลจจจ และตำบลกกก ใช้รหัส 12345  - ตำบลยยย ตำบลฑฑฑ และตำบลฤฤฤ ใช้รหัส 23456    - ตำบลปปปและตำบลสสส ใช้รหัส 98765  - ตำบลฮฮฮ ใช้รหัส 76156"  # noqa: E501

    result = extract_exceptional_zips(data)

    assert result == {
        "อออ": "12345",
        "ขขข": "12345",
        "จจจ": "12345",
        "กกก": "12345",
        "ยยย": "23456",
        "ฑฑฑ": "23456",
        "ฤฤฤ": "23456",
        "ปปป": "98765",
        "สสส": "98765",
        "ฮฮฮ": "76156",
    }


def test_extract_complex_exceptional_zips():
    data = "(ไปรษณีย์คลองจั่น) ยกเว้น แขวงนวลจันทร์ แขวงนวมินทร์ เฉพาะซอยนวมินทร์ 103-111 และแขวงคลองกุ่ม เฉพาะซอยนวมินทร์ 64-68, 74 ใช้รหัส 10230 (ไปรษณีย์จรเข้บัว)"  # noqa: E501

    result = extract_exceptional_zips(data)

    assert result == {"นวลจันทร์": "10230", "นวมินทร์": "10230", "คลองกุ่ม": "10230"}


def test_extract_nondistrict_exceptional_zips():
    data = "ยกเว้น ศูนย์ไปรษณีย์หลักสี่ ใช้รหัส 10010 (ศูนย์ไปรษณีย์หลักสี่)"

    result = extract_exceptional_zips(data)

    assert result == {}


def test_extract_complex_exceptional_zips_case_2():
    data = "(ไปรษณีย์ขอนแก่น) ยกเว้น  − ตำบลท่าพระและตำบลดอนหัน ใช้รหัส 40260 (ไปรษณีย์ท่าพระขอนแก่น)  − ภายในมหาวิทยาลัยขอนแก่น ใช้รหัส 40002 (ไปรษณีย์มหาวิทยาลัยขอนแก่น)  − ศูนย์ไปรษณีย์ขอนแก่น ใช้รหัส 40010 (ศูนย์ไปรษณีย์ขอนแก่น)"  # noqa: E501

    result = extract_exceptional_zips(data)

    assert result == {"ท่าพระ": "40260", "ดอนหัน": "40260"}
