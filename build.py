from functools import reduce
import itertools
import logging
from xml.dom.minidom import Element
import requests
import pandas
import json
from jsmin import jsmin
import sys
import re
import xml.etree.ElementTree as ET
import regex
import pathlib

TUMBON_RESOURCE_URL='https://stat.bora.dopa.go.th/dload/ccaatt.xlsx'
ZIP_RESOURCE_URL='https://th.wikipedia.org/wiki/รายการรหัสไปรษณีย์ไทย'
WORKING_FILE='_tmp.xlsx'
STRUCTURED_RESULT_FILE='structured_data.json'
FLATTENED_RESULT_FILE='flattened_data.json'
DIST_DIR='dist/'
SRC_DIR='src/'
INDEX_TS_FILE='index.ts'

def fetch_tumbon_resource():
    with requests.get(TUMBON_RESOURCE_URL, stream=True) as resp:
        resp.raise_for_status()
        with open(WORKING_FILE, 'wb') as tmpf:
            for chunk in resp.iter_content(chunk_size = 8192):
                tmpf.write(chunk)


def fetch_zip_resource() -> map:
    # web scraping from wiki
    with requests.get(ZIP_RESOURCE_URL, verify=False) as resp:
        zip_content = resp.text
        zip_match = re.findall(r'(<table class="wikitable sortable".*?</table>)', zip_content, re.S + re.U)
        clean_zip = list(map(lambda z: z.replace("\n", '').replace("<i>", "").replace("</i>", "").replace("<br>", "").replace("<br />", "").replace('<td></td>', '<td>-</td>'), zip_match))
        district_zip = list(map(lambda z: extract_descriptive_zip(z), clean_zip))
    flattened_district_zip = list(itertools.chain(*district_zip))
    # build map
    flattened_district_map = {}
    for zip in flattened_district_zip:
        flattened_district_map[zip['district_name']] = {
            'primary': zip['zips'][0],
            'exceptional': zip['exceptionals']
        }
    return flattened_district_map


def extract_descriptive_zip(zip_table: str) -> list:
    tree = ET.fromstring(zip_table)
    trs = tree.findall('./tbody/tr')
    result = list(map(lambda tr: extract_row_zip(tr), trs[1:]))
    return result


def extract_row_zip(zip_row: Element) -> dict:
    district_name = zip_row[0][0][0].text
    zips = [zip_row[1].text]
    alternate_zip = re.findall(r'(\d{5})', zip_row[2].text)
    if alternate_zip:
        zips.extend(alternate_zip)
    exceptional_zips = extract_exceptional_zips(zip_row[2].text)
    return {
        'district_name': district_name,
        'zips': zips,
        'exceptionals': exceptional_zips
    }


def extract_exceptional_zips(data: str) -> dict:
    # ยกเว้น ตำบลYและตำบลZ ใช้รหัส #####
    # ยกเว้น ตำบลW ตำบลX ตำบลYและตำบลZ ใช้รหัส #####
    matches = regex.findall(r'ยกเว้น(?:\s+(?:ตำบล|แขวง)([^\s+]+))*\s+(?:ตำบล|แขวง)([^\s+]+)และ(?:ตำบล|แขวง)([^\s+]+)\s+ใช้รหัส\s+(\d{5})', data)
    if matches:
        m = list(filter(lambda f: f != '', list(matches[0])))
        zip_code = m[-1]
        subdistricts = m[:-1]
        out = {}
        for subdistrict in subdistricts:
            out[subdistrict] = zip_code
        return out

    # ยกเว้น ตำบลW ตำบลX ตำบลY และตำบลZ ใช้รหัส #####
    matches = regex.findall(r'ยกเว้น(?:\s+(?:ตำบล|แขวง)([^\s+]+))+\s+และ(?:ตำบล|แขวง)([^\s+]+)\s+ใช้รหัส\s+(\d{5})', data)
    if matches:
        m = list(filter(lambda f: f != '', list(matches[0])))
        zip_code = m[-1]
        subdistricts = m[:-1]
        out = {}
        for subdistrict in subdistricts:
            out[subdistrict] = zip_code
        return out

    # ยกเว้น ตำบลZ ใช้รหัส #####
    matches = regex.findall(r'ยกเว้น\s+(?:ตำบล|แขวง)([^\s+]+)\s+ใช้รหัส\s+(\d{5})', data)
    if matches:
        m = list(filter(lambda f: f != '', list(matches[0])))
        zip_code = m[-1]
        subdistricts = m[:-1]
        out = {}
        for subdistrict in subdistricts:
            out[subdistrict] = zip_code
        return out

    # ยกเว้น ตำบลW ตำบลX ตำบลY และตำบลZ ใช้รหัส #####
    matches = regex.findall(r'(?:\s+–\s+(.+))+', data)
    if matches:
        lines = matches[0][0].split("–")
        out = {}
        for line in lines:
            ex_zips = extract_exceptional_zips(f'ยกเว้น {line}')
            if ex_zips is not None:
                out = out | ex_zips
        return out

    return {}


