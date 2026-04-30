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
                        show: auth('shangma_order:Create')
                    },
                    export: {
                        text: "导出",
                        title: "导出",
                        show: auth('shangma_order:Export'),
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
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth('shangma_order:Update'),
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth('shangma_order:Delete'),
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
                tenant_id: {
                    title: '租户ID',
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
                            placeholder: '请输入租户ID',
                        },
                    },
                },
                category: {
                    title: '分类',
                    search: {
                        show: true,
                    },
                    type: 'number',
                    column: {
                        minWidth: 80,
                        align: 'center',
                    },
                },
                shop_id: {
                    title: '店铺ID',
                    search: {
                        show: true,
                    },
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                shop_name: {
                    title: '店铺名称',
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
                            placeholder: '请输入店铺名称',
                        },
                    },
                },
                order_no: {
                    title: '订单号',
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                    form: {
                        rules: [
                            {
                                required: true,
                                message: '订单号必填',
                            },
                        ],
                        component: {
                            placeholder: '请输入订单号',
                        },
                    },
                },
                third_order_no: {
                    title: '第三方订单号',
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
                            placeholder: '请输入第三方订单号',
                        },
                    },
                },
                third_order_time: {
                    title: '第三方订单时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                },
                third_order_status: {
                    title: '第三方订单状态',
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
                            placeholder: '请输入第三方订单状态',
                        },
                    },
                },
                payment_method: {
                    title: '支付方式',
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
                            placeholder: '请输入支付方式',
                        },
                    },
                },
                logistics_no: {
                    title: '物流单号',
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
                            placeholder: '请输入物流单号',
                        },
                    },
                },
                logistics_name: {
                    title: '物流公司',
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
                            placeholder: '请输入物流公司',
                        },
                    },
                },
                replace_type: {
                    title: '换货类型',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                order_amount: {
                    title: '订单金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入订单金额',
                        },
                    },
                },
                order_income_amount: {
                    title: '订单收入',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                goods_amount: {
                    title: '商品金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入商品金额',
                        },
                    },
                },
                buyer_paid_shipping_fee: {
                    title: '买家支付运费',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                platform_shipping_discount: {
                    title: '平台运费优惠',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                seller_shipping_discount: {
                    title: '卖家运费优惠',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                actual_shipping_fee: {
                    title: '实际运费',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                final_shipping_fee: {
                    title: '最终运费',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                voucher_from_platform: {
                    title: '平台优惠券',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                voucher_from_seller: {
                    title: '卖家优惠券',
                    type: 'number',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                },
                commission_fee: {
                    title: '佣金费用',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                service_fee: {
                    title: '服务费用',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                other_fee: {
                    title: '其他费用',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                purchase_amount: {
                    title: '采购金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                order_shipped_time: {
                    title: '发货时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                },
                order_completed_time: {
                    title: '完成时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                        align: 'center',
                    },
                },
                order_status: {
                    title: '订单状态',
                    search: {
                        show: true,
                    },
                    type: 'number',
                    column: {
                        minWidth: 80,
                        align: 'center',
                    },
                },
                warehouse_id: {
                    title: '仓库ID',
                    type: 'input',
                    column: {
                        minWidth: 120,
                        align: 'center',
                    },
                    form: {
                        component: {
                            placeholder: '请输入仓库ID',
                        },
                    },
                },
                order_profit: {
                    title: '订单利润',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
                    },
                },
                shipping_difference: {
                    title: '运费差额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                        align: 'center',
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