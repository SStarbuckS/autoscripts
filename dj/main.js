const axios = require('axios');
const ini = require('ini');
const fs = require('fs');

// 从配置文件中读取所有配置信息
function readAllConfig() {
  const configContent = fs.readFileSync('config.ini', 'utf-8');
  return ini.parse(configContent);
}

// 获取所有配置信息
const allConfig = readAllConfig();

// 获取 baseURL
const baseURL = allConfig.urls.baseURL;

// 获取请求头信息
const headers = allConfig.headers;

// 获取时间配置信息
const { taskTime, advanceTime, leadTime } = allConfig.time;

let globalURLs = []; // 全局变量用来存储 URLs

// 获取本地时间字符串（包含毫秒）
function getLocalTime() {
  const now = new Date();
  const milliseconds = `00${now.getMilliseconds()}`.slice(-3); // 获取毫秒数并格式化为3位
  return `[${now.toLocaleString()}.${milliseconds}]`;
}

// 构建链接并抢券
async function claimCoupons() {
  let stopRequests = false;

  try {
    for (let i = 0; i < globalURLs.length; i++) {
      if (stopRequests) {
        console.log('检测到错误词，停止后续请求。');
        break;
      }

      const startTime = Date.now();

      const response = await axios.post(globalURLs[i], {}, { headers });
      const endTime = Date.now();
      const serverResponseTime = endTime - startTime;

      console.log(`${getLocalTime()} 抢券响应：${JSON.stringify(response.data)}，服务器响应时间：${serverResponseTime}ms`);

      if (JSON.stringify(response.data).includes('not login') || JSON.stringify(response.data).includes('您来太晚了')) {
        stopRequests = true;
      }
    }
  } catch (error) {
    console.error(`${getLocalTime()} 抢券请求出错：`, error);
  }
}

// 获取数据并构建链接
async function fetchData() {
  let extractedCount = 0;
  let constructedURLCount = 0;

  try {
    const response = await axios.get('http://127.0.0.1:5889/batchLog?count=6');
    const responseData = response.data;

    if (Array.isArray(responseData) && responseData.length > 0) {
      const fetchData = responseData.map(item => {
        extractedCount++;
        return Object.entries(item)
          .map(([key, value]) => `"${key}":"${value}"`)
          .join(',');
      }).join('\n');

      const urls = fetchData.split('\n').map(data => {
        constructedURLCount++;
        const constructedURL = `${baseURL}${data}&client=wh5`;
        console.log(`${getLocalTime()} 构建的链接：${constructedURL}`);
        return constructedURL;
      });

      console.log(`${getLocalTime()} 本次运行共提取了 ${extractedCount} 条数据。`);
      console.log(`${getLocalTime()} 构建了 ${constructedURLCount} 条链接。`);

      // 将生成的链接存储到全局变量中
      globalURLs = urls;

      // 在这里可以选择调用其他函数处理全局变量中的链接，或者直接在这个函数中进行处理
    } else {
      console.log(`${getLocalTime()} 未找到符合条件的数据对象。`);
    }
  } catch (error) {
    console.error(`${getLocalTime()} 发生错误：`, error);
  }
}

// 新增函数：某团发包模式本地定时
function MouTuan() {
    try {
        const timeParts = taskTime.split(':');
        if (timeParts.length === 3) {
            const hours = parseInt(timeParts[0]);
            const minutes = parseInt(timeParts[1]);
            const seconds = parseInt(timeParts[2]);
            const currentTime = new Date();
            executionTime = new Date(currentTime.getFullYear(), currentTime.getMonth(), currentTime.getDate(), hours, minutes, seconds).getTime();
            console.log(getLocalTime(), "当前模式为：某团发包");
            console.log(getLocalTime(), "执行时间已设置为", taskTime);
            console.log(getLocalTime(), `某团链接将在设定时间提前 ${advanceTime} 毫秒执行，发包将在设定时间提前 ${leadTime} 毫秒执行`);
            setTimeout(fetchData, executionTime - currentTime.getTime() - advanceTime);
            setTimeout(claimCoupons, executionTime - currentTime.getTime() - leadTime);

            // 全局执行时间倒计时
            const countdownInterval = setInterval(() => {
                const remainingTime = Math.max(0, executionTime - Date.now());
                const remainingSeconds = Math.floor(remainingTime / 1000);
                process.stdout.clearLine();
                process.stdout.cursorTo(0);
                process.stdout.write("距离执行时间还有 " + remainingSeconds + " 秒");
                if (remainingSeconds <= 0) {
                    process.stdout.write("\n");
                    clearInterval(countdownInterval);
                }
            }, 100);
        } else {
            console.error("时间格式不正确，请重新设置执行时间。");
        }
    } catch (error) {
        console.error(getLocalTime(), "读取或解析coupon_settings.json文件时出错：", error.message);
    }
}

MouTuan();
