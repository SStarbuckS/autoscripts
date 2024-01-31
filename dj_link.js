const axios = require('axios');
const cheerio = require('cheerio');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// 通过 readline 提问用户输入 targetUrl
rl.question('Please enter the target URL: ', (targetUrl) => {
  rl.close();

  const headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Host': 'prodev.m.jd.com'
  };

  axios.get(targetUrl, { headers })
    .then(response => {
      const $ = cheerio.load(response.data);

      // 在所有的 script 标签中查找包含 window.__api_data__ 的内容
      $('script').each((index, element) => {
        const scriptContent = $(element).html();
        if (scriptContent.includes('window.__api_data__')) {
          // 使用正则表达式提取 window.__api_data__ 内容
          const match = scriptContent.match(/window\.__api_data__\s*=\s*({.*?});/);
          if (match && match[1]) {
            const jsonString = match[1];

            // 尝试解析 JSON 数据
            try {
              const jsonData = JSON.parse(jsonString);

              // 从 targetUrl 中提取 activityId
              const activityIdMatch = targetUrl.match(/\/active\/([^\/]+)/);
              const activityId = activityIdMatch && activityIdMatch[1];

              // 构建新的 URL
              if (jsonData.floorList && jsonData.floorList.length > 0) {
                jsonData.floorList.forEach(floor => {
                  if (floor.couponList && floor.couponList.length > 0) {
                    floor.couponList.forEach(coupon => {
                      const channel = coupon.channel;
                      const scene = coupon.scene;
                      const args = coupon.args;

                      // 构建新的 URL
                      const newUrl = `https://api.m.jd.com/client.action?functionId=newBabelAwardCollection&body={"activityId":"${activityId}","scene":"${scene}","args":"${args}"`;

                      // 输出新的 URL
                      console.log('New URL:', newUrl);
                      console.log('-------------------------');
                    });
                  }
                });
              }
            } catch (error) {
              console.error('Error parsing JSON:', error);
            }
          }
        }
      });
    })
    .catch(error => {
      console.error('Error fetching the page:', error);
    });
});
