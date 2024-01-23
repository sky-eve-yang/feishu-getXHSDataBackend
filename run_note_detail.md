# 笔记详情

## 参数
- 笔记id

## 关于是否需要登录
xs加密强依赖cookie，就算没有登录小红书会临时分配一个cookie。如果发现该接口不需要登录，则可以在web上退出登录，找到该接口用里面的cookie即可，不会有自己账号的信息。

<img width="250" alt="image" src="https://raw.githubusercontent.com/submato/xhscrawl/main/source/84FBF3650075A8DB066F21403A724997.jpg">


## 环境
> 单独都买的代码并不依赖本项目，能够独立运行。注意保持js文件与py文件在同一目录下(调整py文件中js文件路径亦可)

- python环境
  - execjs包
  - 等其他import依赖
- java环境
- node js环境，需要支持ES13的 node js版本，也就是node js版本要晚于June 2022

## how to run 
1. 通过浏览器获取小红书cookie
2. 填入自己需要的参数
3，点击运行即可

## 如何获取自己的cookie
文字教学：https://www.zhihu.com/question/599129698/answer/3013355637?utm_id=0&wd=&eqid=b0c56cde00002d0000000006648034b5
视频教学：https://www.zhihu.com/zvideo/1534355772800929792


