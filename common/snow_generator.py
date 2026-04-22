# -*- coding: utf-8 -*-
'''
@文件: snow_generator.py
@說明:
@時間: 2025/01/10 15:27:29
@作者: LiDong
'''

import threading
import time
from datetime import datetime


class SnowflakeGenerator:
    def __init__(self, datacenter_id=1, worker_id=1):
        """
        初始化雪花ID生成器
        :param datacenter_id: 数据中心ID (0-31)
        :param worker_id: 机器ID (0-31)
        """
        # 64位ID的组成部分
        self.TIMESTAMP_BITS = 41  # 41位时间戳
        self.DATACENTER_BITS = 5  # 5位数据中心
        self.WORKER_BITS = 5      # 5位机器ID
        self.SEQUENCE_BITS = 12   # 12位序列号

        # 最大值
        self.MAX_DATACENTER_ID = -1 ^ (-1 << self.DATACENTER_BITS)
        self.MAX_WORKER_ID = -1 ^ (-1 << self.WORKER_BITS)
        self.MAX_SEQUENCE = -1 ^ (-1 << self.SEQUENCE_BITS)

        # 偏移量
        self.WORKER_ID_SHIFT = self.SEQUENCE_BITS
        self.DATACENTER_ID_SHIFT = self.SEQUENCE_BITS + self.WORKER_BITS
        self.TIMESTAMP_0 = self.SEQUENCE_BITS + self.WORKER_BITS
        self.TIMESTAMP_SHIFT = self.TIMESTAMP_0 + self.DATACENTER_BITS

        # 参数检查
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f'worker_id不能大于{self.MAX_WORKER_ID}或小于0')
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f'datacenter_id不能大于{self.MAX_DATACENTER_ID}或小于0')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

        # 设置起始时间戳（2024-01-01 00:00:00）
        self.EPOCH = int(datetime(2024, 1, 1, 0, 0, 0).timestamp() * 1000)

    def _get_next_timestamp(self, last_timestamp):
        """获取下一个时间戳"""
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp

    def _get_timestamp(self):
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    def get_id(self):
        """
        生成下一个ID
        :return: 64位整型ID
        """
        with self.lock:
            timestamp = self._get_timestamp()

            # 时钟回拨检查
            if timestamp < self.last_timestamp:
                raise RuntimeError('时钟回拨异常')

            # 同一毫秒内序列号自增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                # 同一毫秒序列号用完，等待下一毫秒
                if self.sequence == 0:
                    timestamp = self._get_next_timestamp(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            # 组装ID
            snow_flake_id = (
                (timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT
            ) | (
                self.datacenter_id << self.DATACENTER_ID_SHIFT
            ) | (
                self.worker_id << self.WORKER_ID_SHIFT
            ) | self.sequence

            return snow_flake_id


snow_generator = SnowflakeGenerator()