def extract_address(addr: str) -> map:
    province = extract_province(addr)
    district = extract_district(addr)
    subdistrict = extract_subdistrict(addr)
    key = '{}_{}_{}'.format(province, district, subdistrict)
    data = {
        'zip': extract_zip(addr),
        'key': key
    }
    return data


def extract_zip(addr: str) -> str:
    matches = re.match(r'.*(\d{5}).*', addr, re.UNICODE)
    return matches[1]


def extract_province(addr: str) -> map:
    tokens = addr.split(' ')
    tokens.reverse()
    province = tokens[1]
    if province.startswith('จ.'):
        return province[2:]
    return province


def extract_district(addr: str) -> map:
    tokens = addr.split(' ')
    tokens.reverse()
    district = tokens[2]
    if district.startswith('อ.'):
        return district[2:]
    if district.startswith('เขต'):
        return district[3:]
    if district.startswith('อำเภอ'):
        return district[5:]
    return district


def extract_subdistrict(addr: str) -> map:
    tokens = addr.split(' ')
    tokens.reverse()
    subdistrict = ''
    if len(tokens) > 3:
        subdistrict = tokens[3]
    if subdistrict.startswith('ต.'):
        return subdistrict[2:]
    if subdistrict.startswith('แขวง'):
        return subdistrict[4:]
    if subdistrict.startswith('ตำบล'):
        return subdistrict[4:]
    pos = subdistrict.find('ต.')
    if pos != -1:
        return subdistrict[pos + 2:]
    pos = subdistrict.find('แขวง')
    if pos != -1:
        return subdistrict[pos + 4:]
    pos = subdistrict.find('ตำบล')
    if pos != -1:
        return subdistrict[pos + 4:]

    return subdistrict


def parse_tumbon_resource() -> tuple[list, bool, str]:
    xlsx = pandas.ExcelFile(WORKING_FILE)

    logging.info('- Validating resource ...')
    data_header = pandas.read_excel(xlsx, sheet_name=0, header=None, nrows=5)
    if data_header.iat[0, 0].strip() != 'ทำเนียบท้องที่':
        return (None, False, 'unexpected data layout')
    if data_header.iat[4, 0].strip() != 'รหัสจังหวัด 2 หลัก//อำเภอ 4 หลัก//ตำบล 6 หลัก':
        return (None, False, 'unexpected data layout')

    logging.info('- Transform resource ...')
    data_frame = pandas.read_excel(xlsx, sheet_name=0, header=None, skiprows=5, usecols=[0, 1, 3], names = ['Code', 'Name', 'Obsolete'])
    valid_data_frame = data_frame[data_frame.Obsolete == 0].drop(['Obsolete'], axis=1)

    return (valid_data_frame.values.tolist(), True, None)


def get_zip(zip_info: map, subdistrict_name: str) -> str:
    if subdistrict_name in zip_info['exceptional']:
        return zip_info['exceptional'][subdistrict_name]
    return zip_info['primary']


