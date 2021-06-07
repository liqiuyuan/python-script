#!/usr/bin/env python3
# coding=utf-8
import os
import sys
from aliyunsdkdyvmsapi.request.v20170525 import SingleCallByTtsRequest
from aliyunsdkcore.client import AcsClient
import uuid
import logging


"""
语音业务调用接口示例，版本号：v20170525
Created on 2017-06-12
"""
basedir = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger()  # 不加名称设置root logger
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

# 使用FileHandler输出到文件
fh = logging.FileHandler(f'{basedir}/alivoice.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)


# 暂时不支持多region,默认配置杭州
REGION = "cn-hangzhou"
# ACCESS_KEY_ID/ACCESS_KEY_SECRET 根据实际申请的账号信息进行替换
ACCESS_KEY_ID = "xxx"
ACCESS_KEY_SECRET = "xxxx"
# 初始化AcsClient
acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)


def tts_call(
        business_id,
        called_number,
        called_show_number,
        tts_code,
        tts_param=None):
    ttsRequest = SingleCallByTtsRequest.SingleCallByTtsRequest()
    # 申请的语音通知tts模板编码,必填
    ttsRequest.set_TtsCode(tts_code)
    # 设置业务请求流水号，必填。后端服务基于此标识区分是否重复请求的判断
    ttsRequest.set_OutId(business_id)
    # 语音通知的被叫号码，必填。
    ttsRequest.set_CalledNumber(called_number)
    # 语音通知显示号码，必填。
    ttsRequest.set_CalledShowNumber(called_show_number)
    # tts模板变量参数
    if tts_param is not None:
        ttsRequest.set_TtsParam(tts_param)
    ttsResponse = acs_client.do_action_with_exception(ttsRequest)
    return ttsResponse


if __name__ == '__main__':
    phone_number = sys.argv[1]
    message = sys.argv[2]
    __business_id = uuid.uuid1()
    logger.info(f"uuid: {__business_id}, message: {message}")
    message = str(message).replace('\\', '').replace('"', '').replace(':', '').replace('.', '点')
    # 模板中不存在变量的情况下为{}
    params = {'msg': message}
    response = (tts_call(__business_id, phone_number, "", "TTS_218130474", params))
    logger.info(response)
