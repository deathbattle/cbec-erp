<template>
  <el-scrollbar class="el-scrollbar-container">
    <el-divider content-position="left">接口参数</el-divider>
    <el-form ref="formRef" :inline="true" :model="formData" :rules="formRules" class="form-inline">
      <el-form-item label="席位索引:" prop="SeatIndex">
          <el-input-number
            v-model="formData.SeatIndex"
            placeholder=""
          />
      </el-form-item>
      <el-form-item label="委托号:" prop="OrderId">
          <el-input-number
            v-model="formData.OrderId"
            placeholder=""
          />
      </el-form-item>
      <el-form-item label="系统号:" prop="SystemNo">
          <el-input
            v-model="formData.SystemNo"
            type="text"
            placeholder=""
          />
      </el-form-item>
      <el-form-item>
        <el-button @click="handleDeleteOrderTest" type="primary" :loading="btnLoading">测试</el-button>
      </el-form-item>
    </el-form>
    <el-divider content-position="left">测试结果</el-divider>
    <el-form  size="default" :disabled="btnLoading">
      <el-form-item label="开始时间:">
        <!-- <el-text class="mx-1">{{ startTime }}</el-text> -->
        <el-input
          v-model="startTime"
          type="text"
          placeholder=""
          style="width: 30%"
          :readonly=true
        />
      </el-form-item>
      <el-form-item label="结束时间:">
        <!-- <el-text class="mx-1">{{ endTime }}</el-text> -->
        <el-input
          v-model="endTime"
          type="text"
          placeholder=""
          style="width: 30%"
          :readonly=true
        />
      </el-form-item>
    </el-form>
    <el-form  class="form-result" size="default" :disabled="btnLoading">
      <el-form-item label="结果:" >
        <el-input
          v-model="testRes"
          :autosize="{ minRows: 10 }"
          type="textarea"
          placeholder=""
          :readonly=true
        />
      </el-form-item>
    </el-form>
  </el-scrollbar>
</template>

<script setup lang="ts">
import * as api from '../api';
import { ref, reactive, onMounted  } from 'vue';
import type { FormInstance, FormRules, TableInstance } from 'element-plus';
import { successNotification } from '/@/utils/message';
import { DeleteOrderParamsType } from '../types';
import { dictionary } from '/@/utils/dictionary';

const props = defineProps({
	initFormData: {
		type: Object as () => Partial<DeleteOrderParamsType>,
		default: () => {},
	},
});
// const emit = defineEmits(['drawerClose']);

let btnLoading = ref(false);
let testRes = ref('');
let startTime = ref();
let endTime = ref();
let formData = reactive<DeleteOrderParamsType>({
  SeatIndex: 0,
  OrderId: 2019012100000000031,
  SystemNo: undefined,
});

const formRef = ref<FormInstance>();
  const formRules = reactive<FormRules>({
	SeatIndex: [
		{
			required: true,
      // pattern: /^[0-9]+$/,
			message: '请输入正整数,0轮询席位,非0指定席位',
		},
	],
	OrderId: [
		{
      required: true,
      // pattern: /^[0-9]+$/,
			message: '请输入正整数',
		},
	],
	SystemNo: [
		{
			required: true,
			message: '请输入',
		},
	],
});

const initFormData = () => {
	if (props.initFormData?.SeatIndex) {
    formData.SeatIndex = props.initFormData.SeatIndex || 0;
    formData.OrderId = props.initFormData.OrderId || 2019012100000000031;
    formData.SystemNo = props.initFormData.SystemNo;
	}
};

const handleDeleteOrderTest = () => {
	formRef.value?.validate(async (valid) => {
		if (!valid) return;
		try {
      btnLoading.value = true;
      startTime.value = new Date();
      api.DeleteOrder(formData).then((res: APIResponseData) => {
        const responseData = res.data;
        endTime.value = new Date();
        testRes.value = res.msg ?? '';
        if (res?.code === 200) {
          successNotification(res.msg as string);
        }
        btnLoading.value = false;
      });
		} finally {
			btnLoading.value = false;
		}
	});
};

onMounted(() => {
	initFormData();
});
</script>

<style lang="scss" scoped>
.columns-form-com {
	height: 100%;
	padding: 20px;
	box-sizing: border-box;
}

.form-inline .el-select {
  --el-select-width: 300px;
}

.form-inline .el-input {
  --el-input-width: 300px;
}

.form-inline .el-input-number {
  --el-input-width: 300px;
}

.form-result {
  :deep(.el-textarea__inner) {
    max-height: 200px;
    width: 90%;
  }
}

.el-scrollbar-container {
  height: 100%; /* 根据需要设置合适的高度 */
}
</style>
