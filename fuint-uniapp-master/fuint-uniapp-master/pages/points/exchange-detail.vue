<template>
  <view v-if="!isLoading" class="container b-f p-b">
    <view class="base">
        <view class="goods-main">
            <view class="left">
               <image class="image" :src="detail.image"></image>
            </view>
            <view class="right">
                <view class="item">
                  <view class="name">{{ detail.name ? detail.name : '' }}</view>
                </view>
                <view class="item point-required">
                  <view class="amount">{{ detail.point }}<text class="unit">积分</text></view>
                </view>
            </view>
        </view>
        <view class="item">
           <view class="label">有效期至：</view>
           <view class="time">{{ detail.expireDate }}</view>
        </view>
        <view class="item">
          <view class="label">适用门店：</view>
          <view>{{ detail.storeNames ? detail.storeNames : '全部'}}</view>
        </view>
    </view>
    
    <view class="goods-content m-top20">
        <view class="title">商品详情</view>
        <view class="content"><jyf-parser :html="detail.description ? detail.description : '暂无...'"></jyf-parser></view>
    </view>
    
    <!-- 快捷导航 -->
    <shortcut/>
    
    <!-- 底部选项卡 -->
    <view v-if="!detail.isExchanged" class="footer-fixed">
      <view class="footer-container">
        <!-- 操作按钮 -->
        <view class="foo-item-btn">
          <view class="btn-wrapper">
            <view class="btn-item btn-item-main" @click="exchange(detail.id)">
              <text>立即兑换</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    <view v-else class="footer-fixed">
      <view class="footer-container">
        <!-- 操作按钮 -->
        <view class="foo-item-btn">
          <view class="btn-wrapper">
            <view class="btn-item btn-item-main state">
              <text>已兑换</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 兑换确认弹窗 -->
    <uni-popup ref="confirmPopup" type="dialog">
      <uni-popup-dialog 
        title="确认兑换" 
        content="确定使用积分兑换该商品吗？" 
        :before-close="true"
        @close="cancelExchange"
        @confirm="confirmExchange">
      </uni-popup-dialog>
    </uni-popup>
  </view>
</template>

<script>
  import * as pointsApi from '@/api/points/exchange'
  import { checkLogin } from '@/utils/app'
  
  export default {
    data() {
      return {
        // 正在加载
        isLoading: true,
        // 当前商品ID
        goodsId: 0,
        // 商品详情
        detail: {},
        // 用户积分
        userPoint: 0
      }
    },
    
    onLoad({ goodsId }) {
      // 记录商品ID
      this.goodsId = goodsId
      
      // 获取商品详情
      this.getGoodsDetail()
      
      // 获取用户积分
      this.getUserPoint()
    },
    
    methods: {
      // 获取商品详情
      getGoodsDetail() {
        const app = this
        app.isLoading = true
        pointsApi.detail(app.goodsId)
          .then(result => {
            app.detail = result.data.goods
            app.isLoading = false
          })
      },
      
      // 获取用户积分
      getUserPoint() {
        const app = this
        pointsApi.getUserPoint()
          .then(result => {
            app.userPoint = result.data.point || 0
          })
      },
      
      // 积分兑换
      exchange(goodsId) {
        // 检查用户积分是否足够
        if (this.userPoint < this.detail.point) {
          this.$error('积分不足，无法兑换该商品')
          return
        }
        
        // 显示确认弹窗
        this.$refs.confirmPopup.open()
      },
      
      // 取消兑换
      cancelExchange() {
        this.$refs.confirmPopup.close()
      },
      
      // 确认兑换
      confirmExchange() {
        const app = this
        pointsApi.exchange({ goodsId: app.goodsId })
          .then(result => {
            app.$success('兑换成功')
            // 更新商品状态
            app.detail.isExchanged = true
            // 更新用户积分
            app.userPoint -= app.detail.point
            // 关闭弹窗
            app.$refs.confirmPopup.close()
          })
          .catch(err => {
            app.$error(err.message || '兑换失败')
            app.$refs.confirmPopup.close()
          })
      }
    }
  }
</script>

<style lang="scss" scoped>
  // Reuse and adapt styles from coupon detail page
  .base {
    background: #fff;
    padding: 30rpx;
    margin-bottom: 20rpx;
    
    .goods-main {
      display: flex;
      margin-bottom: 30rpx;
      
      .left {
        width: 200rpx;
        height: 200rpx;
        
        .image {
          width: 200rpx;
          height: 200rpx;
          border-radius: 8rpx;
        }
      }
      
      .right {
        flex: 1;
        padding-left: 20rpx;
        
        .name {
          font-size: 32rpx;
          font-weight: bold;
          color: #333;
        }
        
        .point-required {
          margin-top: 20rpx;
          
          .amount {
            font-size: 42rpx;
            color: #f03c3c;
            font-weight: bold;
            
            .unit {
              font-size: 24rpx;
              margin-left: 5rpx;
            }
          }
        }
      }
    }
    
    .item {
      display: flex;
      margin-bottom: 15rpx;
      font-size: 28rpx;
      
      .label {
        color: #999;
        width: 160rpx;
      }
      
      .time {
        color: #333;
      }
    }
  }
  
  .goods-content {
    background: #fff;
    padding: 30rpx;
    
    .title {
      font-size: 30rpx;
      font-weight: bold;
      margin-bottom: 20rpx;
      border-left: 4rpx solid #f03c3c;
      padding-left: 15rpx;
    }
    
    .content {
      font-size: 28rpx;
      color: #666;
      line-height: 1.6;
    }
  }
  
  .footer-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 100rpx;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
    
    .footer-container {
      width: 100%;
      padding: 0 30rpx;
      
      .foo-item-btn {
        width: 100%;
        
        .btn-wrapper {
          .btn-item {
            height: 80rpx;
            line-height: 80rpx;
            text-align: center;
            border-radius: 40rpx;
            color: #fff;
            font-size: 30rpx;
            background: linear-gradient(to right, #ff6335, #f9211c);
            
            &.state {
              background: #999;
            }
          }
        }
      }
    }
  }
</style> 