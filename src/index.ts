import _ from 'lodash';

const addresses = [/* ADDRESSES */];

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
    constructor() {}

    findByZip(zipCode: string): ThaiAddrRecord[] {
        return _.filter(addresses, (addr: ThaiAddrRecord) => addr.zip === zipCode);
    }

    findBySubdistrictCode(code): ThaiAddrRecord {
        return _.head(_.filter(addresses, (addr: ThaiAddrRecord) => addr.subdistrictCode === code));
    }

    zips(): string[] {
        return _.sortBy(_.uniq(_.map(addresses, (addr) => addr.zip)));
    }

    provinces(): string[] {
        return _.sortBy(_.uniqBy(_.map(addresses, (addr) => ({
            name: addr.province,
            code: addr.provinceCode
        })), 'code'), 'name');
    }

    districts(code: string): ThaiAddrMiniRecord[] {
        return _.map(_.sortBy(_.uniqBy(_.filter(addresses, (addr) => addr.provinceCode === code), 'districtCode'), 'district'), (addr) => ({
            name: addr.district,
            code: addr.districtCode
        }));
    }

    subdistricts(code: string): ThaiAddrMiniRecord[] {
        return _.map(_.sortBy(_.uniqBy(_.filter(addresses, (addr) => addr.districtCode === code), 'subdistrictCode'), 'subdistrict'), (addr) => ({
            name: addr.subdistrict,
            code: addr.subdistrictCode
        }));
    }
};

const ThaiAddr: ThaiAddrClass = new ThaiAddrClass();

export default ThaiAddr;
