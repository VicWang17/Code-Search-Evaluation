<template>
    <mescroll-body ref="mescrollRef" :sticky="true" @init="mescrollInit" :down="{ native: true }" @down="downCallback"
      :up="upOption" @up="upCallback">
  
      <!-- 积分兑换商品列表 -->
      <view class="goods-list clearfix" :class="['column-1']">
        <view class="goods-item" v-for="(item, index) in list.content" :key="index" @click="onTargetDetail(item.id)">
          <view class="dis-flex">
            <!-- 商品图片 -->
            <view class="goods-item_left">
              <image class="image" :src="item.image"></image>
            </view>
            <view class="goods-item_right">
              <!-- 商品名称 -->
              <view class="goods-name twolist-hidden">
                <text>{{ item.name }}</text>
              </view>
              <view class="goods-item_desc">
                <!-- 商品卖点 -->
                <view class="desc-selling_point dis-flex">
                  <text class="onelist-hidden">{{ item.sellingPoint }}</text>
                </view>
                <view class="coupon-attr">
                    <view class="attr-l">
                        <!-- 兑换所需积分 -->
                        <view class="desc_footer point-price">
                          <text class="price_x">{{ item.point }}积分</text>
                        </view>
                    </view>
                    <view class="attr-r">
                        <!--兑换按钮-->
                        <view class="receive" v-if="!item.isReceive">
                            <text>立即兑换</text>
                        </view>
                        <view class="receive state" v-if="item.isReceive">
                            <text>已兑换</text>
                        </view>
                    </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 无数据提示 -->
      <view v-if="list.content.length === 0 && !isLoading" class="no-data">
        <view class="no-data-icon">
          <text class="iconfont icon-wushuju"></text>
        </view>
        <view class="no-data-text">
          <text>暂无可兑换商品</text>
        </view>
      </view>
    </mescroll-body>
  </template>
  
  <script>
    import MescrollBody from '@/components/mescroll-uni/mescroll-body.vue'
    import MescrollMixin from '@/components/mescroll-uni/mescroll-mixins'
    import * as pointsApi from '@/api/points/exchange'
    import { getEmptyPaginateObj, getMoreListData, checkLogin } from '@/utils/app'
  
    const pageSize = 15
  
    export default {
      components: {
        MescrollBody
      },
  
      mixins: [MescrollMixin],
  
      data() {
        return {
          // 正在加载
          isLoading: true,
          // 会员积分
          userPoint: 0,
          // 兑换商品列表
          list: getEmptyPaginateObj(),
          // 上拉加载配置
          upOption: {
            // 首次自动执行
            auto: true,
            // 每页数据的数量; 默认10
            page: { size: pageSize },
            // 数量要大于4条才显示无更多数据
            noMoreSize: 4,
          }
        }
      },
  
      /**
       * 生命周期函数--监听页面加载
       */
      onLoad() {
        // 设置页面标题
        uni.setNavigationBarTitle({
          title: "积分兑换"
        })
      
        // 获取用户积分
        this.getUserPoint()
      },
  
      methods: {
        /**
         * 上拉加载的回调
         * @param {Object} page
         */
        upCallback(page) {
          const app = this
          // 设置列表数据
          app.getPointsExchangeList(page.num)
            .then(list => {
              const curPageLen = list.content.length
              const totalSize = list.totalElements
              app.mescroll.endBySize(curPageLen, totalSize)
            })
            .catch(() => app.mescroll.endErr())
        },
  
        /**
         * 获取用户积分
         */
        getUserPoint() {
          const app = this
          pointsApi.getUserPoint()
            .then(result => {
              app.userPoint = result.data.point || 0
            })
        },
  
        /**
         * 获取积分兑换商品列表
         * @param {number} pageNo 页码
         */
        getPointsExchangeList(pageNo = 1) {
          const app = this
          app.isLoading = true
          return new Promise((resolve, reject) => {
            pointsApi.list({ pageNumber: pageNo })
              .then(result => {
                app.isLoading = false
                const newList = result.data.list
                app.list.content = getMoreListData(newList, app.list, pageNo)
                resolve(newList)
              })
              .catch(err => {
                app.isLoading = false
                reject(err)
              })
          })
        },
  
        // 跳转商品详情页
        onTargetDetail(goodsId) {
          this.$navTo(`pages/points/exchange-detail`, { goodsId })
        },
        
        // 下拉刷新
        downCallback() {
          this.list = getEmptyPaginateObj()
          this.mescroll.resetUpScroll()
        }
      }
    }
  </script>
  
  <style lang="scss" scoped>
    // Reuse existing styles from coupon list page
    .goods-list {
      padding: 20rpx;
      
      .goods-item {
        box-shadow: 0 1rpx 5rpx 0px rgba(0, 0, 0, 0.05);
        background: #fff;
        margin-bottom: 20rpx;
        padding: 20rpx;
        border-radius: 8rpx;
        
        &_left {
          width: 180rpx;
          height: 180rpx;
          
          .image {
            width: 180rpx;
            height: 180rpx;
            border-radius: 8rpx;
          }
        }
        
        &_right {
          flex: 1;
          padding-left: 20rpx;
          
          .goods-name {
            font-size: 28rpx;
            color: #333;
          }
          
          .desc-selling_point {
            font-size: 24rpx;
            color: #999;
            margin: 10rpx 0;
          }
          
          .coupon-attr {
            display: flex;
            justify-content: space-between;
            align-items: center;
            
            .point-price {
              font-size: 32rpx;
              color: #f03c3c;
              font-weight: bold;
            }
            
            .receive {
              background: linear-gradient(to right, #ff6335, #f9211c);
              color: #fff;
              padding: 10rpx 20rpx;
              border-radius: 30rpx;
              font-size: 24rpx;
              
              &.state {
                background: #999;
              }
            }
          }
        }
      }
    }
    
    .no-data {
      padding: 100rpx 0;
      text-align: center;
      
      &-icon {
        font-size: 80rpx;
        color: #999;
        margin-bottom: 30rpx;
      }
      
      &-text {
        font-size: 28rpx;
        color: #999;
      }
    }
  </style>