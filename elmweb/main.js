const axios = require('axios');
const fs = require('fs-extra');
const readline = require('readline');

async function x5sec() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  rl.question('请输入 x5sec 的值：', async (answer) => {
    rl.close();

    // 创建一个 FormData 对象
    const formData = new FormData();
    formData.append('x5sec', answer);

    // 发送 POST 请求
    try {
      const response = await axios.post('http://127.0.0.1:8081/api/v1/cookies/x5sec?token=后台api', formData);
      console.log('请求已发送，服务器响应：', response.data);

      // 询问用户是否继续下一步操作
      askForNextStep();
    } catch (error) {
      console.error('请求发送失败：', error);
    }
  });
}

function askForNextStep() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  rl.question('是否继续下一步操作？(输入 y 继续，其它键退出)：', async (answer) => {
    rl.close();

    if (answer.toLowerCase() === 'y') {
      // 继续执行获取用户令牌函数
      getUserTokens();
    } else {
      console.log('已退出脚本。');
    }
  });
}

async function getUserTokens() {
  try {
    // 读取配置文件
    const configFile = await fs.readJson('config.json');
    const tokens = {};

    // 遍历配置文件中的每个用户
    for (const user in configFile) {
      if (configFile.hasOwnProperty(user)) {
        const userData = configFile[user];
        const userId = userData.user_id; // 提取 user_id

        // 创建一个 FormData 对象，添加用户名和密码
        const formData = new FormData();
        formData.append('username', userData.username);
        formData.append('password', userData.password);

        // 发送 POST 请求获取 token
        try {
          const response = await axios.post('http://127.0.0.1:8081/api/v1/login', formData);
          const token = response.data.data && response.data.data.token ? response.data.data.token : null;
          tokens[user] = {
            token: token,
            user_id: userId // 存储 token 和 user_id
          };

          console.log(`用户 ${user} 登陆请求返回消息：${response.data.msg}`);
          if (token) {
            console.log(`用户 ${user} 的 token 是：${token}`);
          }
        } catch (error) {
          console.error(`用户 ${user} 登陆请求失败：`, error);
        }
      }
    }

    // 调用获取所有账号信息的函数，并传递 tokens
    await getAllAccountInfo(tokens);
  } catch (error) {
    console.error('读取配置文件失败：', error);
  }
}

async function getAllAccountInfo(tokens) {
  try {
    // 遍历每个用户的 token
    for (const user in tokens) {
      if (tokens.hasOwnProperty(user)) {
        const { token, user_id } = tokens[user]; // 解构出 token 和 user_id

        // 设置请求头
        const headers = {
          'Authorization': token
        };

        // 发送 GET 请求
        try {
          const response = await axios.get('http://127.0.0.1:8081/api/v1/user/cookies', {
            headers: headers
          });

          // 检查返回响应中的 code 是否为 200
          if (response.data.code === 200) {
            console.log(`用户 ${user} 的账号信息获取成功：`);

            // 提取返回响应中所有 remark 和 task_id 的值，并输出 user_id
            const accountInfo = response.data.data.data;
            for (const info of accountInfo) {
              console.log(`User ID: ${user_id}, Remark: ${info.remark}, Task ID: ${info.task_id}`);
              await executeTask(info.task_id, user_id, token);
              await delay(20000); // 延迟 20 秒
            }
          } else {
            console.log(`用户 ${user} 的账号信息获取失败：${response.data.msg}`);
          }
        } catch (error) {
          console.error(`用户 ${user} 的账号信息获取失败：`, error);
        }
      }
    }
  } catch (error) {
    console.error('遍历用户 Token 出错：', error);
  }
}

async function executeTask(taskId, userId, token) {
  try {
    const headers = {
      'Authorization': token
    };

    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('user_id', userId);

    const response = await axios.post('http://127.0.0.1:8081/api/v1/task/run', formData, {
      headers: headers
    });

    console.log(`任务执行结果：${response.data.msg}`);
  } catch (error) {
    console.error('执行任务失败：', error);
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 调用获取用户令牌的函数
x5sec();
