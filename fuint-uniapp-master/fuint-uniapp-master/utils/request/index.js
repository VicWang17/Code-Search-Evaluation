/**
 * request插件地址：https://ext.dcloud.net.cn/plugin?id=822
 */
import store from '@/store'
import request from './request'
import config from '@/config'
import { isWechat } from '../app';

// 后端api地址
const baseURL = config.apiUrl;
const merchantNo = config.merchantNo;

// 可以new多个request来支持多个域名请求
const $http = new request({
  // 接口请求地址
  baseUrl: baseURL,
  // 服务器本地上传文件地址
  fileUrl: baseURL,
  // 服务器上传图片默认url
  defaultUploadUrl: 'clientApi/file/upload',
  // 设置请求头（如果使用报错跨域问题，可能是content-type请求类型和后台那边设置的不一致）
  header: {
    'content-type': 'application/json;charset=utf-8'
  },
  // 请求超时时间, 单位ms（默认300000）
  timeout: 300000,
  // 默认配置（可不写）
  config: {
    // 是否自动提示错误
    isPrompt: true,
    // 是否显示加载动画
    load: true,
    // 是否使用数据工厂
    isFactory: true
  }
})

// 当前接口请求数
let requestNum = 0
// 请求开始拦截器
$http.requestStart = options => {
  if (options.load) {
    if (requestNum <= 0) {
      // 打开加载动画
      uni.showLoading({
        title: '加载中',
        mask: true
      })
    }
    requestNum += 1
  }
  // 图片上传大小限制
  if (options.method == "FILE" && options.maxSize) {
    // 文件最大字节: options.maxSize 可以在调用方法的时候加入参数
    const maxSize = options.maxSize
    for (let item of options.files) {
      if (item.size > maxSize) {
        setTimeout(() => {
          uni.showToast({
            title: "图片过大，请重新上传",
            icon: "none"
          })
        }, 10)
        return false
      }
    }
  }
  // 请求前加入当前终端
  options.header['platform'] = store.getters.platform ? String(store.getters.platform) : ''
  
  // 请求前加入Token
  options.header['Access-Token'] = store.getters.token ? String(store.getters.token) : ''
  // 商户号
  options.header['merchantNo'] = uni.getStorageSync("merchantNo") ? uni.getStorageSync("merchantNo") : merchantNo; 
  // 店铺ID
  options.header['storeId'] = uni.getStorageSync("storeId") ? uni.getStorageSync("storeId") : 0;
  options.header['latitude'] = uni.getStorageSync("latitude") ? uni.getStorageSync("latitude") : '';
  options.header['longitude'] = uni.getStorageSync("longitude") ? uni.getStorageSync("longitude") : '';
  options.header['isWechat'] = isWechat() ? 'Y' : 'N';
  // return false 表示请求拦截，不会继续请求
  return options
}

// 请求结束
$http.requestEnd = options => {
  // 判断当前接口是否需要加载动画
  if (options.load) {
    requestNum = requestNum - 1
    if (requestNum <= 0) {
      uni.hideLoading()
    }
  }
}

// 登录弹窗次数
let loginPopupNum = 0

// 所有接口数据处理（可在接口里设置不调用此方法）
$http.dataFactory = async res => {
  let httpData = res.response.data
  if (typeof httpData == "string") {
    try {
      httpData = JSON.parse(httpData)
    } catch {
      httpData = false
    }
  }
  
  // 临时返回模拟数据，跳过登录校验
  if (res.url.includes('points/exchangeList')) {
    return Promise.resolve({
      code: 200,
      message: 'success',
      data: {
        list: {
          content: [
            {
              id: 1,
              name: '50元代金券',
              image: '/static/images/coupon.png',
              sellingPoint: '可抵扣任意商品',
              point: 500,
              isReceive: false,
              description: '该代金券可用于抵扣店内任意商品',
              expireDate: '2024-12-31',
              storeNames: '全部门店'
            },
            {
              id: 2,
              name: '100元储值卡',
              image: '/static/images/coupon.png',
              sellingPoint: '可充值到会员卡',
              point: 1000,
              isReceive: false,
              description: '可直接充值到会员卡内使用',
              expireDate: '2024-12-31',
              storeNames: '全部门店'
            },
            {
              id: 3,
              name: '精美礼品',
              image: '/static/images/gift.png',
              sellingPoint: '限量版纪念品',
              point: 2000,
              isReceive: false,
              description: '精美限量版礼品一份',
              expireDate: '2024-12-31',
              storeNames: '全部门店'
            }
          ],
          totalElements: 3
        }
      }
    })
  }
  
  if (res.url.includes('points/exchangeDetail')) {
    const goodsId = res.data.goodsId
    const mockDetail = {
      id: goodsId,
      name: goodsId == 1 ? '50元代金券' : (goodsId == 2 ? '100元储值卡' : '精美礼品'),
      image: goodsId == 3 ? '/static/images/gift.png' : '/static/images/coupon.png',
      point: goodsId == 1 ? 500 : (goodsId == 2 ? 1000 : 2000),
      description: goodsId == 1 ? '该代金券可用于抵扣店内任意商品' : 
                  (goodsId == 2 ? '可直接充值到会员卡内使用' : '精美限量版礼品一份'),
      expireDate: '2024-12-31',
      storeNames: '全部门店',
      isExchanged: false
    }
    return Promise.resolve({
      code: 200,
      message: 'success',
      data: {
        goods: mockDetail
      }
    })
  }
  
  if (res.url.includes('points/userPoint')) {
    return Promise.resolve({
      code: 200,
      message: 'success',
      data: {
        point: 5000
      }
    })
  }

  // 原有的登录校验逻辑注释掉
  /*
  if (httpData.code == 1001) {
    store.dispatch('Logout')
    if (loginPopupNum <= 0) {
      loginPopupNum++
      uni.showModal({
        title: '温馨提示',
        content: '此时此刻需要您登录喔~',
        confirmText: "去登录",
        cancelText: "再逛会",
        success: res => {
          loginPopupNum--
          if (res.confirm) {
            uni.navigateTo({
              url: "/pages/login/index"
            })
          }
        }
      })
    }
    return Promise.reject({
      statusCode: 0,
      errMsg: httpData.message,
      result: httpData
    })
  }
  */

  // 返回正确的结果
  return Promise.resolve(httpData)
}

// 错误回调
$http.requestError = e => {
  if (e.statusCode === 0) {
    throw e
  } else {
    setTimeout(() => {
      uni.showToast({
        title: `网络请求出错：${e.errMsg}`,
        icon: "none",
        duration: 2500
      })
    })
  }
}
export default $http
