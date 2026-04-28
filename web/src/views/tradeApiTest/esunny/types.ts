// export interface PageQuery {
//   page: number;
//   limit: number;
// }

// export interface APIResponseData {
//   code?: number;
//   data: any;
//   msg?: string;
// }

// export interface CurrentInfoType {
//   role: string;
//   model: string;
//   app: string;

//   menu: string;
// }

// export interface ModelItemType {
//   app: string;
//   key: string;
//   title: string;
//   showText?: string;
// }

// export interface AddColumnsDataType extends CurrentInfoType {
//   id?: number | string;
//   field_name: string;
//   title: string;
//   is_query: boolean;
//   is_create: boolean;
//   is_update: boolean;
// }

// export interface ColumnsFormDataType {
//   id?: number | string;
//   field_name: string;
//   title: string;
//   is_create: boolean;
//   is_update: boolean;
//   is_query: boolean;
// }

// export interface InsertOrderParamsType {
//   direct: string;
//   offset: string;
//   hedge: string;
//   order_type: boolean;
//   valid_type: boolean;
//   seat_index: number | string;
//   account_index?: number | string;
//   order_qty: number;
//   min_qty: number;
// }

export interface InsertOrderParamsType {
  Direct: string;
  Offset: string;
  Hedge: string;
  OrderType: string;
  ValidType: string;
  SeatIndex: number;
  ContractIndex: number;
  ContractNo: string;
  OrderQty: number;
  MinQty: number;
  OrderPrice: number;
}
export interface DeleteOrderParamsType {
  SeatIndex: number;
  OrderId: number;
  SystemNo?: string;
}

