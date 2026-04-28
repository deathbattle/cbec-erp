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

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
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
            table: {
                remove: {
                    confirmMessage: '是否删除该订单？',
                },
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('tiktok:Create')
                    },
                    export: {
                        text: "导出",
                        title: "导出",
                        show: auth('tiktok:Export'),
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
                width: 180,
                buttons: {
                    view: {
                        show: true,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth('tiktok:Update'),
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth('tiktok:Delete'),
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
                    },
                    form: {
                        rules: [
                            {
                                required: true,
                                message: '订单ID必填',
                            },
                        ],
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
                    },
                    form: {
                        component: {
                            type: 'textarea',
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
                    },
                },
                product_price: {
                    title: '商品价格',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                payment_amount: {
                    title: '支付金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
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
                    },
                },
                order_quantity: {
                    title: '下单件数',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                is_refunded: {
                    title: '已退款',
                    type: 'dict-switch',
                    dict: dict({
                        data: [
                            { label: '是', value: true },
                            { label: '否', value: false },
                        ],
                    }),
                    column: {
                        minWidth: 80,
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
                    },
                },
                content_id: {
                    title: '内容ID',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                },
                commission_model: {
                    title: '佣金模型',
                    type: 'input',
                    column: {
                        minWidth: 100,
                    },
                },
                standard_commission_rate: {
                    title: '标准佣金率',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                estimated_commission_amount: {
                    title: '预估计佣金额',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                estimated_standard_commission: {
                    title: '预计标准佣金',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                actual_commission_amount: {
                    title: '实际计佣金额',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                actual_commission: {
                    title: '实际佣金',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                store_ad_commission_rate: {
                    title: '店铺广告佣金率',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                create_time: {
                    title: '创建时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                    },
                },
                payment_time: {
                    title: '支付时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                    },
                },
                delivery_time: {
                    title: '送达时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
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
                    },
                },
            },
        },
    };
};