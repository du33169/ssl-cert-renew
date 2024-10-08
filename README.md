# 腾讯云SSL免费证书自动申请+更新

自动化SSL90天免费证书申请/更新绑定Python脚本。目前仅支持腾讯云。 

注意：其他SSL证书自动化工具主要面向自建web服务器场景，但本项目只调用腾讯云API实现自动申请和更新，适用于托管于腾讯云的静态站点/CDN。

具体执行的操作：

1. 检查是否有证书"即将过期"
2. 如果有，为每一个申请一个新的，并尝试更新绑定资源
3. 删除所有已过期/已取消/已吊销的无用证书

## 要求

1. 证书绑定域名需要使用腾讯云DNS解析，否则申请时需要手动认证
2. 使用前先获取[腾讯云API密钥](https://console.cloud.tencent.com/cam/capi)

## 使用方法

1. 设置环境变量: `SECRET_ID` 、 `SECRET_KEY`
2. 运行:
	```bash
	python ssl_renew.py
	```

如果调试成功，可以部署为定时执行的云函数，例如免费的[华为函数工作流](https://console.huaweicloud.com/functiongraph/)

## 说明

申请新的免费证书需要审核（若干分钟），即使域名已经使用腾讯云DNS，自动DNS认证也可能失败。

即使更新绑定请求因为审核还未通过而失败，审核通过后系统会自动尝试更新托管。