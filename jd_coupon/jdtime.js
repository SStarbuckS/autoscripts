const axios = require('axios');

class JDTimer {
    constructor() {
        this.headers = {
            'User-Agent': 'okhttp/3.12.1;jdmall;android;version/10.5.0;build/95837;',
            'Content-Type': 'application/x-www-form-urlencoded',
        };
        this.jdTime();
    }

    async jdTime() {
        const url = 'https://api.m.jd.com/client.action?functionId=queryMaterialProducts&client=wh5';
        try {
            const response = await axios.get(url, { headers: this.headers });
            const xApiRequestId = response.headers['x-api-request-id'];
            if (xApiRequestId) {
                const timestamp = xApiRequestId.split('-').pop();
                return parseInt(timestamp, 10);
            } else {
                throw new Error("响应标头中没有找到 'X-Api-Request-Id'");
            }
        } catch (error) {
            console.error(error);
        }
    }

    localTime() {
        return Date.now();
    }

    async localJdTimeDiff() {
        try {
            const localTime = this.localTime();
            const jdTime = await this.jdTime();
            const timeDiff = localTime - jdTime;
            console.log(`本地时间: ${localTime}, 京东服务器时间: ${jdTime}, 时间差: ${timeDiff} ms`);
            return timeDiff;
        } catch (error) {
            console.error(error);
            return 0;
        }
    }
}

(async function main() {
    const jdtimer = new JDTimer();
    for (let i = 0; i < 5; i++) {
        console.log(await jdtimer.localJdTimeDiff());
    }
})();
