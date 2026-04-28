<template>
  <fs-page>
    <el-row class="mx-2">
      <el-col xs="24" :sm="8" :md="6" :lg="4" :xl="4" class="p-1">
        <el-card :body-style="{ height: '100%' }">
          <p class="font-mono font-black text-center text-xl pb-5">
            接口列表
            <el-tooltip effect="dark" :content="content" placement="right">
              <el-icon>
                <QuestionFilled/>
              </el-icon>
            </el-tooltip>
          </p>
          <el-input v-model="filterText" :placeholder="placeholder"/>
          <!-- <el-tree ref="treeRef" class="font-mono font-bold leading-6 text-7xl" :data="data" :props="treeProps"
                   :filter-node-method="filterNode" icon="ArrowRightBold" :indent="38" highlight-current @node-click="onTreeNodeClick">
            <template #default="{ node, data }">
              <element-tree-line :node="node" :showLabelLine="false" :indent="32">
					<span v-if="data.status" class="text-center font-black font-normal">
						<SvgIcon name="iconfont icon-shouye" color="var(--el-color-primary)"/>&nbsp;{{ node.label }}
					</span>
                <span v-else color="var(--el-color-primary)"> <SvgIcon name="iconfont icon-shouye"/>&nbsp;{{
                    node.label
                  }} </span>
              </element-tree-line>
            </template>
          </el-tree> -->
          <el-tree ref="treeRef" class="font-mono font-bold leading-6 text-7xl" :data="data" :props="treeProps"
                   :filter-node-method="filterNode" icon="ArrowRightBold" :indent="38" highlight-current @node-click="onTreeNodeClick">
            <template #default="{ node, data }">
              <element-tree-line :node="node" :showLabelLine="false" :indent="32">
					<span v-if="data.status" class="text-center font-black font-normal">
						<SvgIcon name="iconfont icon-shouye" color="var(--el-color-primary)"/>&nbsp;{{ node.label }}
					</span>
                <span v-else color="var(--el-color-primary)"> <SvgIcon name="iconfont icon-shouye"/>&nbsp;{{
                    node.label
                  }} </span>
              </element-tree-line>
            </template>
          </el-tree>
          <iframe
            src="http://10.75.128.154:33333/chatbot/fKP8m6iRZ3sWvvK4"
            style="width: 100%; height: 100%; min-height: 700px"
            frameborder="0"
            allow="microphone">
          </iframe>
        </el-card>
      </el-col>
      <el-col xs="24" :sm="16" :md="18" :lg="20" :xl="20" class="p-1">
        <el-card :body-style="{ height: '100%', padding: '5px' }">
          <!-- <fs-crud ref="crudRef" v-bind="crudBinding">
            <template #actionbar-right>
              <importExcel api="api/system/user/" v-auth="'user:Import'">导入</importExcel>
            </template>
          </fs-crud> -->
          <formInsertOrderParams v-if="curId===2"></formInsertOrderParams>
          <formDeleteOrderParams v-if="curId===4"></formDeleteOrderParams>
        </el-card>
      </el-col>
    </el-row>

  </fs-page>
</template>

<script lang="ts" setup name="user">
import {useExpose, useCrud} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {ElTree, FormRules} from 'element-plus';
import {ref, reactive, onMounted, watch, toRaw, h} from 'vue';
import {getElementLabelLine} from 'element-tree-line';
import formInsertOrderParams from './components/formInsertOrderParams.vue';
import formDeleteOrderParams from './components/formDeleteOrderParams.vue';

const ElementTreeLine = getElementLabelLine(h);

interface Tree {
  id: number;
  name: string;
  status: boolean;
  children?: Tree[];
}

interface APIResponseData {
  code?: number;
  data: [];
  msg?: string;
}

// 引入组件
const placeholder = ref('请输入部门名称');
const filterText = ref('');
const treeRef = ref<InstanceType<typeof ElTree>>();

const treeProps = {
  children: 'children',
  label: 'name',
  icon: 'icon',
};

watch(filterText, (val) => {
  treeRef.value!.filter(val);
});

const filterNode = (value: string, data: Tree) => {
  if (!value) return true;
  return toRaw(data).name.indexOf(value) !== -1;
};

let data = ref([] as any);

const content = `
1.部门信息;
`;

let menuBtnLoading = ref(false);
let testRes = ref('');
let startTime = ref();
let endTime = ref();


const getData = () => {
  // api.GetDept({}).then((ret: APIResponseData) => {
  //   const responseData = ret.data;
  //   const result = XEUtils.toArrayTree(responseData, {
  //     parentKey: 'parent',
  //     children: 'children',
  //     strict: true,
  //   });

  //   data.value = result;
  // });
  data.value = [
    {
      parent: null,
      name: "报单",
      id:1,
      children: [
        {
          name: '报单',
          parent: 1,
          id:2,
        },
        // {
        //   name: '批量报单',
        //   parent: 1,
        //   id:3,
        // },
      ],
    },
    {
      parent: null,
      name: "撤单",
      id:2,
      children: [
        {
          name: '撤单',
          parent: 2,
          id:4,
        },
      ],
    },
  ];
};

//树形点击事件
const onTreeNodeClick = (node: any) => {
  curId.value = node.id;
  // crudExpose.doSearch({form: {dept: id}});
};

// 页面打开后获取列表数据
onMounted(() => {
  getData();
});

// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();
// 暴露的方法
// const {crudExpose} = useExpose({crudRef, crudBinding});
// 你的crud配置
// const {crudOptions} = createCrudOptions({crudExpose});
// 初始化crud配置
// const {resetCrudOptions} = useCrud({crudExpose, crudOptions});
// 当前测试场景id
const curId = ref(2)



// 页面打开后获取列表数据
onMounted(() => {
  // crudExpose.doRefresh();
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
