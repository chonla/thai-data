import ThaiAddr, { ThaiAddrMiniRecord, ThaiAddrRecord } from "../dist/index.mjs";

const thaiAddr: ThaiAddr = new ThaiAddr();

const zips: string[] = thaiAddr.zips();
console.log(zips);

const addressesByZip: ThaiAddrRecord[] = thaiAddr.findByZip('10240');
console.log(addressesByZip);

const provinces: string[] = thaiAddr.provinces();
console.log(provinces);

const districts: ThaiAddrMiniRecord[] = thaiAddr.districts('32000000');
console.log(districts);

const subdistricts: ThaiAddrMiniRecord[] = thaiAddr.subdistricts('32140000');
console.log(subdistricts);

const subdistrict: ThaiAddrRecord = thaiAddr.findBySubdistrictCode('32140200')
console.log(subdistrict);