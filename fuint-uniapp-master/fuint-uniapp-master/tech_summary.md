# Fuint会员营销系统技术文档

## 1. 项目概述

Fuint会员营销系统是一套专为实体店铺开发的会员管理和营销系统。基于前后端分离架构，前端采用Uniapp+Vue开发，支持微信小程序和H5，后端基于Java SpringBoot + MySQL。系统提供完整的会员管理、卡券营销、积分系统、支付功能和商户管理等模块。

## 2. 系统架构

### 2.1 技术架构
- **前端**：Vue2 + Uniapp + uView UI
- **后端**：Java SpringBoot + MySQL + Redis
- **通信**：RESTful API

### 2.2 目录结构
```
fuint-uniapp/
├── api/                # API接口模块
│   ├── login/          # 登录相关API
│   ├── merchant/       # 商户管理API
│   ├── points/         # 积分相关API
│   └── ...
├── components/         # 公共组件
├── pages/              # 页面文件
│   ├── index/          # 首页
│   ├── user/           # 用户中心
│   ├── coupon/         # 卡券相关
│   ├── merchant/       # 商户管理
│   └── ...
├── static/             # 静态资源
├── store/              # Vuex状态管理
├── utils/              # 工具类
│   ├── request/        # 请求封装
│   └── ...
├── App.vue             # 应用入口组件
├── main.js             # 应用入口JS
├── manifest.json       # 应用配置
├── pages.json          # 页面路由配置
└── config.js           # 全局配置
```

## 3. 核心功能模块

### 3.1 会员管理模块

#### 功能描述
提供会员注册、登录、信息管理、等级体系等功能。

#### 相关文件
| 文件路径 | 功能说明 |
|---------|---------|
| api/user.js | 用户信息API接口 |
| api/login/index.js | 用户登录认证API |
| pages/user/index.vue | 会员中心页面 |
| pages/user/setting.vue | 个人信息设置 |
| pages/user/code.vue | 会员码页面 |
| pages/user/card.vue | 领取会员卡页面 |
| pages/user/password.vue | 密码管理页面 |
| pages/user/mobile.vue | 手机号修改页面 |

#### 功能流程
1. 用户通过微信授权或手机号注册/登录
2. 系统分配会员等级和权益
3. 用户查看个人信息、积分、余额
4. 用户可通过会员码进行线下核销和消费

### 3.2 卡券营销模块

#### 功能描述
管理优惠券、储值卡、计次卡的发放、领取、使用和转赠。

#### 相关文件
| 文件路径 | 功能说明 |
|---------|---------|
| api/coupon.js | 卡券领取中心API |
| api/myCoupon.js | 我的卡券API |
| api/give.js | 卡券转赠API |
| pages/coupon/list.vue | 卡券列表页面 |
| pages/coupon/detail.vue | 卡券详情页面 |
| pages/my-coupon/index.vue | 我的卡券页面 |
| pages/give/index.vue | 转赠记录页面 |
| pages/coupon/receive.vue | 卡券兑换页面 |

#### 功能流程
1. 用户浏览可领取的卡券列表
2. 用户领取或购买卡券
3. 用户在我的卡券中查看已领取的卡券
4. 用户可使用、转赠或查看卡券详情
5. 商户可通过扫码核销用户的卡券

### 3.3 积分系统模块

#### 功能描述
管理会员积分的获取、使用、转赠和查询。

#### 相关文件
| 文件路径 | 功能说明 |
|---------|---------|
| api/points/log.js | 积分明细API |
| pages/points/detail.vue | 积分明细页面 |
| pages/points/gift.vue | 积分转赠页面 |

#### 功能流程
1. 用户通过消费、活动等方式获得积分
2. 用户查询积分明细和变动历史
3. 用户可将积分转赠给其他会员
4. 用户可使用积分兑换卡券或商品

### 3.4 商户管理模块

#### 功能描述
为商户提供会员管理、卡券发放、订单管理等功能。

