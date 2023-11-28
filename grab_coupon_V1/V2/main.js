const fs = require('fs');
const axios = require('axios'); // 请确保您已安装 axios 模块

// 从coupon_settings.json文件中读取配置信息
function readCouponSettings() {
  const fileContent = fs.readFileSync('./coupon_settings.json', 'utf8');
  return JSON.parse(fileContent);
}

// 获取 coupon_settings.json 中的配置
const couponSettings = readCouponSettings();
const { mt_url, loopCount, advanceTime, leadTime, delaytime, startTime, errorKeys, keyToExtract, webhookUrl, webhookTitle } = couponSettings;

// 获取当前时间的格式化字符串
function getCurrentTime() {
  const now = new Date();
  now.setHours(now.getHours() + 8); // 将当前时间调整为 UTC+8
  return now.toISOString(); // 返回ISO格式的时间字符串，例如：2023-09-23T14:30:00.000Z
}

// 封装函数，处理CURL文件
function processCurlFiles() {
  const files = fs.readdirSync(__dirname);

  const accountData = []; // 存储所有账户数据的数组

  files.forEach((file) => {
    if (file.endsWith('.txt')) {
      const accountName = file.replace('.txt', '');
      const fileContent = fs.readFileSync(file, 'utf-8');
      const { url, headers, body } = extractCurlData(fileContent);

      // 在这里，你可以将提取的数据存储到对应的账户变量中
      //console.log(`${getCurrentTime()} - Account: ${accountName}`);
      //console.log(`${getCurrentTime()} - URL: ${url}`);
      //console.log(`${getCurrentTime()} - Headers: ${JSON.stringify(headers)}`);
      //console.log(`${getCurrentTime()} - Body: ${body}`);
      //console.log(`${getCurrentTime()} - ------------------------`);

      accountData.push({ accountName, url, headers, body });
    }
  });

  // 提取请求URL、请求头和请求体
  function extractCurlData(curlCommand) {
    const urlRegex = /curl '([^']+)'/;
    const headerRegex = /-H '([^:]+): ([^']+)'/g;
    const bodyRegex = /--data-raw '([^']+)'/;

    const matchUrl = curlCommand.match(urlRegex);
    const url = matchUrl ? matchUrl[1] : '';

    const headers = {};
    let matchHeader;
    while ((matchHeader = headerRegex.exec(curlCommand))) {
      headers[matchHeader[1]] = matchHeader[2];
    }

    const matchBody = curlCommand.match(bodyRegex);
    const body = matchBody ? matchBody[1] : '';

    return { url, headers, body };
  }

  return accountData;
}

// 函数executeGetAndPost：提取URL中的couponReferId并构建新的GET请求，然后发送POST请求
async function executeGetAndPost(accountData) {

  // 创建一个Promise数组，用于存储并行发送的请求
  const promises = accountData.map(async ({ accountName, url, headers, body }) => {
    const couponReferIdRegex = /couponReferId=([^&]+)/;
    const matchCouponReferId = url.match(couponReferIdRegex);

    if (matchCouponReferId) {
      const couponReferId = matchCouponReferId[1];
      const newUrl = `${mt_url}${couponReferId}`;
      //console.log(`account ${accountName}:New URL: ${newUrl}`); // 打印 newUrl 变量的值

      try {
        // 发送GET请求
        const getResponse = await axios.get(newUrl, { headers });
        console.log(`${getCurrentTime()} - 账户 ${accountName} GET请求响应:`, getResponse.data.msg);

        // 等待2秒
        await new Promise(resolve => setTimeout(resolve, 2000));

        // 再发送原始参数的POST请求
        const postResponse = await axios.post(url, body, { headers });
        console.log(`${getCurrentTime()} - 账户 ${accountName} POST请求响应:`, postResponse.data.msg);
      } catch (error) {
        console.error(`${getCurrentTime()} - 账户 ${accountName} 错误:`, error);
      }
    }
  });

  // 使用Promise.all并行执行所有请求
  await Promise.all(promises);
}

