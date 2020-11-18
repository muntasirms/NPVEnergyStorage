# each line represents a single unit
# each point of a line is a simulated day with randomized parameters
# we are looking to see each percentile's profit after a given amount of simulated days of multiple simulated units
# this is a tool for powell--so keep things easy to change--variables at the top and clearly labeled, code commented and understandable
# model lithium ion and thermal as you guys found--maybe find a more competitive efficiency for thermal online
# you can use peak and trough pricing as a generalized model--but how can you simulate changes in price?
#currently assuming 0% equity


import random
import numpy as np
import matplotlib.pyplot as mtplt
import seaborn as sns
import payulator



maxPeakPrice = .11  # Maximum peak price ($/kWh)
minPeakPrice = .0672  # Minimum peak price ($/kWh)

maxTroughPrice = .03  # Maximum trough price ($/kWh)
minTroughPrice = .01  # Minimum trough price ($/kWh)

maxStorageTime = 5  # Maximum amount of time energy will be stored for
minStorageTime = 3  # Minimum amount of time energy will be stored for

isThermal = False  # If thermal storage is being modeled, set to True. For all other technologies, set to False
capacity = 250000  # Storage capacity--amount of energy required to charge storage unit (kWh)
efficiency = .8  # Conversion efficiency of unit (0-1)
efficiencyLoss = .00037  # Percentage of total storage lost per hour
heatRecycling = .54  # Thermal only, proportion of lost heat recycled (0-1)

simulatedYears = 30  # The number of simulated years each unit will undergo--set as plant life and should be equivalent to storage technology lifetime assuming one cycle per day
numSimulations = 1000  # Number of units to be simulated. The more units, the more statistically accurate results

#Economic parameters

loanPeriod = 10                     #years
loanRate = .08
taxRate = .21
internalROR = .1
MACRSRates = [.1429,.2449,.1749,.1249,.0893,.0892,.0893,.0446]      #7 year MACRS depreciation period

#FCI--should we randomize cost factor ranges as well?

storageCost = 80                   #$/kWh
TDCFactor = .7                      #land = .05 TIC, buildings = .4, site development = .1, auxiliaries = .15,
IndirectFactor = .5                 #prorated expenses = .1, construction fees = .2, field expenses = .1, contingency = .1
TIC = storageCost*capacity          #$/kWh


FCI = TIC*(1+TDCFactor)*(1+IndirectFactor)+TIC*(1+TDCFactor)
print(FCI)

#operating cost parameters

workers = {'Plant Managers': 1, 'Plant Engineer': 2, 'Maintenance Supervisor': 1, 'Lab Manager': 0, 'Shift Supervisor': 1, 'Maintenance Tech': 2, 'Shift Operator': 3, 'Yard Worker': 1, 'Clerks and Secretaries': 1}
salary = {'Plant Managers': 176000, 'Plant Engineer': 83000, 'Maintenance Supervisor': 68000, 'Lab Manager': 67000, 'Shift Supervisor': 57000, 'Maintenance Tech': 47000, 'Shift Operator': 57000, 'Yard Worker': 33000, 'Clerks and Secretaries': 43000}
overhead = .9                       #90% overhead/maintenance of salaries
maintenance = .05                   #% of FCI per year



def simulatedYearProfit(maxPeakPrice, minPeakPrice, maxTroughPrice, minTroughPrice, maxStorageTime, minStorageTime,
                 isThermal, capacity, efficiency, efficiencyLoss, heatRecycling):

    annualProfit = 0

    for day in range(365):
        simPeakPrice = random.uniform(minPeakPrice, maxPeakPrice)
        simTroughPrice = random.uniform(minTroughPrice, maxTroughPrice)
        simStorageTime = random.uniform(minStorageTime, maxStorageTime)

        storageLoss = simStorageTime * efficiencyLoss * capacity
        chargeCost = simTroughPrice * capacity
        dischargeCost = simPeakPrice * efficiency * (capacity - storageLoss)

        if isThermal:
            heatRecycleProfit = (1 - efficiency) * capacity * heatRecycling * simPeakPrice
            annualProfit += dischargeCost - chargeCost + heatRecycleProfit

            # print(simPeakPrice,simTroughPrice)


        else:
            annualProfit += dischargeCost - chargeCost



    return annualProfit

