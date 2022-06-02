from functools import reduce
import logging
import requests
import pandas
import json
from jsmin import jsmin
import sys

TUMBON_RESOURCE_URL='https://stat.bora.dopa.go.th/dload/ccaatt.xlsx'
WORKING_FILE='_tmp.xlsx'
RESULT_FILE='structured_data.json'

def fetch_tumbon_resource():
    with requests.get(TUMBON_RESOURCE_URL, stream=True) as resp:
        resp.raise_for_status()
        with open(WORKING_FILE, 'wb') as tmpf:
            for chunk in resp.iter_content(chunk_size = 8192):
                tmpf.write(chunk)

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

def build_tumbon_resource(data: list) -> list:
    raw = list(map(lambda d: ['{}'.format(d[0]), d[1]], data))

    subdistricts = list(map(lambda d: {
        'districtKey': d[0][0:4], 
        'subdistrictKey': d[0],
        'subdistrictName': d[1]
    }, filter(lambda d: not d[0].endswith('0000'), raw)))
    subdistricts_map = reduce(lambda acc, d: build_map(acc, d['districtKey'], {
        'subdistrictKey': d['subdistrictKey'],
        'subdistrictName': d['subdistrictName'],
    }), subdistricts, {})

    districts = list(map(lambda d: {
        'provinceKey': d[0][0:2],
        'districtKey': d[0][0:4],
        'districtName': d[1],
        'subdistricts': subdistricts_map[d[0][0:4]]
    }, filter(lambda d: d[0].endswith('0000') and not d[0].endswith('000000'), raw)))
    districts_map = reduce(lambda acc, d: build_map(acc, d['provinceKey'], {
        'districtKey': d['districtKey'],
        'districtName': d['districtName'],
        'subdistricts': d['subdistricts']
    }), districts, {})

    provinces = list(map(lambda d: {
        'provinceKey': d[0][0:2],
        'provinceName': d[1],
        'districts': districts_map[d[0][0:2]]
    }, filter(lambda d: d[0].endswith('000000'), raw)))

    return provinces

def build_map(map_value: map, key: str, value: tuple) -> map:
    if key not in map_value:
        map_value[key] = []
    map_value[key].append(value)
    return map_value

def export(data: list, minified: bool):
    with open(RESULT_FILE, 'w') as tmpf:
        content = json.dumps(data, indent=2, ensure_ascii=False)
        if minified:
            content = jsmin(content)
        tmpf.write(content)


logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    buildProd = False
    if len(sys.argv) > 1 and sys.argv[1] == 'prod':
        buildProd = True

    logging.info('Fetch resource ...')
    # fetch_tumbon_resource()

    logging.info('Parsing resource ...')
    (data, ok, err) = parse_tumbon_resource()
    if not ok:
        logging.error('Unable to parse resource - {}'.format(err))
        exit(1)

    logging.info('Rebuild resource ...')
    structured_data = build_tumbon_resource(data)
    
    logging.info('Writing structured result ...')
    export(structured_data, buildProd)