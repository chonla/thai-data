import _ from 'lodash';

const addresses: ThaiAddrRecord[] = [/* ADDRESSES */];

export interface ThaiAddrRecord {
    province: string;
    district: string;
    subdistrict: string;
    zip: string;
    subdistrictCode: string;
    districtCode: string;
    provinceCode: string;
}

export interface ThaiAddrMiniRecord {
    name: string;
    code: string;
}

class ThaiAddrClass {
    _dataVersion: string = /* ADDRESSES_VERSION */;

    constructor() { }

    findByZip(zipCode: string): ThaiAddrRecord[] {
        return _.filter(addresses, (addr: ThaiAddrRecord): boolean => addr.zip === zipCode);
    }

    findBySubdistrictCode(code: string): ThaiAddrRecord | undefined {
        return _.head(_.filter(addresses, (addr: ThaiAddrRecord): boolean => addr.subdistrictCode === code));
    }

    zips(): string[] {
        return _.sortBy(_.uniq(_.map(addresses, (addr: ThaiAddrRecord): string => addr.zip)));
    }

    provinces(): ThaiAddrMiniRecord[] {
        return _.sortBy(_.uniqBy(_.map(addresses, (addr: ThaiAddrRecord): ThaiAddrMiniRecord => ({
            name: addr.province,
            code: addr.provinceCode
        })), 'code'), 'name');
    }

    districts(code: string): ThaiAddrMiniRecord[] {
        return _.map(_.sortBy(_.uniqBy(_.filter(addresses, (addr: ThaiAddrRecord): boolean => addr.provinceCode === code), 'districtCode'), 'district'), (addr: ThaiAddrRecord): ThaiAddrMiniRecord => ({
            name: addr.district,
            code: addr.districtCode
        }));
    }

    subdistricts(code: string): ThaiAddrMiniRecord[] {
        return _.map(_.sortBy(_.uniqBy(_.filter(addresses, (addr: ThaiAddrRecord): boolean => addr.districtCode === code), 'subdistrictCode'), 'subdistrict'), (addr: ThaiAddrRecord): ThaiAddrMiniRecord => ({
            name: addr.subdistrict,
            code: addr.subdistrictCode
        }));
    }

    dataVersion(): string {
        return this._dataVersion;
    }
};

const ThaiAddr: ThaiAddrClass = new ThaiAddrClass();

export default ThaiAddr;
