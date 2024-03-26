import os.path,re
from pycore._base import *
import pycore.okx.Account_api as Account
import pycore.okx.Funding_api as Funding
import pycore.okx.Market_api as Market
import asyncio
import pycore.okx.Public_api as Public
import pycore.okx.Trade_api as Trade
import pycore.okx.status_api as Status
import pycore.okx.subAccount_api as SubAccount
import pycore.okx.TradingData_api as TradingData
import pycore.okx.Broker_api as Broker
import pycore.okx.Convert_api as Convert
import pycore.okx.FDBroker_api as FDBroker
import pycore.okx.Rfq_api as Rfq
import pycore.okx.TradingBot_api as TradingBot
import pycore.okx.Finance_api as Finance
import pycore.okx.Copytrading_api as Copytrading
import time
import threading
from datetime import datetime, timedelta
class BuyThread(threading.Thread, Base):
    args = None
    interval = 0.5
    __execute_timelong = 0
    __execute_tag = {}
    buy_restlimit = 60
    __cachestore = []
    __schedulelist = []
    __new_instId = [] #新币列表
    __newcoinverify = {} #before seconds verify
    def __init__(self, args, target=None,flag="1", group_queue=None, public_queue=None, thread_id=None,thread_name=None, daemon=False):#1模拟交易,0真实交易
        threading.Thread.__init__(self, name=thread_name, daemon=daemon)
        self.__group_queue = group_queue
        self.__public_queue = public_queue
        self.__thread_id = thread_id
        self.task = args.get('task')
        args_flag = args.get('flag')
        if args_flag != None:
            flag = args_flag
        self.flag = flag
        if target == None:
            target = args.get('target')
        self.target = target
        self.args = args
        self.thread_name = thread_name
        self.resultQueue = []
        self.is_alive = True
    def main(self):
        self.init_api()

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        # 创建一个新的事件循环
        loop = asyncio.new_event_loop()
        # 在新的事件循环中运行异步任务
        loop.run_until_complete(self.main_coroutine())
        # 关闭事件循环
        # loop.close()

    # 是的,我要赚到的,
    # 我要赚几百万元人民币 + 美金
    async def buy_coin(self):
        orders = self.get_cachestore(clear=True)
        # print("wait order",orders)
        if len(orders) > 0:
            self.com_util.pprint(orders)
            check_orders = []
            for order in orders:
                if order.get('type') == 'new':
                    if 'clOrdId' not in order:
                        generated_order_id = self.com_exchange.generate_order_id()
                        order['clOrdId'] = generated_order_id
                new_order = self.com_exchange.check_order(order)
                if new_order != None:
                    check_orders.append(new_order)

            remaining = self.execute_check(interval=2, limit=60, tag="buy")
            if remaining > 0 :
                self.com_util.print_info(check_orders)
                # Create an async task to execute place_multiple_orders
                # async_place_orders_task = asyncio.create_task(self.tradeAPI.place_multiple_orders(orders))
                try:
                    result = self.tradeAPI.place_multiple_orders(check_orders)
                    code, data,msg = self.get_code_and_data(result)
                    try:
                        sMsg = data.get('sMsg')
                        if "Insufficient" in sMsg:
                            for order in orders:
                                order['sz'] = self.com_string.scale_number(order['sz'])
                    except:
                        pass
                    self.com_util.pprint(result)
                except Exception as e:
                    self.com_util.print_warn(e)
                    code = -1
                # If you want to store the result of the task, you can use 'await' keyword:
                # result = await async_place_orders_task
                if code != 0:
                    self.save_cachestore(orders)
                else:
                    for order in orders:
                        if order.get('type') == 'new':
                            instId = order['instId']
                            #下单成功后新新币订单加入监控列表（一个数组而已）
                            sz = order['sz']
                            self.com_util.print_info(f'buy new-coin {instId} {sz} success.')
                            self.__new_instId.append({
                                "order_id": order['clOrdId'],
                                "instId": instId,
                                "automatically_cancel_order": False,
                                "sz": sz,
                                "timestamp":self.com_util.create_timestamp(),
                                "monitor_time": 0,
                            })


        # 参数名	类型	是否必须	描述
        # instId	String	是	产品ID，如 BTC-USD-190927-5000-C
        # tdMode	String	是	交易模式
        # 保证金模式：isolated：逐仓 ；cross：全仓
        # 非保证金模式：cash：非保证金
        # ccy	String	否	保证金币种，仅适用于单币种保证金模式下的全仓杠杆订单
        # clOrdId	String	否	客户自定义订单ID
        # 字母（区分大小写）与数字的组合，可以是纯字母、纯数字且长度要在1-32位之间。
        # tag	String	否	订单标签
        # 字母（区分大小写）与数字的组合，可以是纯字母、纯数字，且长度在1-16位之间。
        # side	String	是	订单方向
        # buy：买， sell：卖
        # posSide	String	可选	持仓方向
        # 在双向持仓模式下必填，且仅可选择 long 或 short。 仅适用交割、永续。
        # ordType	String	是	订单类型
        # market：市价单
        # limit：限价单
        # post_only：只做maker单
        # fok：全部成交或立即取消
        # ioc：立即成交并取消剩余
        # optimal_limit_ioc：市价委托立即成交并取消剩余（仅适用交割、永续）
        # sz	String	是	委托数量
        # px	String	可选	委托价格，仅适用于limit、post_only、fok、ioc类型的订单
        # reduceOnly	Boolean	否	是否只减仓，true 或 false，默认false
        # 仅适用于币币杠杆，以及买卖模式下的交割/永续
        # 仅适用于单币种保证金模式和跨币种保证金模式
        # tgtCcy	String	否	市价单委托数量sz的单位，仅适用于币币市价订单
        # base_ccy: 交易货币 ；quote_ccy：计价货币
        # 买单默认quote_ccy， 卖单默认base_ccy
        # banAmend	Boolean	否	是否禁止币币市价改单，true 或 false，默认false
        # 为true时，余额不足时，系统不会改单，下单会失败，仅适用于币币市价单
        # tpTriggerPx	String	否	止盈触发价，如果填写此参数，必须填写 止盈委托价
        # tpOrdPx	String	否	止盈委托价，如果填写此参数，必须填写 止盈触发价
        # 委托价格为-1时，执行市价止盈
        # slTriggerPx	String	否	止损触发价，如果填写此参数，必须填写 止损委托价
        # slOrdPx	String	否	止损委托价，如果填写此参数，必须填写 止损触发价
        # 委托价格为-1时，执行市价止损
        # tpTriggerPxType	String	否	止盈触发价类型
        # last：最新价格
        # index：指数价格
        # mark：标记价格
        # 默认为last
        # slTriggerPxType	String	否	止损触发价类型
        # last：最新价格
        # index：指数价格
        # mark：标记价格
        # 默认为last
        # quickMgnType	String	否	一键借币类型，仅适用于杠杆逐仓的一键借币模式：
        # manual：手动，auto_borrow： 自动借币，auto_repay： 自动还币
        # 默认是manual：手动
        # 返回结果
        # {
        #     "code":"0",
        #     "msg":"",
        #     "data":[
        #         {
        #             "clOrdId":"oktswap6",
        #             "ordId":"12345689",
        #             "tag":"",
        #             "sCode":"0",
        #             "sMsg":""
        #         }
        #     ]
        # }
        # 返回参数
        # 参数名	类型	描述
        # ordId	String	订单ID
        # clOrdId	String	客户自定义订单ID
        # tag	String	订单标签
        # sCode	String	事件执行结果的code，0代表成功
        # sMsg	String	事件执行失败或成功时的msg

        # tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
        # 下单  Place Order
        # result = tradeAPI.place_order(instId='BTC-USDT-SWAP', tdMode='cross', side='sell', posSide='',
        #                               ordType='market', sz='100',tgtCcy='',banAmend='',quickMgnType='auto_borrow',
        #                               tpTriggerPx = '1111', tpOrdPx = '1000', slTriggerPx = '', slOrdPx = '', tpTriggerPxType = '', slTriggerPxType = '')
        # 批量下单  Place Multiple Orders
        # result = tradeAPI.place_multiple_orders([
        #     {'instId': 'BTC-USD-210402', 'tdMode': 'isolated', 'side': 'buy', 'ordType': 'limit', 'sz': '1', 'px': '17400',
        #      'posSide': 'long',
        #      'clOrdId': 'a12344', 'tag': 'test1210','tgtCcy':''},
        #     {'instId': 'BTC-USD-210409', 'tdMode': 'isolated', 'side': 'buy', 'ordType': 'limit', 'sz': '1', 'px': '17359',
        #      'posSide': 'long',
        #      'clOrdId': 'a12344444', 'tag': 'test1211','tgtCcy':''}
        # ])
        # 前三个蜡烛图至少有两个是亮的,并且要一个比一个高
        # 最后一个蜡烛图不能同时小于前两个
        # 前两个的差距不能比最后一个大太多
        # print("this buy new coin")
        return "yes" + "gain"
    def get_buy_orders(self,tasks):
        orders = []
        # orders
        # {
        #     'exec_time': exec_time,
        #     'exec_timestamp': timestamp,
        #     'instId': instId,
        #     'schedule': schedule_type,
        #     'side': side,
        #     'sz': sz,
        #     'ordType': ordType,
        #     'type': type,
        #     'px': px,
        # }
        for task in tasks:
            orders.append({
                "instId": task.get("instId"),  # 产品ID，如 BTC-USD-190927-5000-C
                "tdMode": "cash",  # task.get("tdMode")
                "ordType": task.get("ordType"),  # market,limit
                "sz": task.get("sz"),  # 委托数量type
                "side": task.get("buy"),
                "px": task.get("px"),  # 委托价格
            })
        self.save_cachestore(orders)
        return orders
                    #'%Y-%m-%d %H:%M:%S'
    def schedule(self, exec_time, instId,side,sz,ordType, px="",type="",):
        # 判断 exec_time 的格式
        time_formatstr = self.com_string.is_timestring(exec_time)
        time_format = '%Y-%m-%d %H:%M:%S'
        time_format_hms = '%H:%M:%S'

        if time_formatstr == time_format:
            timestamp = datetime.strptime(exec_time, time_format).timestamp()
            schedule_type = 'core'
        elif time_formatstr == time_format_hms:
            now = datetime.now()
            time_only = datetime.strptime(exec_time, time_format_hms)
            timestamp = datetime(now.year, now.month, now.day, time_only.hour, time_only.minute, time_only.second).timestamp()
            schedule_type = 'interval'
        else:
            self.com_util.print_warn("Invalid exec_time format")
            return
        task = {
            'exec_time': exec_time,
            'exec_timestamp': timestamp,
            'tdMode': "cash",
            'instId': instId,
            'schedule': schedule_type,
            'side':side,
            'sz':self.get_sz( sz,instId,side),
            'ordType':ordType,
            'type': type,
            'px': px,
        }
        task_string = self.com_string.json_tostring(task)
        self.com_util.print_info(f"add coin_schedule {task_string}")

        self.__schedulelist.append(task)
        self.__schedulelist.sort(key=lambda x: x['exec_timestamp'])#, reverse=True)

    def check_schedule(self,current_timestamp):
        buy_list = []
        while True:
            if len(self.__schedulelist) == 0:
                break
            # 弹出一个数据
            schedule_data = self.__schedulelist.pop(0)
            # print(f"schedule_data {schedule_data}")

            # 检查是否为昨天的core schedule
            if schedule_data['schedule'] == 'core':
                exec_date = datetime.fromtimestamp(schedule_data['exec_timestamp']).date()
                if exec_date == datetime.now().date() - timedelta(days=1):
                    # 根据exec_time重新生成今天的exec_timestamp
                    today_exec_time = datetime.now().replace(hour=schedule_data['exec_time'].hour,
                                                             minute=schedule_data['exec_time'].minute,
                                                             second=schedule_data['exec_time'].second, microsecond=0)
                    schedule_data['exec_timestamp'] = int(today_exec_time.timestamp())

            # 判断是否大于或等于exec_timestamp
            if current_timestamp >= schedule_data['exec_timestamp']:
                side = schedule_data.get('side')
                schedule_data["side"] =side
                buy_list.append(schedule_data)
            else:
                # 将数据从新压回原位置
                self.__schedulelist.insert(0, schedule_data)

                # 计算离执行该函数还有多长时间
                remaining_time = schedule_data['exec_timestamp'] - current_timestamp
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"离该函数最近的一个执行还有 {hours} 时 {minutes} 分 {seconds} 秒")

                # 结束循环，不再检测后续数据
                break
        self.save_cachestore(buy_list)
    def add_buy(self,instId,side,sz,ordType, px,type,info=False):
        sz = self.get_sz(sz,instId,side)
        order = {
            "instId":instId,
            "side":side,
            "tdMode": "cash",  # task.get("tdMode")
            "sz":sz,#self.get_sz(sz,instId),
            "ordType":ordType,
            "px":px,
            "type":type,
            "trade_type":"buy",
        }
        if sz <= 0:
            self.com_util.print_warn(f"instId {instId} {side} {sz} is zero, Not Add to sell Tasks.")
            self.com_util.pprint(order)
            return
        if info:
            self.com_util.print_info(f"Notion: add_buy {instId} to tasks")
            self.com_util.print_info(f"Notion: add_buy {instId} to tasks")
            self.com_util.print_info(f"Notion: add_buy {instId} to tasks")
            self.com_util.print_info(f"Notion: add_buy {instId} to tasks")
            self.com_util.pprint(order)
        task_string = self.com_string.json_tostring(order)
        self.com_util.print_info(f"add coin_buy {task_string}")
        self.save_cachestore([order])

    def get_sz(self, sz, trade_name,side):
        if sz == "all":
            if side == "buy":
                return self.availUSDT
            else:
                # print("trade_name",trade_name)
                result = self.accountAPI.get_maximum_trade_size(instId=trade_name, tdMode='cross', ccy='', px='',
                                                           leverage='10', unSpotOffset='false')
                self.com_util.pprint(result)
                availBal = self.com_exchange.from_resultgetavail(result, "maxSell")
                availBal = float(availBal)
                print("availBal",result,availBal)
                return availBal
            # trade_price = await self.get_trade_price(trade_name)
            # result = trade_price / self.__per_price
        elif sz == "automation":
            result = self.accountAPI.get_account(trade_name)
            availBal = self.com_exchange.from_resultgetavail(result, "availBal")
            availBal = float(availBal)
            return availBal
        else:
            return float(sz)
    async def monitor(self):
        while True:
            # 获取当前时间戳
            current_timestamp = self.com_exchange.get_HKtimestamp()
            self.check_schedule(current_timestamp)
            tasks = []
            sale_tasks = []
            while self.task.qsize() > 0:
                task = self.task.get()
                tasks.append(task)
            self.get_buy_orders(tasks)
            # self.buy_coin(buy_tasks)
            # self.sale_coin(sale_tasks)
            self.__execute_timelong += self.interval
            await asyncio.sleep(self.interval)

    async def repeat_run_buycoin(self):
        while True:
            await self.buy_coin()
            await asyncio.sleep(1)

    async def main_coroutine(self):
        repeat_run_buycoin = self.repeat_run_buycoin()
        monitor = self.monitor()
        monitor_newcoin = self.repeat_run_monitornewcoin()
        await asyncio.gather(repeat_run_buycoin, monitor,monitor_newcoin)
    def execute_check(self, interval, tag, limit):
        accumtime = self.__execute_tag.get(tag)
        if accumtime == None:
            self.__execute_tag[tag] = {
                "interval": 0,
                "addn": 0,
            }
        self.__execute_tag[tag]["addn"] += 1
        self.__execute_tag[tag]["interval"] += self.interval
        if self.__execute_tag[tag]["interval"] % interval == 0:
            self.__execute_tag[tag]["addn"] = 0
        result = limit - self.__execute_tag[tag]["addn"]
        return result
    def get_cachestore(self,clear=False):
        orders = self.__cachestore
        if clear:
            self.__cachestore = []
        return orders
    def save_cachestore(self,order):
        self.__cachestore += order
    def get_availUSDT(self):
        result = self.accountAPI.get_account('USDT')
        totalUSDT = self.com_exchange.from_resultgetavail(result,"availBal")
        totalUSDTFloat = float(totalUSDT)
        totalUSDTInt = int(totalUSDTFloat)
        self.availUSDT = totalUSDTInt
        self.com_util.print_info(f"current USDT {self.availUSDT} from {totalUSDTFloat}")

    def is_consecutive_decline(self,prices,length=5):
        if len(prices) < length:
            return False

        for i in range(len(prices) - 1, len(prices) - length, -1):
            if prices[i] >= prices[i - 1]:
                return False
        return True
    async def repeat_run_monitornewcoin(self):
        while True:
            await self.monitor_newcoin()
            await asyncio.sleep(1)
    async def monitor_newcoin(self):
        for item in self.__new_instId:
            order_id = item['order_id']
            instId = item['instId']
            timestamp = item['timestamp']
            item['monitor_time'] += 1
            file_path = self.com_config.get_public('cointemp/curses.pyc.txt')
            if os.path.exists(file_path):
                filecontent = self.com_file.read_file(file_path)
                first_line = re.split(re.compile(r'\n+'),filecontent)
                if len(first_line) > 0:
                    first_line = first_line[0]
                    if first_line:
                        first_line= first_line.strip()
                    print(f"命令{first_line}")
                    if first_line == "sell":
                        message = f"monitor: nnewb {instId} force sell"
                        self.com_util.print_warn(message)
                        self.chancesalenewcoin_(instId)
                    elif first_line == "skip":
                        pass
                    elif first_line == "reserve":
                        continue
            # self.com_util.pprint(item)

            history_pricestring = self.db_redis.read_list(tabname=instId)
            if len(history_pricestring) == 0:
                self.com_util.print_warn(f'monitor {instId} has not history-prices')
                continue
            history_pricestring = self.com_exchange.parse_redisparsestring(history_pricestring)
            current = history_pricestring[-1]

            now_timestamp = self.com_util.create_timestamp(length=13)
            current_timestamp = current['timestamp']
            last_received_time = now_timestamp - current_timestamp
            last_received_time = last_received_time / 1000
            if last_received_time > 3:
                self.com_util.print_warn(f"Warning: redis has not received {last_received_time} seconds, please check the front end")
                self.com_util.print_warn(f"Warning: redis has not received {last_received_time} seconds, please check the front end")
                self.com_util.print_warn(f"Warning: redis has not received {last_received_time} seconds, please check the front end")
                self.com_util.print_warn(f"Warning: redis has not received {last_received_time} seconds, please check the front end")
                self.com_util.print_warn(f"Warning: redis has not received {last_received_time} seconds, please check the front end")
                self.com_util.print_warn(f"Warning: redis has not received {last_received_time} seconds, please check the front end")
            else:
                self.com_util.print_info(f"last received {instId} data before {last_received_time}s")
            current_price = current['lastPrice']
            current_time = self.com_util.timestamp_todate(current_timestamp)

            befores = [
                {
                    "before_time":"5s",
                    "diff_rate":0.09999999999999999,
                    "verify":3,
                },
                {
                    "before_time": "20s",
                    "diff_rate": 0.19999999999999998,
                    "verify":2,
                },
                {
                    "before_time": "30s",
                    "diff_rate": 0.6,
                    "verify":2,
                },
                {
                    "before_time": "60s",
                    "diff_rate": 1.2,
                    "verify":2,
                },
                {
                    "before_time": "180s",
                    "diff_rate": 1.2,
                    "verify":2,
                },
                {
                    "before_time": "300s",
                    "diff_rate": 1.2,
                    "verify":2,
                }
            ]
            for before in befores:
                before_sconds = before.get('before_time')
                diff_rate = before.get('diff_rate')
                verify = before.get('verify')

                if instId not in self.__newcoinverify:
                    self.__newcoinverify[instId] = {}
                if before_sconds not in self.__newcoinverify[instId]:
                    self.__newcoinverify[instId][before_sconds] = 0

                if self.__newcoinverify[instId][before_sconds] > 0 and current_price >= self.__newcoinverify[instId][before_sconds]:
                    self.__newcoinverify[instId][before_sconds] = 0
                    self.com_util.print_info(f"monitor The {instId} verification by {before_sconds}, the current price is just curses.pyc jumper")

                before_prices = self.com_exchange.find_value_within(history_pricestring,before_sconds, current_timestamp)
                if before_prices != None:
                    before_price = before_prices["lastPrice"]
                    diff_price = current_price - before_price
                    diff_price = float(diff_price)
                    diff_price = format(diff_price, ".14f")
                    rate = self.com_util.calculate_percentage(diff_price, current_price)
                    rate = float(rate)
                    rate_str = format(rate, ".14f")
                    before_timestamp = before_prices['timestamp']
                    before_time = self.com_util.timestamp_todate(before_timestamp)
                    trend = "up"
                    if rate < 0:
                        trend = "down"
                        if abs(rate) >= diff_rate:
                            self.__newcoinverify[instId]["verify_price"] = current_price

                            self.__newcoinverify[instId][before_sconds] += 1
                            verify_accum = self.__newcoinverify[instId][before_sconds]
                            if verify_accum >= verify:
                                sell_message = f'monitor: Falling beyond verify {verify_accum} the {rate_str} within {before_sconds} seconds, nnewb {instId}  sell all'
                                self.com_util.print_warn(sell_message)
                                self.chancesalenewcoin_(instId)
                                continue
                            else:
                                verify_wait = verify_accum - verify
                                sell_message = f'monitor: Wait vefiry {verify_wait} the {rate_str} within {before_sconds}'
                                self.com_util.print_warn(sell_message)

                    trend_message = f'newb {instId} {before_sconds} seconds, {trend} {rate_str}'
                    if trend == "up":
                        self.com_util.print_info(trend_message)
                    else:
                        self.com_util.print_warn(trend_message)
            history_prices = [price["lastPrice"] for price in history_pricestring]
            history_prices.remove(max(history_prices))
            max_price = max(history_prices)
            wihtmax_diff = current_price - max_price
            rate_withmaxprice = self.com_util.calculate_percentage(wihtmax_diff, current_price)
            rate_withmaxprice = float(rate_withmaxprice)
            rate_withmaxprice_str = format(rate_withmaxprice, ".14f")

            max_diffmessage = f"monitor: nnewb {instId} with maxprice-rate {rate_withmaxprice_str}."
            if wihtmax_diff < 0:
                self.com_util.print_warn(max_diffmessage)
                max_rate = 2.0
                if abs(rate_withmaxprice) >= max_rate:
                    max_diffmessage = f"monitor: The nnewb {instId} difference vs highest price reaches {max_rate}, sell all"
                    self.com_util.print_warn(max_diffmessage)
                    self.chancesalenewcoin_(instId)
                    continue
            else:
                self.com_util.print_info(max_diffmessage)

            if item["automatically_cancel_order"] != True:
                self.com_util.print_info(f"monitor: Still {item['monitor_time']}  automatic cancellatio nnewb {instId}")
                if item['monitor_time'] > 20:# 20秒后，未交易完的撤单
                    self.com_util.print_info(f"monitor: Automatically canceling the order")
                    result = self.tradeAPI.cancel_order(instId, clOrdId=order_id)
                    code,data,msg = self.get_code_and_data(result)
                    if code != 0:
                        self.com_util.print_warn(f"monitor: Automatically {msg}")
                    else:
                        self.com_util.print_info(f"monitor: nnewb {instId} Automatically canceling success.")
                        item["automatically_cancel_order"] = True
    def chancesalenewcoin_(self,instId):
        self.add_buy(instId=instId, side="sell", sz="all", ordType="market", px="",type="",info=True)
        self.__new_instId = [item for item in self.__new_instId if item['instId'] != instId]
    def get_code_and_data(self,response):
        code = response.get('code')
        data = []
        msg = response.get('msg')

        if code != None:
            data = response.get('data', [])
            if len(data) > 0:
                data = data[0]
        return int(code), data,msg
    def init_api(self,):
        self.api_key = self.com_config.get_config("okx","api_key")
        self.secret_key = self.com_config.get_config("okx","secret_key")
        self.passphrase = self.com_config.get_config("okx","passphrase")
        self.marketAPI = Market.MarketAPI(self.api_key, self.secret_key, self.passphrase, True, self.flag)
        self.com_util.print_info("MarketAPI initialized.")
        self.accountAPI = Account.AccountAPI(self.api_key, self.secret_key, self.passphrase, False, "0")
        self.com_util.print_info("AccountAPI initialized.")
        self.tradeAPI = Trade.TradeAPI(self.api_key, self.secret_key, self.passphrase, False, "0")
        self.com_util.print_info("TradeAPI initialized.")
        self.get_availUSDT()
    def get_histroy_candlestacks(self):
        # result = marketAPI.get_history_index_candlesticks(instId='BTC-USDT', after='', before='', bar='', limit='')
        pass
    def set(self, name, data):
        self.__dict__[name] = data

    def setargs(self, args):
        self.args = args

    def done(self):
        if self.is_alive == False:
            return True
        return False

    def result(self):
        while self.done() == False:
            self.com_util.print_warn(f"waiting for ComThread return.")
        resultQueue = self.resultQueue
        self.resultQueue = []
        return resultQueue
