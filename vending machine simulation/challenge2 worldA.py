# -*- coding: utf-8 -*-
import random
import math
import pandas as pd
import numpy as np
import os, sys
import time
start_time = time.time()
from scipy import stats


firstPrice = 1000
maximumPrice = 2000
priceChangeAmount = 100
startExpectRevenue = 12000
tippingPoint = 0.5

# customer property
totalPopulation = 500
# alpha = 0.45
# beta = 0.3
# delta = 0.08
trycount = 30

# worldList = [[0.5, 0, 0], [0.5, 0.4, 0], [0.5, 0.4, 0.3]]
scriptName = os.path.basename(os.path.realpath(sys.argv[0]))
RevenueDistributionPerWorld = []

alpha = 0.5
beta = 0.0
delta = 0.0
totRevenueList = []
for TRY in range(trycount):
    class Client:
        def __init__(self, index):
            self.index = index
            self.whetherPassOrNotLog = []
            self.buyLog = []
            self.buyProbabilityLog = []

        def get_state(self):
            state = [self.index,
                     self.whetherPassOrNotLog,
                     self.buyLog,
                     self.buyProbabilityLog]
            return state

        def action(self, t, vm):
            self.whetherPassOrNotLog.append(self.pass_or_not(t.weather))

            if self.whetherPassOrNotLog[-1] == 1:  # 지나갔을 때만 살 것이므로
                self.buyLog.append(
                    self.buy_or_not(vm.priceLog[-1], vm.totalBuyCountLog[-1], t.weather * totalPopulation))
                vm.pass_one()  # 만약 이 함수가 if문 이전에 실행되었다면 자기까지 포함해서 지나간 사람이 구매 확률에 계산될 것이다. 이는 모방효과에 왜곡을 불러옴.
                if self.buyLog[-1] == 1:  # 주의 요함. 무조건 지나갔다고 샀을리 없으니.
                    vm.buy_one()
            else:
                self.buyLog.append(0)
                self.buyProbabilityLog.append(0)  # true인 경우엔 이미 함수상에서 미리 로그가 기록되도록 함. 대칭이 아니라 보기 안좋지만 일단 넘어간다.

        def pass_or_not(self, weather):
            if random.random() < weather:
                return 1
            else:
                return 0

        def buy_or_not(self, price, n, N):  # 확률식은 초기조건 시트에 명시된 i일차 개인별 구매확률이 아닌 ppt를 따름. 단 감마라고 적힌 부분은 시트에 따라 delta로 대체
            # 1. 과제 설명할 땐 그날 지나다닌 사람의 수를 합한 값을 넣었지만 그것은 후행하는 정보이기 때문에 말이 되지 않으므로, 우선 이제까지 다닌 사람의 수만 카운팅하여 분모로 넣는다.
            # 2. 해봤는데 0으로 나누게 되는 일이 생겨버린다. 따라서 전날 총 구매인원을 대신 넣는다.
            # 3. 0일차에 전날 총 구매인원 값이 존재하지 않으므로 2는 틀렸다. 일단 추후에 더 좋은 모방효과를 나타낼 식을 떠올리고 대안으로 지나다닐 사람 수 기대값을 넣는다.
            buy_prob = (1 - (price / 2000)) * (alpha
                                               + beta * (n / N)
                                               + delta * ((math.exp(-math.exp(-0.15 * (sum(self.buyLog) - 5)))) - 0.12))
            # 구매 회수 m은 구매기록의 값을 모두 더한 값으로 한다.
            self.buyProbabilityLog.append(buy_prob)
            if random.random() < buy_prob:
                return 1
            else:
                return 0


    clientList = []


    class VendingMachine:
        def __init__(self, expect_revenue):
            self.date = []
            self.priceLog = []
            self.ExpectRevenue = expect_revenue  # 최초 예시에선 2일차에만 유용. 현재 예제에선 무의미함.
            self.totalBuyCountLog = []
            self.revenueLog = []
            self.passPopulationLog = []  # 각 날짜별 지나다닌 사람의 수.

        def price_decision(self):
            # if self.date[-1] == 0:
            self.priceLog.append(firstPrice)
            # elif self.date[-1] == 1:
            #     if self.ExpectRevenue < self.revenueLog[-1]:  # 기대한것 보다 많이 벌면
            #         self.priceLog.append(self.priceLog[-1] + priceChangeAmount)
            #     else:
            #         self.priceLog.append(self.priceLog[-1] - priceChangeAmount)
            # else:
            #     if self.revenueLog[-1] < self.revenueLog[-2]:  # 가장 최근 매출이 바로 전날보다 적은 경우
            #         self.priceLog.append(self.priceLog[-1] + priceChangeAmount)
            #     else:
            #         self.priceLog.append(self.priceLog[-1] - priceChangeAmount)

        def settlement_of_accounts(self):  # 매출액 정산.
            return self.revenueLog.append(self.priceLog[-1] * self.totalBuyCountLog[-1])

        def pass_one(self):
            self.passPopulationLog[-1] = self.passPopulationLog[-1] + 1

        def buy_one(self):
            self.totalBuyCountLog[-1] = self.totalBuyCountLog[-1] + 1

        def get_state(self):
            return self.date, \
                   self.priceLog, \
                   self.totalBuyCountLog, \
                   self.revenueLog, \
                   self.passPopulationLog  # 각 날짜별 지나다닌 사람의 수.

        def evaluation(self):
            return 0


    vm = VendingMachine(startExpectRevenue)


    class Env:  # only god know this param
        def __init__(self, date):
            self.date = date
            self.weather = random.random()


    for index in range(totalPopulation):  # client generate
        client = Client(index)
        clientList.append(client)

    vmMonitor = pd.DataFrame(columns=['일수',
                                      'n 일차 가격',
                                      'n 일차 날씨',
                                      'n 일차 지나갈 사람수 기대값',
                                      'n 일차 지나간 사람수',
                                      'n 일차 구매횟수',
                                      'n 일차 매출'])
    writer = pd.ExcelWriter(scriptName+" Log try " + str(TRY) + ".xlsx")
    for date in range(30):  # from 0 to 29
        # print("day ", date)
        t = Env(date)
        vm.date.append(date)
        vm.price_decision()
        vm.passPopulationLog.append(0)
        vm.totalBuyCountLog.append(0)

        dayMonitor = pd.DataFrame(columns=['사람',
                                           '지나감 여부',
                                           '구매여부',
                                           '개인 누적 구매회수 m',
                                           '하루 인구 누적 구매횟수(n)',
                                           '개인별 구매확률'])

        for index in range(len(clientList)):
            client = clientList[index]
            presentBuyCount = vm.totalBuyCountLog[-1]
            # print("presentBuyCount ", presentBuyCount)

            client.action(t, vm)
            dayMonitor.loc[index] = [client.index,
                                     client.whetherPassOrNotLog[-1],
                                     client.buyLog[-1],
                                     sum(client.buyLog),  # 이렇게 하면 엑셀과 달리 그날까지 포함한 누적 구매량이 출력됨.
                                     # lambda x: sum(client.buyLog) if client.buyLog[-1] == 0 else sum(client.buyLog)-1,
                                     presentBuyCount,
                                     client.buyProbabilityLog[-1]]
            # print("index : ", client.index)
            # print(client.whetherPassOrNotLog, "\n", client.buyLog, "\n", client.buyProbabilityLog)

        dayMonitor.to_excel(writer, sheet_name='day ' + str(date), encoding='euc-kr')

        # dayMonitor.to_csv("day "+str(date)+" client Log.csv", encoding='euc-kr')
        vm.settlement_of_accounts()

        vmMonitor.loc[date] = [str(date) + "일차",
                               vm.priceLog[-1],
                               t.weather,
                               t.weather * totalPopulation,
                               vm.passPopulationLog[-1],
                               vm.totalBuyCountLog[-1],
                               vm.revenueLog[-1]]
        # print(vm.get_state())

    totalSummation = ['총합',
                      np.sum(vm.priceLog),
                      np.sum(vmMonitor['n 일차 날씨'].values),
                      np.sum(vmMonitor['n 일차 지나갈 사람수 기대값'].values),
                      np.sum(vmMonitor['n 일차 지나간 사람수'].values),
                      np.sum(vmMonitor['n 일차 구매횟수'].values),
                      np.sum(vmMonitor['n 일차 매출'].values)]
    totRevenueList.append(np.sum(vmMonitor['n 일차 매출'].values))
    averageEval = ['평균',
                   np.mean(vm.priceLog),
                   np.mean(vmMonitor['n 일차 날씨'].values),
                   np.mean(vmMonitor['n 일차 지나갈 사람수 기대값'].values),
                   np.mean(vmMonitor['n 일차 지나간 사람수'].values),
                   np.mean(vmMonitor['n 일차 구매횟수'].values),
                   np.mean(vmMonitor['n 일차 매출'].values)]
    varianceEval = ['분산',
                    np.var(vm.priceLog),
                    np.var(vmMonitor['n 일차 날씨'].values),
                    np.var(vmMonitor['n 일차 지나갈 사람수 기대값'].values),
                    np.var(vmMonitor['n 일차 지나간 사람수'].values),
                    np.var(vmMonitor['n 일차 구매횟수'].values),
                    np.var(vmMonitor['n 일차 매출'].values)]
    vmMonitor.loc[date + 1] = totalSummation
    vmMonitor.loc[date + 2] = averageEval
    vmMonitor.loc[date + 3] = varianceEval
    vmMonitor.to_excel(writer, sheet_name='종합', encoding='euc-kr')
    # vmMonitor.to_csv("vending machine Log.csv", encoding='euc-kr')
    writer.save()
