<template>
  <fs-page>
    <el-card class="mb-4">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white">
          <div class="text-sm opacity-80">TikTok订单总数</div>
          <div class="text-2xl font-bold mt-1">{{ tiktokStats.total || 0 }}</div>
        </div>
        <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white">
          <div class="text-sm opacity-80">上马订单总数</div>
          <div class="text-2xl font-bold mt-1">{{ shangmaStats.total || 0 }}</div>
        </div>
        <div class="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white">
          <div class="text-sm opacity-80">TikTok总销售额</div>
          <div class="text-2xl font-bold mt-1">{{ formatMoney(tiktokStats.total_amount?.toString()) }}</div>
        </div>
        <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-4 text-white">
          <div class="text-sm opacity-80">上马总销售额</div>
          <div class="text-2xl font-bold mt-1">{{ formatMoney(shangmaStats.total_amount?.toString()) }}</div>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card title="订单趋势">
          <div ref="trendChart" class="h-80"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card title="TikTok订单状态分布">
          <div ref="tiktokPieChart" class="h-64"></div>
        </el-card>
        <el-card title="上马订单状态分布" class="mt-4">
          <div ref="shangmaPieChart" class="h-64"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card title="TikTok佣金统计">
          <el-table :data="tiktokCommission" border>
            <el-table-column prop="status" label="状态" />
            <el-table-column prop="count" label="订单数" />
            <el-table-column prop="amount" label="佣金金额" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card title="上马利润统计">
          <el-table :data="shangmaProfit" border>
            <el-table-column prop="status" label="状态" />
            <el-table-column prop="count" label="订单数" />
            <el-table-column prop="profit" label="利润" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </fs-page>
</template>

<script lang="ts" setup name="dashboard">
import { ref, onMounted, onUnmounted } from 'vue';
import * as api from './api';
import { EChartsType } from 'echarts';

const tiktokStats = ref({ total: 0, total_amount: 0 });
const shangmaStats = ref({ total: 0, total_amount: 0 });
const tiktokCommission = ref([]);
const shangmaProfit = ref([]);

const trendChart = ref(null);
const tiktokPieChart = ref(null);
const shangmaPieChart = ref(null);

let trendChartInstance: EChartsType | null = null;
let tiktokPieChartInstance: EChartsType | null = null;
let shangmaPieChartInstance: EChartsType | null = null;

const formatMoney = (amount: string) => {
  if (!amount) return '0.00';
  return parseFloat(amount).toFixed(2);
};

const initCharts = () => {
  if (typeof window !== 'undefined' && window.echarts) {
    trendChartInstance = window.echarts.init(trendChart.value);
    tiktokPieChartInstance = window.echarts.init(tiktokPieChart.value);
    shangmaPieChartInstance = window.echarts.init(shangmaPieChart.value);
    loadTrendChart();
    loadPieCharts();
  }
};

const loadTrendChart = () => {
  api.GetOrderTrend({ days: 7 }).then((res: any) => {
    const data = res.data || { dates: [], tiktok: [], shangma: [] };
    const option = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['TikTok订单', '上马订单'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: data.dates },
      yAxis: { type: 'value' },
      series: [
        { name: 'TikTok订单', type: 'line', data: data.tiktok },
        { name: '上马订单', type: 'line', data: data.shangma },
      ],
    };
    trendChartInstance?.setOption(option);
  });
};

const loadPieCharts = () => {
  const tiktokOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: 'TikTok订单状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 35, name: '待确认' },
          { value: 25, name: '客户未付款' },
          { value: 20, name: '不符合条件' },
          { value: 20, name: '已完成' },
        ],
      },
    ],
  };

  const shangmaOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: '上马订单状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 40, name: '待发货' },
          { value: 30, name: '已发货' },
          { value: 20, name: '已完成' },
          { value: 10, name: '已取消' },
        ],
      },
    ],
  };

  tiktokPieChartInstance?.setOption(tiktokOption);
  shangmaPieChartInstance?.setOption(shangmaOption);
};

const loadData = () => {
  api.GetTiktokStatistics().then((res: any) => {
    tiktokStats.value = res.data || {};
    tiktokCommission.value = res.data?.commission || [];
  });

  api.GetShangmaStatistics().then((res: any) => {
    shangmaStats.value = res.data || {};
    shangmaProfit.value = res.data?.profit || [];
  });
};

const handleResize = () => {
  trendChartInstance?.resize();
  tiktokPieChartInstance?.resize();
  shangmaPieChartInstance?.resize();
};

onMounted(() => {
  loadData();
  setTimeout(() => {
    initCharts();
  }, 100);
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  trendChartInstance?.dispose();
  tiktokPieChartInstance?.dispose();
  shangmaPieChartInstance?.dispose();
});
</script>

<style lang="scss" scoped>
.grid {
  display: grid;
}
</style>