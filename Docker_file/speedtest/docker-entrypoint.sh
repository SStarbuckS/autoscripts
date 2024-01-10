#!/bin/sh
while true; do
    echo "请选择模式："
    echo "1.直接测速  2.指定测速节点  3.退出"
    read -p "请输入选项： " choice

    case $choice in
        1)
            echo "执行当前测速..."
            speedtest
            ;;
        2)
            read -p "请输入测速节点地区，英文(china\beijing\shanghai)： " location
            url="https://www.speedtest.net/api/js/servers?engine=js&search=${location}"
            echo "查询节点信息：$url"
            result=$(wget -qO- $url)
            echo -e "返回的测速节点信息：\n$result"
            read -p "请输入测速节点ID，数字(123\22333\666666): " server_id
            echo "开始指定测速节点 $server_id..."
            speedtest -s $server_id
            ;;
        3)
            echo "退出"
            break
            ;;
        *)
            echo "无效选项，请重新选择."
            ;;
    esac
done