RevenueDistributionPerWorld.append(totRevenueList)

m, s = divmod((time.time() - start_time), 60)
print("almost %d minute" % m)
### evaluation ###
# revenueMatrix = np.array(RevenueDistributionPerWorld)
# 모든 조합으로 독립표본 t-test 실시.
# 각 월드의 모델 당 30회 이상 관측 되었으므로 정규성이 만족.
# 참고 http://www.dodomira.com/2016/04/02/r%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%9C-t-test/


def equ_var_test_and_unpaired_t_test(x1, x2):
    # 등분산성 확인. 가장 기본적인 방법은 F분포를 사용하는 것이지만 실무에서는 이보다 더 성능이 좋은 bartlett, fligner, levene 방법을 주로 사용.
    # https://datascienceschool.net/view-notebook/14bde0cc05514b2cae2088805ef9ed52/
    if stats.bartlett(x1, x2).pvalue < 0.05:
        tTestResult = stats.ttest_ind(x1, x2, equal_var=True)
        print("The t-statistic and p-value assuming equal variances is %.3f and %.3f." % tTestResult)
        # 출처: http: // thenotes.tistory.com / entry / Ttest - in -python[NOTES]
        if tTestResult.pvalue < 0.05:
            compare_mean(x1, x2)
        else:
            print("two sample mean is same h0 not rejected")
    else:
        tTestResult = stats.ttest_ind(x1, x2, equal_var=False)  # 등분산이 아니므로 Welch’s t-test
        print("The t-statistic and p-value not assuming equal variances is %.3f and %.3f" % tTestResult)
        # 출처: http: // thenotes.tistory.com / entry / Ttest - in -python[NOTES]
        if tTestResult.pvalue < 0.05:
            compare_mean(x1, x2)
        else:
            print("two sample mean is same h0 not rejected")


def compare_mean(x1, x2):
    mean1 = np.mean(x1)
    mean2 = np.mean(x2)
    print("mean of first  one is ", mean1)
    print("mean of second one is ", mean2)
    if mean1 < mean2:
        print("so mean2 is bigger")
    else:
        print("so mean1 is bigger")


worldA_before = [1419900,	332900,	1263400,	1152300,	1147300,	1137100,	563800,	1119000,	1401100,	959500,	1407500,	1231400,	1247800,	1288000,	748000,	1386400,	1360600,	1497400,	297600,	577600,	1666100,	1070900,	827600,	962000,	1353000,	1565600,	290200,	1227700,	1654500,	1243500]
# 손으로 일일이 계산한 결과 옮겨옴
RevenueDistributionPerWorld.append(worldA_before)
equ_var_test_and_unpaired_t_test(RevenueDistributionPerWorld[0], RevenueDistributionPerWorld[1])
