import _ from 'lodash';

const addresses = [/* ADDRESSES */];

class ThaiAddr {
    constructor() {}

    findByZip(zipCode) {
        return _.filter(addresses, (addr) => addr.zip === zipCode);
    }

    findBySubdistrictCode(code) {
        return _.filter(addresses, (addr) => addr.subdistrictCode === code);
    }

    zips() {
        return _.sortBy(_.uniq(_.map(addresses, (addr) => addr.zip)));
    }

    provinces() {
        return _.sortBy(_.uniqBy(_.map(addresses, (addr) => ({
            name: addr.province,
            code: addr.provinceCode
        })), 'code'), 'name');
    }

    districts(code) {
        return _.map(_.sortBy(_.uniqBy(_.filter(addresses, (addr) => addr.provinceCode === code), 'districtCode'), 'district'), (addr) => ({
            name: addr.district,
            code: addr.districtCode
        }));
    }

    subdistricts(code) {
        return _.map(_.sortBy(_.uniqBy(_.filter(addresses, (addr) => addr.districtCode === code), 'subdistrictCode'), 'subdistrict'), (addr) => ({
            name: addr.subdistrict,
            code: addr.subdistrictCode
        }));
    }
};

export default ThaiAddr;