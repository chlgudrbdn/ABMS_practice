

import numpy as np
import math
import random
import scipy
from scipy.stats import poisson
from scipy.stats import expon

# np.random.seed(seed=42)
start = 0
end = 1000
# rand_pois = np.random.poisson(lam=2., size=end)
# # 출처: http://rfriend.tistory.com/284 [R, Python 분석과 프로그래밍 (by R Friend)]
# print(rand_pois)

# for num in range(end):
#     if num == 0:
#         arrival_time.append(0)
#         continue
#     arrival_time[num] = rand_pois[num-1]+rand_pois[num]
#     print(num, " : ", arrival_time)
Lambda = 2
Mu = 3
Arrival_time = []
Service_time = []
for i in range(end):
    timeGap = -math.log(random.random()) * (1/Lambda)
    serviceGap = -math.log(random.random()) * (1/Mu)
    # https://stackoverflow.com/questions/25098197/simulate-arival-times-in-a-poisson-process
    # print("timeGap", timeGap)
    if i == start:
        Arrival_time.append(timeGap)
        Service_time.append(serviceGap)
        continue
    Arrival_time.append(Arrival_time[-1] + timeGap)
    Service_time.append(Service_time[-1] + serviceGap)
# print(arrival_time)


class Client:
    def __init__(self, clientNum):
        self.clientNum = clientNum
        self.arrival_time = Arrival_time[clientNum]
        self.service_time = Service_time[clientNum]
        self.server_choice = 1
        self.waitTime = 0.0
        self.startTime = 0.0
        self.endTime = 0.0
        self.totalSpendTime=0.0

    def setNum(self, num):
        self.clientNum = num

    def getNum(self):
        return self.clientNum

    def setArrival_time(self, num):
        self.arrival_time = Arrival_time[num]

    def getArrival_time(self):
        return self.arrival_time

    def setServerChoice(self, num):
        self.server_choice = num

    def getServerChoice(self):
        return self.server_choice

    def setwaitTime(self, num):
        self.waitTime = num

    def getwaitTime(self):
        return self.waitTime

    def setstartTime(self, num):
        self.startTime = num

    def getstartTime(self):
        return self.waitTime

    def setendTime(self, num):
        self.endTime = num

    def getendTime(self):
        return self.endTime

    def choose_server(self):
        print(len(server1.getQueue()), ", ", len(server2.getQueue()))

        if len(server1.getQueue()) <= len(server2.getQueue()):
            self.setServerChoice(1)
            server1.setQueue(self)
            server1.setServicetime(self.service_time)

        else:
            self.setServerChoice(2)
            server2.setQueue(self)
            server2.setServicetime(self.service_time)

    def get_state(self):
        print(self.clientNum, self.arrival_time, self.service_time, self.server_choice, self.waitTime, self.startTime, self.endTime, self.totalSpendTime, sep='\t')

class Server:
    def __init__(self, ServerNum):
        self.ServerNum = ServerNum
        self.Queue = []
        self.ServiceTimePerClient = []

    def getQueue(self):
        return self.Queue

    def setQueue(self, client):
        self.Queue.append(client)

    def getServicetime(self):
        print(self.ServiceTimePerClient)
        return self.ServiceTimePerClient

    def setServicetime(self, servicetime):
        self.ServiceTimePerClient.append(servicetime)


server1 = Server(1)
server2 = Server(2)


def server_reference(num):
    if num == 1:
        return server1
    else:
        return server2
client_list = []

def client_reference(num):
    client_list.index(num)


for clientNum in range(end):  # event generate
    client = Client(clientNum)
    client.choose_server()
    if len(client_list) == 0:
        # client.setWatingTime(last_time - client.getArrival_time())
        client.setstartTime(client.getArrival_time())
        client.setendTime(client.getArrival_time() + client.service_time )
        client.totalSpendTime = client.service_time
        client_list.append(client)
        client.get_state()
        continue

    if client.getArrival_time() < client.getServerChoice().getQueue()[-1].getendTime() :
        last_time = server_reference(client.getServerChoice()).getQueue()[-1].getendTime()
        print("last serviec time : ", last_time)
        client.setWatingTime(last_time - client.getArrival_time())
        client.setstartTime(last_time)
        client.setendTime(last_time + client.service_time)
        client.totalSpendTime = client.endTime + client.startTime
    else:
        # client.setWatingTime 은 생략.
        client.setstartTime(client.getArrival_time())
        client.setendTime(client.getArrival_time() - client.service_time)
        client.totalSpendTime = client.endTime + client.startTime
    client.get_state()
    client_list.append(client)

print("clientNum", "arrival_time", "service_time", "server_choice", "waitTime", "startTime", "endTime", "totalSpendTime", sep='\t')

for client in client_list:  # event generate
    client.get_state()

"""
"""
