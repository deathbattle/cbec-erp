import { request } from '/@/utils/service';

export function GetTiktokStatistics() {
    return request({
        url: '/api/order/tiktok/statistics/',
        method: 'get',
    });
}

export function GetShangmaStatistics() {
    return request({
        url: '/api/order/shangma/statistics/',
        method: 'get',
    });
}

export function GetOrderTrend(params: any) {
    return request({
        url: '/api/order/trend/',
        method: 'get',
        params: params,
    });
}

export function GetOrderSummary() {
    return request({
        url: '/api/order/summary/',
        method: 'get',
    });
}