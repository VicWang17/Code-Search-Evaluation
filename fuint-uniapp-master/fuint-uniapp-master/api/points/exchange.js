import request from '@/utils/request'

// api地址
const api = {
  list: 'clientApi/points/exchangeList',
  detail: 'clientApi/points/exchangeDetail',
  exchange: 'clientApi/points/doExchange',
  userPoint: 'clientApi/points/userPoint'
}

// 积分兑换商品列表
export const list = (param) => {
  return request.get(api.list, param)
}

// 积分兑换商品详情
export function detail(goodsId) {
  return request.get(api.detail, { goodsId })
}

// 执行积分兑换
export function exchange(param) {
  return request.post(api.exchange, param)
}

// 获取用户积分
export function getUserPoint() {
  return request.get(api.userPoint)
} 