def amortize(principal, interest, period, frequency):

    a = principal*(((interest/frequency)*(1+(interest/frequency))**(period*frequency)))/((1+(interest/frequency))**(period*frequency)-1)
    # print (a)
    return a


def cashFlow(year):
    #accounts for loan payment, operating (fixed and variable), and profit from sales

    preTax = 0
    loanTime = 0

    workerPay = 10

        # workers.get('Plant Manager') * salary.get('Plant Manager') + workers.get('Plant Engineer') * salary.get(
        # 'Plant Engineer') + workers.get('Maintenance Supervisor') * salary.get('Maintenance Supervisor') + workers.get(
        # 'Lab Manager') * salary.get('Lab Manager') + workers.get('Shift Supervisor') * salary.get(
        # 'Shift Supervisor') + workers.get('Maintenance Tech') * salary.get('Maintenance Tech') + workers.get(
        # 'Shift Operator') * salary.get('Shift Operator') + workers.get('Yard Worker') * salary.get(
        # 'Yard Worker') + workers.get('Clerks and Secretaries') * salary.get('Clerks and Secretaries')


    if (year <= loanPeriod):
        loanPayment = amortize(FCI,loanRate,loanPeriod,12)
        print(loanPayment)
    else:
        loanPayment = 0



    preTax = simulatedYearProfit(maxPeakPrice,minPeakPrice,maxTroughPrice,minTroughPrice,maxStorageTime,minStorageTime,isThermal,capacity,efficiency,efficiencyLoss,heatRecycling)-workerPay-(loanPayment*12)

    return preTax

def simulation():

    year = 0
    preTaxInc = []
    depr = []
    deprInc = []            #net revenue in DCFROR spreadsheets

    taxableInc = []
    taxedInc = []           #annual cash income, taxed income
    discountedInc = []
    simulation = []

    #calculate pretax cash flow and depreciation per year
    for years in range(simulatedYears):

        preTaxInc.append(cashFlow(years))
        if years <= 7:
            depr.append(FCI*MACRSRates[years])
        else:
            depr.append(0)

    #calculate depreciated income for each year, to calculate taxable income
    for years in range(simulatedYears):
        deprInc.append(preTaxInc[years]-depr[years])

    #calculate taxable income for each year
    taxableInc.append(deprInc[0])
    for years in range(1, simulatedYears):
        if(taxableInc[years-1] <=0 ):
            taxableInc.append(deprInc[years]+taxableInc[years-1])
        else:
            taxableInc.append(deprInc[years])

    #and finally calculate taxes
    for years in range(simulatedYears):
        if taxableInc[years] < 0:
            taxedInc.append(preTaxInc[years])
        else:
            taxedInc.append(preTaxInc[years]-(taxableInc[years] * taxRate))

    for years in range(simulatedYears):
        discountedInc.append(taxedInc[years]*(1/((1+internalROR)**years)))

    return discountedInc


def runSimulation(simulations):

    allSims = []

    for sim in range(simulations):
        allSims.append(simulation())

    return allSims

def NPV(simArray):

    NPVArray = []

    for sim in range(len(simArray)):
        tempNPV = 0

        for value in range(len(simArray[sim])):

            tempNPV += simArray[sim][value]

        NPVArray.append(tempNPV)

    return NPVArray

