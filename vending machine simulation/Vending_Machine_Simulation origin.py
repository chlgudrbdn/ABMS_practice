import random

firstPrice = 300
priceChangeAmount = 100
startExpectRevenue = 12000
tippingPoint = 0.5

# customer property
totalPopulation = 500
alpha = 0.45
beta = 0.3
delta = 0.08


class Client:
    def __init__(self, index):
        self.index = index
        self.whetherPassOrNotLog = []
        self.buyLog = []
        self.buyProbabilityLog = []
        self.nCount = 0

    def action(self):
        return

    def getState(self):
        state = [self.index, ]
        return state


class VendingMachine:
    def __init__(self, ExpectRevenue, price):
        self.date = []
        self.price = []
        self.ExpectRevenue = ExpectRevenue  # 2일차에만 유용.
        self.totalBuyCount = []

    def priceDecision(self):
        if self.date[-1] == 1 :
            if self.ExpectRevenue < self.RealRevenue:
                self.price += priceChangeAmount
            else:
                self.price -= priceChangeAmount
        else:
            if self.totalBuyCount[-1]*self.totalBuyCount[-2]


    def getBeforePrice(self):
        return self.date[-1]


class Env:  # only god know this param
    def __init__(self, date):
        self.date = date
        self.weather = random.random()
        self.passPopulationThisDate = totalPopulation * self.weather


vm = VendingMachine(startExpectRevenue, firstPrice)

for index in range(totalPopulation):  # client generate
    client = Client(index)


for date in range(30): # from 0 to 29
    print("day ", date)