def build_tumbon_resource(data: list, zip_data: map) -> list:
    raw = list(map(lambda d: ['{}'.format(d[0]), d[1]], data))

    subdistricts = list(map(lambda d: {
        'districtKey': d[0][0:4], 
        'subdistrictKey': d[0],
        'subdistrictName': d[1]
    }, filter(lambda d: not d[0].endswith('0000'), raw)))
    subdistricts_map = reduce(lambda acc, d: build_map(acc, d['districtKey'], {
        'name': d['subdistrictName'],
        'code': d['subdistrictKey']
    }), subdistricts, {})

    districts = list(map(lambda d: {
        'code': d[0],
        'provinceKey': d[0][0:2],
        'districtKey': d[0][0:4],
        'districtName': clean_district_name(d[1]),
        'zip': zip_data[clean_district_name(d[1])],
        'subdistricts': subdistricts_map[d[0][0:4]]
    }, filter(lambda d: d[0].endswith('0000') and not d[0].endswith('000000'), raw)))
    districts_map = reduce(lambda acc, d: build_map(acc, d['provinceKey'], {
        'name': d['districtName'],
        'code': d['code'],
        'subdistricts': list(map(lambda s: {
            'name': s['name'],
            'code': s['code'],
            'zip': get_zip(zip_data[d['districtName']], s['name'])
        }, d['subdistricts'])),
    }), districts, {})

    provinces = list(map(lambda d: {
        'name': d[1],
        'code': d[0],
        'districts': districts_map[d[0][0:2]]
    }, filter(lambda d: d[0].endswith('000000'), raw)))

    return provinces


def clean_district_name(name: str) -> str:
    if name.startswith('เขต'):
        return name[3:]
    return name


def build_map(map_value: map, key: str, value: tuple) -> map:
    if key not in map_value:
        map_value[key] = []
    map_value[key].append(value)
    return map_value


def export(data: list, output_file: str, minify: bool):
    with open(output_file, 'w') as tmpf:
        content = json.dumps(data, indent=2, ensure_ascii=False)
        if minify:
            content = jsmin(content)
        tmpf.write(content)


def flat_structured_data(data: list) -> list:
    out = []
    for province in data:
        province_name = province['name']
        for district in province['districts']:
            district_name = district['name']
            for subdistrict in district['subdistricts']:
                out.append({
                    "province": province_name,
                    "district": district_name,
                    "subdistrict": subdistrict['name'],
                    "zip": subdistrict['zip'],
                    "subdistrictCode": subdistrict['code'],
                    "districtCode": district['code'],
                    "provinceCode": province['code']
                })
    return out


def apply_template(input_file: str, output_file: str, data: map, minify: bool):
    with open(input_file, 'r') as tmpf:
        content = tmpf.read()
        for key in data:
            content = content.replace(key, jsmin(json.dumps(data[key], indent=2, ensure_ascii=False)))
        with open(output_file, 'w') as tmpof:
            if minify:
                content = jsmin(content)
            tmpof.write(content)

logging.basicConfig(level=logging.INFO)
if __name__ == '__main__':
    build_prod = False
    if len(sys.argv) > 1 and sys.argv[1] == '-prod':
        logging.info('Building production output ...')
        build_prod = True

    indexts_input = f"{SRC_DIR}{INDEX_TS_FILE}"
    indexts_output = f"{DIST_DIR}{INDEX_TS_FILE}"
    structured_output = f"{DIST_DIR}{STRUCTURED_RESULT_FILE}"
    flattened_output = f"{DIST_DIR}{FLATTENED_RESULT_FILE}"
    if not pathlib.Path(DIST_DIR).exists():
        pathlib.Path(DIST_DIR).mkdir()

    logging.info('Fetch resource ...')
    fetch_tumbon_resource()
    zip_data = fetch_zip_resource()

    logging.info('Parsing resource ...')
    (data, ok, err) = parse_tumbon_resource()
    if not ok:
        logging.error('Unable to parse resource - {}'.format(err))
        exit(1)

    logging.info('Rebuild resource ...')
    structured_data = build_tumbon_resource(data, zip_data)
    flattened_data = flat_structured_data(structured_data)
    
    logging.info('Writing structured result ...')
    export(structured_data, structured_output, build_prod)

    logging.info('Writing flattened result ...')
    export(flattened_data, flattened_output, build_prod)

    logging.info('Writing node package ...')
    apply_template(indexts_input, indexts_output, {
        '[/* ADDRESSES */]': flattened_data
    }, build_prod)