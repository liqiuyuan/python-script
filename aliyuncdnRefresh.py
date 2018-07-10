#!/usr/bin/python
# -*- coding:utf-8 -*-
# 手动刷新阿里云 cdn目录
# 当返回{"RefreshTaskId":"2572169593","RequestId":"901A91C2-348C-4591-9861-0F0C31475B94"} 即表示刷新成功

from aliyunsdkcore.client import AcsClient
from aliyunsdkcdn.request.v20141111 import RefreshObjectCachesRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException
# 调用阿里云SDK api信息
AcessKeyId = 'xxx'
AccessKeySecret = 'xxxx'
RegionId = 'cn-hongkong'

client = AcsClient(AcessKeyId, AccessKeySecret, RegionId)
# cnd刷新的目录
objectPath = 'http://xxxx.com/'
# cdn刷新的方式
objectType = 'Directory'

request = RefreshObjectCachesRequest.RefreshObjectCachesRequest()
request.set_ObjectPath(objectPath)  # 刷新地址
request.set_ObjectType(objectType)  # 地址类型
request.set_accept_format('json')

try:
    response = client.do_action_with_exception(request)
    print(response)
except ServerException as e:
    print(e.get_http_status())
    print(e.get_error_code())
    print(e.get_error_msg())