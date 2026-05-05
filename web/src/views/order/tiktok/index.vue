<template>
  <fs-page>
    <el-card :body-style="{ height: '100%' }">
      <fs-crud ref="crudRef" v-bind="crudBinding">
        <template #actionbar-right>
          <importExcel api="api/order/tiktok/" v-auth="'tiktok_order:Import'">导入</importExcel>
        </template>
      </fs-crud>
    </el-card>
  </fs-page>
</template>

<script lang="ts" setup name="tiktokOrder">
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import importExcel from '/@/components/importExcel/index.vue';
import { ref, onMounted } from 'vue';

const crudRef = ref();
const crudBinding = ref();
const { crudExpose } = useExpose({ crudRef, crudBinding });
const { crudOptions } = createCrudOptions({ crudExpose, context: {} });
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions });

onMounted(() => {
  crudExpose.doRefresh();
});
</script>

<style lang="scss" scoped>
.el-row {
  height: 100%;

  .el-col {
    height: 100%;
  }
}

.el-card {
  height: 100%;
}

.font-normal {
  font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, SimSun, sans-serif;
}
</style>