<template>
  <div class="c-flex-row c-justify-content-between" style="height: 100vh;">
    <PgsqlDashboard style="width: calc(100% - 410px); height: calc(100% - 40px); margin: 20px 0"/>
    <div class="c-flex-column" style="width: 430px; height: 100%; background: RGBA(242, 246, 255, 1.00); padding: 20px;">
      <div class="c-shaow-card">
        <div class="c-flex-column" style="padding: 20px; width: 380px;">
          <div class="c-flex-row c-align-items-center c-justify-content-between">
            <span style="color: #666666">{{ $t('timeRangeTip') }}：</span>
            <i class="el-icon-time" style="font-size: 22px; color: #999999;cursor: pointer" @click="onHistoryClick"/>
          </div>
          <div class="c-flex-row c-align-items-center c-justify-content-between" style="margin-top: 10px">
            <el-date-picker
              v-model="timeSelected"
              style="width: 190px; flex-shrink: 0"
              type="datetime"
              format="yyyy-MM-dd HH:mm:ss"
              value-format="timestamp"
              :placeholder="$t('timeTip')"
              :clearable="false"
              :editable="false"
            />
            <el-select v-model="timeStep" style="width: 140px; margin-left: 5px; flex-shrink: 0" placeholder="请选择">
              <el-option
                v-for="item in timeStepOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </div>
          <div class="c-flex-row c-justify-content-right c-align-items-center">
            <div
              class="u-text-center"
              style="background: #682FF9; border-radius: 20px; padding: 6px 20px;
               color: #FFFFFF; flex-shrink: 0; cursor: pointer; width: 100%; margin-top: 10px; text-align: center"
              @click="onChatConfirm()"
            >
              {{ $t('analysisButton') }}
            </div>
          </div>
        </div>
        <Chat style="height: calc(100vh - 190px)" :messages="messages"/>
      </div>

    </div>

    <el-drawer
      :title="$t('historyTitle')"
      :visible.sync="historyDrawer"
      direction="rtl"
      v-loading="historyLoading"
    >
      <el-collapse v-model="activeName" accordion @change="onCollapseClick">
        <el-collapse-item v-for="(item, index) in historyMessages" :key="index" :title="item.title" :name="index+1">
          <Chat :messages="item.value"/>
        </el-collapse-item>
      </el-collapse>
    </el-drawer>
  </div>
</template>

<script>

import PgsqlDashboard from '@/components/PgsqlDashboard'
import Chat from '@/components/Chat'
import { nextStep, run, robotIntro, history } from '@/api/api'
import moment from 'moment'
// const MESSAGEKEY = 'chat_messages'

