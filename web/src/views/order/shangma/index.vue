<template>
  <fs-page>
    <el-card>
      <fs-crud ref="crudRef" v-bind="crudBinding">
        <template #actionbar-right>
          <importExcel api="api/order/shangma/" v-auth="'shangma:Import'">导入</importExcel>
        </template>
      </fs-crud>
    </el-card>
  </fs-page>
</template>

<script lang="ts" setup name="shangmaOrder">
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import importExcel from '/@/components/importExcel/index.vue';

const crudRef = ref();
const crudBinding = ref();
const { crudExpose } = useExpose({ crudRef, crudBinding });
const { crudOptions } = createCrudOptions({ crudExpose });
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions });

import { ref, onMounted } from 'vue';

onMounted(() => {
  crudExpose.doRefresh();
});
</script>