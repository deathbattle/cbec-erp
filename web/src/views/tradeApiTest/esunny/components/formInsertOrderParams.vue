<template>
  <el-scrollbar class="el-scrollbar-container">
    <el-divider content-position="left">接口参数</el-divider>
    <el-form ref="formRef" :inline="true" :model="formData" :rules="formRules" class="form-inline">
      <!-- <el-row>
        <el-col :span="4.8">

        </el-col>
        <el-col :span="4.8">
          
        </el-col>
        <el-col :span="4.8">
          
        </el-col>
        <el-col :span="4.8">
          
        </el-col>
        <el-col :span="4.8">
          
        </el-col>
      </el-row> -->
      <el-form-item label="买卖方向:" prop="Direct">
        <el-select v-model="formData.Direct" placeholder="请选择买卖方向" clearable>
          <el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in dictionary('esunny_direct')"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="开平标志:" prop="Offset">
        <el-select v-model="formData.Offset"  placeholder="请选择开平标志" clearable>
          <el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in dictionary('esunny_offset')"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="投机套保:" prop="Hedge">
        <el-select v-model="formData.Hedge" placeholder="请选择投机套保" clearable>
          <el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in dictionary('esunny_hedge')"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="委托类型:" prop="OrderType">
        <el-select v-model="formData.OrderType" placeholder="请选择委托类型" clearable>
          <el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in dictionary('esunny_order_type')"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="有效类型:" prop="ValidType">
        <el-select v-model="formData.ValidType" placeholder="请选择有效类型" clearable>
          <el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in dictionary('esunny_valid_type')"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="合约编号:" prop="ContractNo">
          <el-input
            v-model="formData.ContractNo"
            type="text"
            placeholder=""
          />
      </el-form-item>
      <el-row>
        <el-form-item label="席位索引:" prop="SeatIndex">
            <el-input-number
              v-model="formData.SeatIndex"
              placeholder=""
            />
        </el-form-item>
        <el-form-item label="合约索引:" prop="ContractIndex">
            <el-input-number
              v-model="formData.ContractIndex"
              placeholder=""
            />
        </el-form-item>
        <el-form-item label="委托数量:" prop="OrderQty">
            <el-input-number
              v-model="formData.OrderQty"
              placeholder=""
            />
        </el-form-item>
        <el-form-item label="最小成交量:" prop="MinQty">
            <el-input-number
              v-model="formData.MinQty"
              placeholder=""
            />
        </el-form-item>
        <el-form-item label="委托价格:" prop="OrderPrice">
            <el-input-number
              v-model="formData.OrderPrice"
              placeholder=""
            />
        </el-form-item>
      </el-row>
      <el-form-item>
        <el-button @click="handleInsertOrederTest" type="primary" :loading="btnLoading">测试</el-button>
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
import { InsertOrderParamsType } from '../types';
import { dictionary } from '/@/utils/dictionary';

const props = defineProps({
	initFormData: {
		type: Object as () => Partial<InsertOrderParamsType>,
		default: () => {},
	},
});
// const emit = defineEmits(['drawerClose']);

let btnLoading = ref(false);
let testRes = ref('');
let startTime = ref();
let endTime = ref();
let formData = reactive<InsertOrderParamsType>({
  Direct: 'B',
  Offset: 'O',
  Hedge: 'T',
  OrderType: '2',
  ValidType: '3',
  SeatIndex: 1,
  ContractIndex: 33,
  ContractNo: "CF903",
  OrderQty: 1,
  MinQty: 0,
  OrderPrice: 15000
});

const formRef = ref<FormInstance>();
  const formRules = reactive<FormRules>({
	Direct: [
		{
			required: true,
			message: '请选择',
		},
	],
	Offset: [
		{
			required: true,
			message: '请选择',
		},
	],
	Hedge: [
		{
			required: true,
			message: '请选择',
		},
	],
	OrderType: [
		{
			required: true,
			message: '请选择',
		},
	],
	ValidType: [
		{
			required: true,
			message: '请选择',
		},
	],
	SeatIndex: [
		{
			required: true,
      // pattern: /^[0-9]+$/,
			message: '请输入正整数,0轮询席位,非0指定席位',
		},
	],
	ContractIndex: [
		{
      required: true,
      // pattern: /^[0-9]+$/,
			message: '请输入正整数',
		},
	],
	ContractNo: [
		{
			required: true,
			message: '请输入',
		},
	],
	OrderQty: [
		{
      required: true,
      pattern: /^[0-9]+$/,
			message: '请输入正整数',
		},
	],
	MinQty: [
		{
      required: true,
      pattern: /^[0-9]+$/,
			message: '请输入正整数',
		},
	],
	OrderPrice: [
		{
			required: true,
      pattern: /^-?(0|[1-9]\d*)(\.\d+)?$/,
			message: '请输入数字',
		},
	],
});

const initFormData = () => {
	if (props.initFormData?.ContractNo) {
    formData.Direct = props.initFormData.Direct || 'B';
    formData.Offset = props.initFormData.Offset || 'O';
    formData.Hedge = props.initFormData.Hedge || 'T';
    formData.OrderType = props.initFormData.OrderType || '2';
    formData.ValidType = props.initFormData.ValidType || '3';
    formData.SeatIndex = props.initFormData.SeatIndex || 1;
    formData.ContractIndex = props.initFormData.ContractIndex || 33;
    formData.ContractNo = props.initFormData.ContractNo || "CF903";
    formData.OrderQty = props.initFormData.OrderQty || 1;
    formData.MinQty = props.initFormData.MinQty || 0;
    formData.OrderPrice = props.initFormData.OrderPrice || 15000;
	}
};

const handleInsertOrederTest = () => {
	formRef.value?.validate(async (valid) => {
		if (!valid) return;
		try {
      btnLoading.value = true;
      startTime.value = new Date();
      api.InserOrder(formData).then((res: APIResponseData) => {
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
