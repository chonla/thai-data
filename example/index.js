import ThaiAddr from "../dist/index.mjs";

const thaiAddr = new ThaiAddr();

console.log(thaiAddr.zips());

console.log(thaiAddr.findByZip('10240'));

console.log(thaiAddr.provinces());

console.log(thaiAddr.districts('32000000'));

console.log(thaiAddr.subdistricts('32140000'));

console.log(thaiAddr.findBySubdistrictCode('32140200'));