#### 相关文件
| 文件路径 | 功能说明 |
|---------|---------|
| api/merchant/coupon.js | 商户卡券管理API |
| api/merchant/member.js | 商户会员管理API |
| api/merchant/order.js | 商户订单管理API |
| api/merchant/recharge.js | 商户充值管理API |
| pages/merchant/index.vue | 商户管理主页 |
| pages/merchant/member/* | 会员管理相关页面 |
| pages/merchant/order/index.vue | 订单列表页面 |
| pages/merchant/balance/recharge.vue | 会员充值页面 |
| pages/merchant/coupon/receive.vue | 卡券发放页面 |

#### 功能流程
1. 商户登录商户管理后台
2. 商户可查看和管理会员列表
3. 商户可向会员发放卡券
4. 商户可为会员充值余额
5. 商户可查看订单记录和统计数据

### 3.5 订单支付模块

#### 功能描述
实现商品订单创建、结算、支付和状态跟踪。

#### 相关文件
| 文件路径 | 功能说明 |
|---------|---------|
| api/order.js | 订单管理API |
| api/settlement.js | 结算中心API |
| pages/settlement/index.vue | 结算中心页面 |
| pages/settlement/goods.vue | 订单确认页面 |
| utils/app.js | 支付处理功能 |

#### 功能流程
1. 用户选择商品加入购物车
2. 用户进入结算页面确认订单
3. 用户选择支付方式(微信支付/余额支付等)
4. 系统处理支付请求并更新订单状态
5. 用户可查看订单详情和状态

## 4. 核心API接口

### 4.1 用户认证API

| 接口名称 | 接口路径 | 功能描述 |
|---------|----------|---------|
| 用户注册 | clientApi/sign/register | 注册新用户 |
| 用户登录 | clientApi/sign/signIn | 账号密码登录 |
| 微信登录 | clientApi/sign/mpWxLogin | 微信小程序快捷登录 |
| 微信授权 | clientApi/sign/mpWxAuth | 微信公众号授权登录 |
| 发送验证码 | clientApi/sms/sendVerifyCode | 发送短信验证码 |

### 4.2 用户信息API

| 接口名称 | 接口路径 | 功能描述 |
|---------|----------|---------|
| 用户信息 | clientApi/user/info | 获取当前用户信息 |
| 会员码信息 | clientApi/user/qrCode | 获取会员码信息 |
| 账户资产 | clientApi/user/asset | 查询账户资产(积分/余额) |
| 会员设置 | clientApi/user/setting | 获取会员设置 |
| 保存信息 | clientApi/user/saveInfo | 保存用户信息 |

### 4.3 卡券相关API

| 接口名称 | 接口路径 | 功能描述 |
|---------|----------|---------|
| 卡券列表 | clientApi/coupon/list | 获取可领取卡券列表 |
| 领取卡券 | clientApi/coupon/receive | 领取指定卡券 |
| 卡券详情 | clientApi/coupon/detail | 查看卡券详情 |
| 我的卡券 | clientApi/myCoupon/list | 查询已领取的卡券 |
| 卡券详情 | clientApi/userCouponApi/detail | 查询我的卡券详情 |
| 删除卡券 | clientApi/myCoupon/remove | 删除已领取的卡券 |

### 4.4 积分相关API

| 接口名称 | 接口路径 | 功能描述 |
|---------|----------|---------|
| 积分列表 | clientApi/points/list | 获取积分明细列表 |
| 积分转赠 | clientApi/points/doGive | 将积分转赠给他人 |

### 4.5 订单相关API

| 接口名称 | 接口路径 | 功能描述 |
|---------|----------|---------|
| 订单统计 | clientApi/order/todoCounts | 获取待处理订单数量 |
| 订单列表 | clientApi/order/list | 获取订单列表 |
| 订单详情 | clientApi/order/detail | 查看订单详情 |
| 取消订单 | clientApi/order/cancel | 取消指定订单 |
| 支付订单 | clientApi/pay/doPay | 支付指定订单 |
| 确认收货 | clientApi/order/receipt | 确认订单收货 |

### 4.6 商户管理API

| 接口名称 | 接口路径 | 功能描述 |
|---------|----------|---------|
| 会员列表 | merchantApi/member/list | 获取会员列表 |
| 会员详情 | merchantApi/member/info | 查看会员详情 |
| 保存会员 | merchantApi/member/save | 保存会员信息 |
| 发放卡券 | merchantApi/coupon/sendCoupon | 向会员发放卡券 |
| 会员充值 | merchantApi/balance/doRecharge | 为会员充值余额 |

## 5. 工具类说明

### 5.1 网络请求工具

**文件路径**: utils/request/index.js

**功能描述**: 封装HTTP请求处理，包含拦截器、统一错误处理和登录状态校验。

**主要方法**:
- GET 请求: `request.get(url, data, options)`
- POST 请求: `request.post(url, data, options)`
- 文件上传: `request.upload(url, files, options)`

### 5.2 应用工具函数

**文件路径**: utils/app.js

**功能描述**: 提供通用功能方法，如平台检测、消息提示、支付处理等。

**主要方法**:
- 平台检测: `getPlatform()`
- 消息提示: `showSuccess()`/`showError()`/`showToast()`
- 页面导航: `navTo(url, query)`
- 登录验证: `checkLogin()`/`needLogin()`
- 支付处理: `wxPayment(options)`

### 5.3 存储工具

**文件路径**: utils/storage.js

**功能描述**: 对本地存储操作的封装，提供数据持久化方法。

**主要方法**:
- 设置缓存: `set(key, value)`
- 获取缓存: `get(key)`
- 移除缓存: `remove(key)`
- 清空缓存: `clear()`

### 5.4 通用工具函数

**文件路径**: utils/util.js

**功能描述**: 提供数据格式化、URL处理等通用函数。

**主要方法**:
- URL编码: `urlEncode(data)`
- 日期格式化: `formatDate(date, format)`
- 数组操作: `inArray(value, array)`
- 对象操作: `isEmpty(obj)`/`cloneObj(obj)`

## 6. 业务流程

### 6.1 用户注册与登录流程
1. 用户进入小程序，系统检查登录状态
2. 未登录时引导用户进入登录页面
3. 用户选择微信快捷登录或手机号登录
4. 系统验证用户身份后生成token并保存
5. 跳转至首页，显示用户信息

### 6.2 卡券领取与使用流程
1. 用户在卡券中心浏览可领取的卡券
2. 用户点击领取按钮获取卡券
3. 系统将卡券分配给用户并记录
4. 用户在"我的卡券"中查看已领取的卡券
5. 用户到店消费时，出示卡券二维码
6. 商户通过扫码核销用户的卡券

### 6.3 会员充值与消费流程
1. 用户选择预存/充值卡券
2. 用户选择充值金额并支付
3. 系统记录充值交易并增加用户余额
4. 用户消费时可选择余额支付
5. 系统从用户余额中扣减消费金额
6. 系统记录消费交易并更新余额

### 6.4 商户管理流程
1. 商户登录商户管理后台
2. 商户可查看会员列表和会员详情
3. 商户可为会员发放卡券或积分
4. 商户可为会员充值余额
5. 商户可查看订单记录和统计数据
6. 商户可通过扫码为会员核销卡券

## 7. 开发与部署

### 7.1 开发环境要求
- Node.js 10.0+
- HBuilderX 3.0+
- 微信开发者工具

### 7.2 配置说明
在 `config.js` 文件中进行全局配置：
```javascript
module.exports = {
   // 系统名称
   name: "fuint会员系统",
   // 后端api地址
   apiUrl: "https://www.fuint.cn/fuint-application/",
   // 默认商户号
   merchantNo: "10001"
}
```

### 7.3 部署步骤
1. 使用HBuilderX打开项目
2. 修改 `config.js` 配置信息
3. 编译为微信小程序
4. 在微信开发者工具中预览和上传

## 8. 安全与注意事项

### 8.1 数据安全
- 使用token机制保护API请求
- 敏感信息加密存储
- 定期清理本地缓存

### 8.2 性能优化
- 使用分页加载减少数据请求量
- 图片懒加载减少初始加载时间
- 本地缓存减少重复请求

### 8.3 兼容性注意事项
- 不同微信版本兼容处理
- 小程序与H5环境差异处理
- 不同机型屏幕适配 