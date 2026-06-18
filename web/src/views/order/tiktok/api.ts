import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

export const apiPrefix = '/api/order/tiktok/';

export function GetList(query: PageQuery) {
    return request({
        url: apiPrefix,
        method: 'get',
        params: query,
    });
}

export function GetObj(id: InfoReq) {
    return request({
        url: apiPrefix + id,
        method: 'get',
    });
}

export function AddObj(obj: AddReq) {
    return request({
        url: apiPrefix,
        method: 'post',
        data: obj,
    });
}

export function UpdateObj(obj: EditReq) {
    return request({
        url: apiPrefix + obj.id + '/',
        method: 'put',
        data: obj,
    });
}

export function DelObj(id: DelReq) {
    return request({
        url: apiPrefix + id + '/',
        method: 'delete',
        data: { id },
    });
}

export function BatchDelObj(ids: number[]) {
    return request({
        url: apiPrefix + 'batch_delete/',
        method: 'post',
        data: { ids },
    });
}

export function exportData(params: any) {
    return downloadFile({
        url: apiPrefix + 'export_data/',
        params: params,
        method: 'get'
    })
}

/**
 * 同步TikTok订单
 * @param params - 同步参数
 * @param params.days - 同步最近N天的数据（默认7天）
 * @param params.start_time - 开始时间
 * @param params.end_time - 结束时间
 */
export function syncOrders(params?: {
    days?: number;
    start_time?: string;
    end_time?: string;
}) {
    return request({
        url: apiPrefix + 'sync/',
        method: 'post',
        data: params || {},
    });
}

/**
 * 获取同步状态
 */
export function getSyncStatus() {
    return request({
        url: apiPrefix + 'sync_status/',
        method: 'get',
    });
}