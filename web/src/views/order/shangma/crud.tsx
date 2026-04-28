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
                        show: auth('shangma:Create')
                    },
                    export: {
                        text: "导出",
                        title: "导出",
                        show: auth('shangma:Export'),
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
                        show: auth('shangma:Update'),
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth('shangma:Delete'),
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
                    },
                    form: {
                        rules: [
                            {
                                required: true,
                                message: '订单号必填',
                            },
                        ],
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
                    },
                },
                third_order_time: {
                    title: '第三方订单时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
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
                    },
                },
                replace_type: {
                    title: '换货类型',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                order_amount: {
                    title: '订单金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                order_income_amount: {
                    title: '订单收入',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                goods_amount: {
                    title: '商品金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                buyer_paid_shipping_fee: {
                    title: '买家支付运费',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                platform_shipping_discount: {
                    title: '平台运费优惠',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                seller_shipping_discount: {
                    title: '卖家运费优惠',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                actual_shipping_fee: {
                    title: '实际运费',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                final_shipping_fee: {
                    title: '最终运费',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                voucher_from_platform: {
                    title: '平台优惠券',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                voucher_from_seller: {
                    title: '卖家优惠券',
                    type: 'number',
                    column: {
                        minWidth: 120,
                    },
                },
                commission_fee: {
                    title: '佣金费用',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                service_fee: {
                    title: '服务费用',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                other_fee: {
                    title: '其他费用',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                purchase_amount: {
                    title: '采购金额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                order_shipped_time: {
                    title: '发货时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
                    },
                },
                order_completed_time: {
                    title: '完成时间',
                    type: 'datetime',
                    column: {
                        minWidth: 150,
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
                    },
                },
                warehouse_id: {
                    title: '仓库ID',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                },
                order_profit: {
                    title: '订单利润',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
                shipping_difference: {
                    title: '运费差额',
                    type: 'number',
                    column: {
                        minWidth: 100,
                    },
                },
            },
        },
    };
};