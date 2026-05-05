import * as api from './api';
import {
    dict,
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import { auth } from '/@/utils/authFunction';
import { commonCrudConfig } from "/@/utils/commonCrud";

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        // 直接返回api调用结果，fast-crud会通过全局配置的transformRes自动转换格式
        return await api.GetList(query);
    };
    const editRequest = async ({ form, row }: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({ row }: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({ form }: AddReq) => {
        return await api.AddObj(form);
    };

    const exportRequest = async (query: UserPageQuery) => {
        return await api.exportData(query)
    }

    return {
        crudOptions: {
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            // hooks: {
            //     beforePageQuery: (ctx: any) => {
            //         console.log('beforePageQuery 执行了');
            //         return ctx;
            //     },
            //     afterPageQuery:(ctx: any) => {
            //         // 请求成功了，处理数据
            //         debugger
            //         console.log('查询成功，数据为：', ctx.res.records)
            //         return ctx
            //     }
            // },
            table: {
                remove: {
                    confirmMessage: '是否删除该订单？',
                },
                onRefreshed: {
                    // 列表刷新回调
                    querySuccess: (data: any) => {
                        debugger
                        console.log('列表刷新回调', data);
                    },
                },
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('tiktok_order:Create')
                    },
                    export: {
                        text: "导出",
                        title: "导出",
                        show: auth('tiktok_order:Export'),
                        click() {
                            return exportRequest(crudExpose!.getSearchFormData())
                        }
                    },
                    clear: {
                        text: "清空筛选",
                        title: "清空筛选",
                        show: true,
                        click() {
                            crudExpose!.doSearch({ form: {} })
                        }
                    }
                }
            },
            rowHandle: {
                fixed: 'right',
                width: 250,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        link: true,
                        show: auth('tiktok_order:Update'),
                    },
                    remove: {
                        iconRight: 'Delete',
                        link: true,
                        show: auth('tiktok_order:Delete'),
                    },
                },
            },
            columns: {
                _index: {
                    title: '序号',
                    form: { show: false },
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true,
                    },
                },
                order_id: {
                    title: '订单ID',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                    form: {
                        rules: [
                            {
                                required: true,
                                message: '订单ID必填',
                            },
                        ],
                        component: {
                            placeholder: '请输入订单ID',
                        },
                    },
                },
                product_id: {
                    title: '商品ID',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入商品ID',
                        },
                    },
                },
                product_name: {
                    title: '商品名称',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                    form: {
                        component: {
                            // type: 'textarea',
                            placeholder: '请输入商品名称',
                        },
                    },
                },
                sku_id: {
                    title: 'SKU ID',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入SKU ID',
                        },
                    },
                },
                product_price: {
                    title: '商品价格',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入商品价格',
                        },
                    },
                },
                payment_amount: {
                    title: '支付金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入支付金额',
                        },
                    },
                },
                currency_unit: {
                    title: '货币单位',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入货币单位',
                        },
                    },
                },
                order_quantity: {
                    title: '下单件数',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入下单件数',
                        },
                    },
                },
                is_refunded: {
                    title: '已退款',
                    search: {
                        show: true,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            { label: '是', value: true },
                            { label: '否', value: false },
                        ],
                    }),
                    column: {
                        minWidth: 80,
                        align: 'center',
                    },
                },
                payment_method: {
                    title: '付款方式',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入付款方式',
                        },
                    },
                },
                order_status: {
                    title: '订单状态',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入订单状态',
                        },
                    },
                },
                influencer_username: {
                    title: '达人用户名',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入达人用户名',
                        },
                    },
                },
                content_type: {
                    title: '内容形式',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入内容形式',
                        },
                    },
                },
                content_id: {
                    title: '内容ID',
                    type: 'input',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入内容ID',
                        },
                    },
                },
                commission_model: {
                    title: '佣金模型',
                    type: 'input',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入佣金模型',
                        },
                    },
                },
                standard_commission_rate: {
                    title: '标准佣金率',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入标准佣金率',
                        },
                    },
                },
                estimated_commission_amount: {
                    title: '预估计佣金额',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                estimated_standard_commission: {
                    title: '预计标准佣金',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                actual_commission_amount: {
                    title: '实际计佣金额',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                actual_commission: {
                    title: '实际佣金',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                store_ad_commission_rate: {
                    title: '店铺广告佣金率',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                create_time: {
                    title: '创建时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                },
                payment_time: {
                    title: '支付时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                },
                delivery_time: {
                    title: '送达时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                },
                platform: {
                    title: '平台',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 80,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入平台',
                        },
                    },
                },
                ...commonCrudConfig({
                    dept_belong_id: {
                        form: true,
                        table: true
                    }
                })
            },
        },
    };
};