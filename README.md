# 北航每日自动打卡脚本 v1.1

虽然到了学校还是没听打卡一次，但是我根本记不住啊！！不做人了！自动打卡机器上线！

功能列表：
- 在校打卡、不在校打卡
- 自定义定位
- 检测登录是否成功和网页能否打开
- 定时自动打卡*
- 微信推送打卡结果**
- 日志记录

\* 定时自动打卡需要程序持续开启，退出或关机无效，建议部署到服务器如阿里云等。

\** 微信推送结果需要http://sc.ftqq.com/ 支持，免费申请


本脚本基于chrome和selenium，原理为模拟浏览器点击，支持linux系统部署。部分代码参考自https://github.com/buaalzm/fuckdaka 以及 https://github.com/colasama/buaa-ncov-hitcarder ，两者各有一些不足之处，我整合了一下。


## 部署
### windows
1、下载谷歌浏览器并查看版本

2、```pip install requests, selenium```

3、下载对应版本Chromedriver:https://chromedriver.chromium.org/downloads

4、放到一个环境变量能找到的位置或者配置该位置为环境变量（自行百度）

5、在python中测试
```
from selenium import webdriver
browser = webdriver.Chrome()
browser.get("https://www.baidu.com/")
````
6、下载main.py或in_school.py并修改其中关键信息，运行
```
python main.py
```

###centOS
1、安装chrome

```yum install https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm```

2、确认chrome版本：
```google-chrome --version```

3、根据版本下载Chromedriver: https://chromedriver.chromium.org/downloads

4、将下载的文件解压之后的```chromedriver```移动到```/usr/bin```下，并给予执行权限

```chmod +x /usr/bin/chromedriver```

5、同windows

6、同windows