// 函数executeAxiosRequest：使用账户数据构建多次POST请求，并记录响应时间
async function executeAxiosRequest(accountData) {

  const lastResponses = []; // 用于存储最后一次响应数据
  
  // 创建一个Promise数组，用于存储并行发送的请求
  const promises = accountData.map(async ({ accountName, url, headers, body }) => {
    //let lastResponse = null; // 用于存储最后一次的响应

    for (let i = 0; i < loopCount; i++) {
      const startTime = Date.now(); // 记录开始时间

      try {
        // 使用axios创建Promise并发送请求
        const response = await axios.post(url, body, { headers });

        // 提取配置文件中指定的关键字段
        const extractedData = response.data.hasOwnProperty(keyToExtract) ? response.data[keyToExtract] : response.data;
        
        //lastResponse = response; // 更新最后一次的响应

        const endTime = Date.now(); // 记录结束时间
        const responseTime = endTime - startTime; // 计算响应时间
        const formattedResponseTime = Math.round(responseTime); // 四舍五入响应时间为整数

        // 将响应数据转换为字符串以便搜索关键词
        const responseDataString = JSON.stringify(extractedData);
        
        // 存储最后一次响应数据
        lastResponses[accountName] = responseDataString;

        // 搜索关键词并终止线程
        if (errorKeys.some(errorkey => responseDataString.includes(errorkey))) {
          console.error(`${getCurrentTime()} - 账户 ${accountName}，第 ${i + 1} 次请求，响应时间: ${formattedResponseTime} ms - 响应内容:`, responseDataString);
          console.error(`${getCurrentTime()} - 账户 ${accountName}，第 ${i + 1} 次请求检测到预设错误，停止此账户线程`);
          // 终止当前账户的线程
          break;
        }


        console.log(`${getCurrentTime()} - 账户 ${accountName}，第 ${i + 1} 次请求，响应时间: ${formattedResponseTime} ms 响应内容:-`, responseDataString);

        const delayTime = parseInt(delaytime); // 从配置中获取延迟时间
        if (!isNaN(delayTime) && delayTime > 0 && i < loopCount - 1) {
          //console.log(getCurrentTime(), `等待 ${delayTime} 毫秒后继续下一次请求...`);
          await new Promise(resolve => setTimeout(resolve, delayTime));
        }
      } catch (error) {
        console.error(`${getCurrentTime()} - 账户 ${accountName}，第 ${i + 1} 次请求错误:`, error);
      }
    }
  });

  // 使用Promise.all并行执行所有账户的请求
  await Promise.all(promises);
  
  // 整理最后一次响应数据为一个字符串
  const logText = Object.entries(lastResponses)
  .map(([accountName, responseDataString]) => `${accountName}: ${responseDataString}`)
  .join('\r\n');
  
  // 输出最后一次响应数据
  console.log('最后一次响应数据：');
  console.log(logText);

  // 构造推送的消息
  const message = `${webhookTitle}\n\n${logText}`;

  // 检查 webhookUrl 是否为空
  if (webhookUrl) {
  // 发送 POST 请求到 Webhook 接口
  axios.post(webhookUrl + encodeURIComponent(message))
    .then(response => {
      console.log('日志已成功推送到 Webhook 接口。', response.data);
    })
    .catch(error => {
      console.error('推送日志到 Webhook 接口时出错：', error);
    });
} else {
  console.log('webhookUrl 为空，不执行推送操作。');
}

}

// 封装函数：某团模式
async function MouTuanSendRequests() {
    const accountData = processCurlFiles();
    await executeGetAndPost(accountData);
}

// 封装函数：发包模式
async function SendRequests() {
    const accountData = processCurlFiles();
    await executeAxiosRequest(accountData);
}

// 新增函数：某团发包模式本地定时
function MouTuan() {
    try {
        const timeParts = startTime.split(':');
        if (timeParts.length === 3) {
            const hours = parseInt(timeParts[0]);
            const minutes = parseInt(timeParts[1]);
            const seconds = parseInt(timeParts[2]);
            const currentTime = new Date();
            executionTime = new Date(currentTime.getFullYear(), currentTime.getMonth(), currentTime.getDate(), hours, minutes, seconds).getTime();
            console.log(getCurrentTime(), "当前模式为：某团发包");
            console.log(getCurrentTime(), "执行时间已设置为", startTime);
            console.log(getCurrentTime(), "循环次数已设置为", loopCount);
            console.log(getCurrentTime(), `某团链接将在设定时间提前 ${advanceTime} 毫秒执行，发包将在设定时间提前 ${leadTime} 毫秒执行`);
            setTimeout(MouTuanSendRequests, executionTime - currentTime.getTime() - advanceTime);
            setTimeout(SendRequests, executionTime - currentTime.getTime() - leadTime);

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
        console.error(getCurrentTime(), "读取或解析coupon_settings.json文件时出错：", error.message);
    }
}

// 新增函数：通用发包模式本地定时
function Standard() {
    try {
        const timeParts = startTime.split(':');
        if (timeParts.length === 3) {
            const hours = parseInt(timeParts[0]);
            const minutes = parseInt(timeParts[1]);
            const seconds = parseInt(timeParts[2]);
            const currentTime = new Date();
            executionTime = new Date(currentTime.getFullYear(), currentTime.getMonth(), currentTime.getDate(), hours, minutes, seconds).getTime();
            console.log(getCurrentTime(), "当前模式为：通用发包");
            console.log(getCurrentTime(), "执行时间已设置为", startTime);
            console.log(getCurrentTime(), "循环次数已设置为", loopCount);
            console.log(getCurrentTime(), `发包将在设定时间提前 ${leadTime} 毫秒执行`);
            //setTimeout(MouTuanSendRequests, executionTime - currentTime.getTime() - advanceTime);
            setTimeout(SendRequests, executionTime - currentTime.getTime() - leadTime);

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
        console.error(getCurrentTime(), "读取或解析coupon_settings.json文件时出错：", error.message);
    }
}

// 与账户交互获取执行时间和循环次数，并将其作为全局变量存储
function getExecutionTimeAndLoopCountFromUser() {
    const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
    });

    readline.question("请选择模式：1.某团发包  2.通用发包  3.某团测试\n", (mode) => {
        readline.close();
        switch (mode) {
            case '1':
                // 执行模式1：某团发包
                MouTuan();
                break;
            case '2':
                // 执行模式2：通用发包
                Standard();
                break;
            case '3':
                // 执行模式3：某团测试
                MouTuanSendRequests();
                break;
            default:
                console.error("无效的模式选择。");
        }
    });
}

// 调用函数以等待指定时间，然后执行脚本
getExecutionTimeAndLoopCountFromUser();