export default {
  components: { PgsqlDashboard, Chat },
  filters: {},
  data() {
    return {
      timeSelected: Date.now(),
      timeStep: 30,
      timeStepOptions: [
        { label: '± 30 Seconds', value: 30 },
        { label: '± 1 Minutes', value: 60 },
        { label: '± 2 Minutes', value: 120 },
        { label: '± 3 Minutes', value: 180 },
        { label: '± 5 Minutes', value: 300 }
      ],
      messages: [],
      introMessage: [],
      historyMessages: [],
      historyLoading: false,
      historyDrawer: false,
      activeName: '1',
      analyseAt: undefined
    }
  },
  watch: {},
  mounted() {
    // this.messages = JSON.parse(localStorage.getItem(MESSAGEKEY) || '[]')
    // this.getRobotIntro()
  },
  beforeDestroy() {
  },
  methods: {
    addLoadingMessage() {
      this.messages.push({
        loading: true
      })
    },
    removeLoadingMessage() {
      this.messages = this.messages.filter(item => {
        return !item.loading
      })
    },
    onHistoryClick() {
      this.historyDrawer = !this.historyDrawer
      this.historyMessages = []
      this.historyLoading = true
      history().then(res => {
        const data = res.data
        for (const dataKey in data) {
          console.log(dataKey)
          this.historyMessages.push({
            title: dataKey,
            value: data[dataKey]
          })
        }
      }).finally(() => {
        this.historyLoading = false
      })
    },
    getRobotIntro() {
      robotIntro({}).then(res => {
        this.introMessage = res.data
      }).finally(() => {
      })
    },
    onCollapseClick() {},
    formatAnalyseAt() {
      var analyseAt = moment(this.timeSelected).format('YYYY-MM-DD HH:mm:ss')
      for (var i = 0; i < this.timeStepOptions.length; i++) {
        if (this.timeStepOptions[i].value === this.timeStep) {
          analyseAt += (' ' + this.timeStepOptions[i].label)
          break
        }
      }
      return analyseAt
    },
    onChatConfirm() {
      if (!this.timeSelected) {
        this.$message.warning(this.$t('timeRangeSelectTip'))
        return
      }
      this.messages = []
      this.messages = this.messages.concat(this.introMessage)
      this.addLoadingMessage()

      this.analyseAt = this.formatAnalyseAt()
      run({
        start_at: parseInt(this.timeSelected / 1000 - this.timeStep),
        end_at: parseInt(this.timeSelected / 1000 + this.timeStep),
        analyse_at: this.analyseAt
      }).then(res => {
        if (res.data) {
          this.removeLoadingMessage()
          this.messages.push(res.data)
          // localStorage.setItem(MESSAGEKEY, JSON.stringify(this.messages))
          this.runNextStep()
        }
      }).catch(() => {
        this.removeLoadingMessage()
      })
    },
    runNextStep() {
      this.addLoadingMessage()
      nextStep({ analyse_at: this.analyseAt }).then(res => {
        if (res.data) {
          this.removeLoadingMessage()
          this.messages.push(res.data)
          // localStorage.setItem(MESSAGEKEY, JSON.stringify(this.messages))
          this.runNextStep()
        }
      }).catch(() => {
        this.removeLoadingMessage()
      })
    }
  }
}
</script>

<style>
.container >>> .el-collapse-item__header {
  background: #f9f9f9;
  width: 100vw;
}

.el-input__inner {
  border-radius: 20px;
}

.el-input--suffix .el-input__inner {
  padding-right: 10px;
}

.el-collapse-item__content {
  padding-bottom: 0;
}

.el-drawer__header {
  margin-bottom: 10px !important;
  border: none;
}

.el-drawer {
  border-radius: 12px;
  padding: 0 20px;
}

.el-collapse-item__header {
  border-bottom: none;
}

.el-collapse-item__wrap {
  border-bottom: none;
}

.el-collapse {
  border: none;
}

</style>

<style lang="scss" scoped>

.container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.status-card-container {
  margin: auto;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  overflow-x: auto;
}

.status-card {
  min-width: 80px;
  margin-right: 10px;
  display: flex;
  min-height: 50px;
  flex-direction: column;
  justify-content: flex-start;
}

.top-card-title {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  text-align: center;
  height: 20px;
}

.top-card-detail {
  color: rgba(0, 0, 0, 0.85);
  font-weight: bolder;
  font-size: 18px;
  margin-top: 5px;
  text-align: center;
}

.card-header-title {
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
  white-space: nowrap;
  word-break: break-all;
  font-size: 18px;
}

.el-divider--horizontal {
  margin: 20px 0;
}

.el-col-5 {
  width: 20%;
}

.nineGridContainer {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 相当于 1fr 1fr 1fr */
  grid-gap: 10px; /* grid-column-gap 和 grid-row-gap的简写 */
  grid-auto-flow: row;

  .nineGrid {
    background-color: #FFFFFF;
  }

  margin-top: 20px;
}

.mysqlLineChart {
  width: 100%;
  height: 200px;
}

.detectorDiagnosticChart {
  width: 800px;
  height: 300px;
}

.breathing-box {
  box-shadow: 0 0 5px 5px RGBA(103, 194, 58, 0.5);
  animation: breathing 1.8s infinite alternate;
}

@keyframes breathing {
  0% {
    box-shadow: 0 5px 5px RGBA(103, 194, 58, 0.2);
  }
  100% {
    box-shadow: 0 0 5px 5px RGBA(103, 194, 58, 0.5);
  }
}
</style>