def storageUnitProfit(maxPeakPrice, minPeakPrice, maxTroughPrice, minTroughPrice, maxStorageTime, minStorageTime,
                 isThermal, capacity, efficiency, efficiencyLoss, heatRecycling, simDays):
    profitArray = []
    profitTotal = 0

    for x in range(simDays):
        profitTotal += simulatedYearProfit(maxPeakPrice, minPeakPrice, maxTroughPrice, minTroughPrice, maxStorageTime, minStorageTime,
                                    isThermal, capacity, efficiency, efficiencyLoss, heatRecycling)
        profitArray.append(profitTotal)

    return profitArray





def getChart():
    # maxPeakPrice = float(request.args.get('maxPeakPrice'))  # Maximum peak price ($/kWh)
    # minPeakPrice = float(request.args.get('minPeakPrice'))  # Minimum peak price ($/kWh)
    #
    # maxTroughPrice = float(request.args.get('maxTroughPrice'))  # Maximum trough price ($/kWh)
    # minTroughPrice = float(request.args.get('minTroughPrice'))  # Minimum trough price ($/kWh)
    #
    # maxStorageTime = float(request.args.get('maxStorageTime'))  # Maximum amount of time energy will be stored for
    # minStorageTime = float(request.args.get('minStorageTime'))  # Minimum amount of time energy will be stored for
    #
    # isThermal = True if request.args.get('isThermal')=="True" else False # If thermal storage is being modeled, set to True. For all other technologies, set to False
    # capacity = float(request.args.get('capacity'))  # Storage capacity--amount of energy required to charge storage unit (kWh)
    # efficiency = float(request.args.get('efficiency'))  # Conversion efficiency of unit (0-1)
    # efficiencyLoss = float(request.args.get('efficiencyLoss'))  # Proportion of total storage lost per hour
    # heatRecycling = float(request.args.get('heatRecycling'))  # Thermal only, proportion of lost heat recycled (0-1)
    #
    # simulatedDays = int(request.args.get('simulatedDays'))  # The number of simulated days each unit will undergo
    # numSimulations = int(request.args.get('numSimulations'))  # Number of units to be simulated. The more units, the more statistically accurate results

    yearArray = []

    for yrs in range(simulatedYears):
        yearArray.append(yrs+1)

    allUnits = runSimulation(numSimulations)

    for sim in range(numSimulations):
        mtplt.plot(yearArray, allUnits[sim])

    finalProfits = NPV(allUnits)

    # for simulation in range(len(allUnits)):
    #     finalProfits.append(allUnits[simulation][simulatedYears - 1])
    #     # print(allUnits[simulation][simulatedDays-1])

    ninetyPercentile = np.percentile(finalProfits, 90)
    tenPercentile = np.percentile(finalProfits, 10)
    median = np.median(finalProfits)

    print('Median: $' + str(round(median, 2)))
    print('90th Percentile: $' + str(round(ninetyPercentile, 2)))
    print('10th Percentile: $' + str(round(tenPercentile, 2)))

    if isThermal:
        mtplt.title('Monte Carlo Simulation of TES @' + str(efficiency * 100) + '% Efficiency, and ' + str(
            heatRecycling * 100) + '% Heat Recycling')
    else:
        mtplt.title('Monte Carlo Simulation of Energy Storage @' + str(efficiency * 100) + ' % Efficiency')

    mtplt.xlabel('Time (years)')
    mtplt.ylabel('Profit ($)')
    mtplt.draw()

    mtplt.figure()
    if isThermal:
        mtplt.title('Probability Density of TES Profits@' + str(efficiency * 100) + '% Efficiency, and ' + str(
            heatRecycling * 100) + '% Heat Recycling')
    else:
        mtplt.title('Probability Density of Energy Storage Profits @' + str(efficiency * 100) + '% Efficiency')

    sns.distplot(finalProfits, hist=False, kde=True, label='Probability Density')

    mtplt.xlabel('Profit ($)')
    mtplt.ylabel('Probability Density')

    mtplt.draw()

    mtplt.show()
    return "done"


getChart()