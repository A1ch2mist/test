'''
豪迈继保、昂立继保、被测设备通讯测试
'''
import CreatTest.Case as Case
import CreatTest.Solution as Solution
import CreatTest.EUT as EUT
import CreatTest.EUTResult as EUTResult
import CreatTest.Interface as Interface
import CreatTest.Comtrade as Comtrade
import CreatTest.HaoMaiRelayTestDataUI as HaoMaiRelayTestDataUI
import CreatTest.RelayTestDataUI as RelayTestDataUI

# 初始化接口变量
case = GetCurCase()		# 获取测试用例对象
solution = GetCurSln()	# 获取测试方案对象

interfaceTestItem = case.GetInterfaceByName('测试条目')
item = interfaceTestItem.GetTestItemByIndex(0)     	            # 功能测试条目

interfaceTable = case.GetInterfaceByName('通讯规约')
port = interfaceTable.GetTableCellValue(0, 0)       	        # 国网端口
protocol = interfaceTable.GetTableCellValue(0, 1)   	        # 国网协议

interfaceTable = case.GetInterfaceByName('测试连接状态')
relayTest = interfaceTable.GetTableCellValue(0, 0)
eutTest = interfaceTable.GetTableCellValue(0, 1)


# 功能：设备连接。对一台样品：配置端口、连接、初始化
# 参数：EUT试品
# 返回：True，初始化完成；False，连接失败
def linkEut(eut, port, protocol):
	name = eut.GetName()

	# 配置样品端口与协议
	if not eut.SetComm(port, protocol):
		OutputLog(f'[{name}]  配置端口 {port} 和协议 {protocol} 失败')
		return False

	# 启动样品
	if not eut.Start():
		OutputLog(f'[{name}]  启动失败')
		return False

	# 样品链路初始化
	if not eut.LinkInitial():
		eut.Stop()
		OutputLog(f'[{name}]  链路初始化失败')
		return False

	OutputLog(f'[{name}]  初始化完成')
	return True


# 试验结束，断开设备连接
def stopEut(eut):
	eut.Stop()  # 样品结束运行


# 功能：继保仪连接
# 返回：True，初始化完成；False，连接失败
def linkRelay(relay):
	if not relay.Connect():
		return False
	return True


# 试验结束，断开继保仪连接
def stopRelay(relay):
	relay.StopTest()  # 继保仪结束运行
	relay.Disconnect()  # 与继保仪断开链接

# 创建继保仪序列
def HaoMaiTestData():
	testData = HaoMaiRelayTestDataUI.HaoMaiRelayTestDataUI()
	return testData

# 创建继保仪电压电流状态
def OnllyTestData():
	testData = RelayTestDataUI.RelayTestDataUI()
	return testData

# 连接所有测试样品和继保仪
# 返回：True，初始化完成；False，连接失败
def linkAllEutRelay():
	isOk = True

	# 连接所有设备
	if eutTest ==1:
		error = 0
		for eut in eut_list:
			OutputLog(f'[{eut.GetName()}]  建立连接')
			if not linkEut(eut, port, protocol):
				OutputLog(f'[{eut.GetName()}]  建立连接失败')
				isOk = False
				error += 1
			else:
				OutputLog(f'[{eut.GetName()}]  建立连接成功')

		count = len(eut_list)
		correct = count-error
		OutputLog(f'样品共{count}台。连接成功{correct}台，连接失败{error}台。')
		OutputLog(f'')

	# 如果需要用到继保仪，则建立连接
	if relayTest ==1:
		testDateList = [HaoMaiTestData(),OnllyTestData()]
		error = 0
		for relay in relay_list:
			OutputLog(f'[{relay.GetName()}]  建立连接')
			if not linkRelay(relay):
				OutputLog(f'[{relay.GetName()}]  建立连接失败')
				isOk = False
				error += 1
			else:
				OutputLog(f'[{relay.GetName()}]  建立连接成功')
				_i = 0
				for testData in testDateList:
					relay.SetTestData(testData) # 设置继保仪试验
					if not relay.StartTest():  # 启动继保仪试验
						_i += 1
					else:
						OutputLog(f'[{relay.GetName()}]  启动试验成功')
						break
					if _i == len(testDateList):
						OutputLog(f'[{relay.GetName()}]  启动试验失败')
						isOk = False
						break

		count = len(relay_list)
		OutputLog(f'继保仪共{count}台。连接成功{count-error}台，连接失败{error}台。')
		OutputLog(f'')

	return isOk

# 断开所有测试样品和继保仪
def stopAllEutRelay():
	if eutTest ==1:
		for eut in eut_list:
			OutputLog(f'[{eut.GetName()}]  断开连接')
			stopEut(eut)

	if relayTest ==1:
		for relay in relay_list:
			OutputLog(f'[{relay.GetName()}]  断开连接')
			stopRelay(relay)


# 功能：输出试验结果
# 参数：eutTest=试验对象
def saveResult(eut,result):
	eutResult = case.CreateEUTResult(eut, item)
	if result:
		eutResult.SetStateSuccess()
		eutResult.GetOutputParm(0).SetValue(f'所有设备或继保仪连接成功')
		OutputLog(f'所有设备或继保仪连接成功')
	else:
		eutResult.SetStateFail()
		eutResult.GetOutputParm(0).SetValue(f'存在设备或继保仪连接失败')
		OutputLog(f'存在设备或继保仪连接失败')
	case.PushEUTResult(eutResult)

#--------------------------------------------------------------------- #
# 开始试验
#--------------------------------------------------------------------- #
# 创建relay测试对象
relay_list = []
relayCount = solution.GetEnableRelayCount()
for count in range(relayCount):
	relay = solution.GetEnableRelayByIndex(count)
	relay_list.append(relay)

# 创建eut测试对象
eut_list = []
eutCount = solution.GetEnableEUTCount()
for count in range(eutCount):
	eut = solution.GetEnableEUTByIndex(count)
	eut_list.append(eut)

# 连接设备或继保仪
result = linkAllEutRelay()
stopAllEutRelay()

# 结果输出
if len(eut_list)>=1:
	saveResult(eut_list[0],result)