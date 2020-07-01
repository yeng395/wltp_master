from minizinc import Instance, Model, Solver, CLI
import os

class MiniZincModel:

    def __init__(self, model, solver, datafile, modelfile):
        model.add_file(datafile, True)
        model.add_file(modelfile, True)
        self.mod = model
        self.sol = solver
        self.ins = CLI.CLIInstance(solver, model)

    def getresults(self):
        result = self.ins.solve()
        return result

    def getdatainput(self, data):
        d = {}
        for x in data:
            d[x] = self.mod.__getitem__(x)
        return d

    def getdecisionvariable(self, decision, result):
        d = {}
        for x in decision:
            d[x] = result[x]
        return d

    def getRestrictionsProduce(self, maxProduction, produce, productionPlan, demand_per_Product, excessdemand):
        produceRestriction_1 = [[0 for x in range(0, len(produce[0]))] for y in range(0, len(produce))]
        produceRestriction_2 = [[0 for x in range(0, len(produce[0]))] for y in range(0, len(produce))]
        produceRestriction_final = [[0 for x in range(0, len(produce[0]))] for y in range(0, len(produce))]
        produceRestriction_final_perProduct = [0 for x in range(0, len(produce[0]))]
        produceRestriction_final_perProduct_Constraint = ['' for x in range(0, len(produce[0]))]
        otherproduce = [0 for x in range(0, len(produce[0]))]
        for i in range(0, len(produce)):
            for j in range(0, len(produce[i])):
                for l in range(0, len(produce[i])):
                    if j != l:
                        otherproduce[j] += produce[i][l] * productionPlan[i][j]

                if (maxProduction[i] * productionPlan[i][j]) - otherproduce[j] > (round(demand_per_Product[j]* excessdemand[j] * productionPlan[i][j] + 0.5)):
                    produceRestriction_final[i][j] = (round(demand_per_Product[j]* excessdemand[j] * productionPlan[i][j]))
                    produceRestriction_final_perProduct_Constraint[j] = "Excess Demand"
                else:
                    if (maxProduction[i] * productionPlan[i][j]) - otherproduce[j] <= 0:
                        produceRestriction_final[i][j] = 0
                        produceRestriction_1[i][j] = 0
                    else:
                        produceRestriction_final[i][j] = (maxProduction[i] * productionPlan[i][j]) - otherproduce[j]
                        produceRestriction_final_perProduct_Constraint[j] = "Max Production"
                produceRestriction_1[i][j] = (maxProduction[i] * productionPlan[i][j]) - otherproduce[j]
                produceRestriction_2[i][j] = (round(demand_per_Product[j]* excessdemand[j] * productionPlan[i][j]))
                produceRestriction_final_perProduct[j] += produceRestriction_final[i][j]

        return  produceRestriction_final_perProduct, produceRestriction_final_perProduct_Constraint


    def getRestrictionsDelivery(self, produceRestriction_final_perProduct, delivered, demand, productionPlan):
        demandothers = [[[0 for x in range(0, len(delivered[0][0]))] for y in range(0, len(delivered[0]))] for z in range(0, len(delivered))]
        deliveredRestriction_final = [[[0 for x in range(0, len(delivered[0][0]))] for y in range(0, len(delivered[0]))] for z in range(0, len(delivered))]
        for i in range(0, len(delivered)):
            for j in range(0, len(delivered[i])):
                for k in range(0, len(delivered[i])):
                    for l in range(0, len(delivered[i][j])):
                        if j != k:
                             demandothers[i][j][l] += demand[k][l] * productionPlan[i][l]

                        deliveredRestriction_final[i][j][l] = (produceRestriction_final_perProduct[l] - demandothers[i][j][l])  * productionPlan[i][l]

        return  deliveredRestriction_final


def getFinePerProduct(soldCars, emissionWLTP, emission, emissionRealFine):
    finePerProduct = [0 for x in range(0, len(soldCars))]
    finePerSingleCar = [0 for x in range(0, len(soldCars))]
    for i in range(0, len(soldCars)):
        finePerProduct[i] = (emissionRealFine/ (emission/ 100)) * emissionWLTP[i] * soldCars[i]
        finePerSingleCar[i] = (emissionRealFine / (emission / 100)) * emissionWLTP[i]

    return  finePerProduct, finePerSingleCar

def getSavingandFine(soldCars, sold, emissionlimit, emissionWLTP, payperfine, emission, emissionRealFine, supercredit):
    finePerSingleCar = [0 for x in range(0, len(soldCars))]
    emissionFine_without_supercredit = (((emission/100) / sold) - emissionlimit) * payperfine * sold
    emissionFine_Per_g_Co2 = (emissionFine_without_supercredit / (emission/ 100))
    diff_emission = emissionFine_without_supercredit - emissionRealFine
    supercreditCars = 0
    for i in range(0, len(soldCars)):
        if supercredit[i] > 100:
            supercreditCars = supercreditCars + soldCars[i]
            finePerSingleCar[i] = 0

    for i in range(0, len(soldCars)):
        if supercredit[i] <= 100:
            finePerSingleCar[i] = emissionFine_Per_g_Co2 * emissionWLTP[i]

    return diff_emission, finePerSingleCar, emissionFine_without_supercredit

def getoptimumChangePerProductPos(r, d):
    newtotalSales_1 = [0 for x in range(0, len(r['soldCars']))]
    newtotalSales_10 = [0 for x in range(0, len(r['soldCars']))]
    newemission_1 = [0 for x in range(0, len(r['soldCars']))]
    newemission_10 = [0 for x in range(0, len(r['soldCars']))]
    new_wltpavg_1 = [0 for x in range(0, len(r['soldCars']))]
    new_change_optimum_1 = [0 for x in range(0, len(r['soldCars']))]
    emission_limit_new_1 = [0 for x in range(0, len(r['soldCars']))]
    ebMax = [0 for x in range(0, len(r['soldCars']))]
    for i in range(0, len(d['eb'][0])):
        ebMax[i] = d['eb'][0][i]
        for c in range(1, len(d['eb'])):
            if(ebMax[i] <= d['eb'][c][i]):
                ebMax[i] = d['eb'][c][i]

    for i in range(0, len(r['soldCars'])):
        totalweight_new_1= r['totalweight'] + (10 * d['weight'][i])
        avg_weight_new_1 = totalweight_new_1/ (r['sold'] + 10)
        emission_limit_new_1[i] = (d['payperfine'] + (0.0333 * (avg_weight_new_1-1380)))
        newtotalSales_1[i] = r['totalSales'] + ebMax[i] * 10
        newemission_1[i] = r['emission'] + (d['emissionWLTP'][i] * 100 * 10)
        new_CarsforWltp_supercredit = (r['carsforWLTP_supercredit'] + (10 * d['supercredit'][i]))
        new_wltpavg_1[i] = newemission_1[i] / new_CarsforWltp_supercredit
        new_emisssionFine = (new_wltpavg_1[i] - emission_limit_new_1[i]) * d['payperfine'] * (r['sold'] + 10)

        new_change_optimum_1[i] = (newtotalSales_1[i] - new_emisssionFine) - r['total']

    return new_change_optimum_1

def getoptimumChangePerProductNeg(r, d):
    newtotalSales_1 = [0 for x in range(0, len(r['soldCars']))]
    newtotalSales_10 = [0 for x in range(0, len(r['soldCars']))]
    newemission_1 = [0 for x in range(0, len(r['soldCars']))]
    newemission_10 = [0 for x in range(0, len(r['soldCars']))]
    new_wltpavg_1 = [0 for x in range(0, len(r['soldCars']))]
    new_change_optimum_1 = [0 for x in range(0, len(r['soldCars']))]
    emission_limit_new_1 = [0 for x in range(0, len(r['soldCars']))]
    ebMax = [0 for x in range(0, len(r['soldCars']))]
    for i in range(0, len(d['eb'][0])):
        ebMax[i] = d['eb'][0][i]
        for c in range(1, len(d['eb'])):
            if(ebMax[i] <= d['eb'][c][i]):
                ebMax[i] = d['eb'][c][i]

    for i in range(0, len(r['soldCars'])):
        totalweight_new_1= r['totalweight'] - (d['weight'][i] * 10)
        avg_weight_new_1 = totalweight_new_1/ (r['sold'] - 10)
        emission_limit_new_1[i] = (d['payperfine'] + (0.0333 * (avg_weight_new_1-1380)))
        newtotalSales_1[i] = r['totalSales'] - ebMax[i] * 10
        newemission_1[i] = r['emission'] - (d['emissionWLTP'][i] * 100 * 10)
        new_CarsforWltp_supercredit = (r['carsforWLTP_supercredit'] - (d['supercredit'][i]) * 10)
        new_wltpavg_1[i] = newemission_1[i] / new_CarsforWltp_supercredit
        new_emisssionFine = (new_wltpavg_1[i] - emission_limit_new_1[i]) * d['payperfine'] * (r['sold'] - 10)

        new_change_optimum_1[i] = (newtotalSales_1[i] - new_emisssionFine) - r['total']

    return new_change_optimum_1

def saveDataFile(data, name_file):
    d = data
    save_path = '/Users/Yannick/Documents/Uni Augsburg/Git/untitled/app/DataFiles/'
    name_of_file = name_file
    completeName = os.path.join(save_path, name_of_file+".dzn")

    f = open(completeName, "w")
    for y in ['pname', 'cname', 'sname']:
        f.write(y + " = [")
        for x in range(0, len(d[y])):
            if x == len(d[y]) - 1:
                f.write("\"" + d[y][x] + "\"];")
            else:
                f.write("\"" + d[y][x] + "\", " )
        f.write("\n")

    for y in ['weight', 'supercredit', 'emissionWLTP', 'excessdemand', 'maxProduction']:
        f.write(y + " = [")
        for x in range(0, len(d[y])):
            if x == len(d[y]) - 1:
                f.write(str(d[y][x]) + "];")
            else:
                f.write(str(d[y][x]) + ", " )
        f.write("\n")

    for y in ['eb', 'productionPlan', 'demand']:
        f.write(y + " = ")
        for x in range(0, len(d[y])):
            for z in range(0, len(d[y][x])):
                if x == 0:
                    if z == 0:
                        f.write("[|" + str(d[y][x][z]) + ", ")
                if z == 0:
                    if x != 0:
                        f.write("|" + str(d[y][x][z]) + ", ")
                if z != 0 and x != len(d[y]) - 1:
                   f.write(str(d[y][x][z]) + ", ")
                if z != 0 and x == len(d[y]) - 1 and z!= len(d[y][x]) - 1:
                   f.write(str(d[y][x][z]) + ", ")
                if x == len(d[y]) - 1 and z == len(d[y][x]) - 1:
                    f.write(str(d[y][x][z]) + " |]; ")
            f.write("\n")

    for y in ['payperfine', 'nproducts', 'nsites', 'ncustomers']:
        f.write(y + " = " + str(d[y]) + ";")
        f.write("\n")

    f.close()

#
# #
# #

# option=1
# option2=2
#
# modelfile_final = "/Users/Yannick/Documents/Uni Augsburg/Git/untitled/app/" \
#                       "MiniZincFiles/Vertriebsplanung_10.mzn"
#
# datafile1 = "/Users/Yannick/Documents/Uni Augsburg/Git/untitled/app/" \
#                 "DataFiles/t.dzn"
#
# dataList_final = {'nproducts', 'nsites', 'ncustomers', 'eb', 'weight', 'pname', 'sname', 'cname', 'productionPlan',
#                       'supercredit', 'demand', 'maxProduction',
#                       'emissionWLTP', 'payperfine', 'excessdemand'}
#
# decisionList_final = {"delivered", "produce", "emissionPerCar", "soldCars", "sold", "total", "wltpavg",
#                           "emissionRealFine", 'emission', "totalweight",
#                           "emissionlimit", "avgweight", "totalSales", "demand_per_Product", "totalSales_perProduct", "carsforWLTP_supercredit"}
#
# modelfile = modelfile_final
#
# data: str = datafile1
#
# couenne = "couenne"
#
# model = Model()
# solver = Solver.lookup(couenne)
# mini = MiniZincModel(model, solver, modelfile, datafile1)
# result = mini.getresults()
# dataList = dataList_final
# decision = decisionList_final
# optionList_final = ['option1', 'option2']
# d = mini.getdatainput(dataList)
# r = mini.getdecisionvariable(decision, result)
# inputdata = {}
# inputdata['option1'] = d
# # a,b = getFinePerProduct(r['soldCars'], d['emissionWLTP'], r['emission'], r['emissionRealFine'])
# # print(a)
# # print(b)
# #c,d,e = getSavingandFine(r['soldCars'], r['sold'], r['emissionlimit'], d['emissionWLTP'], d['payperfine'], r['emission'], r['emissionRealFine'], d['supercredit'])
# #print(c)
# #print(d)
# #print(e)
# # k = getoptimumChangePerProductPos(r,d)
# # print(k)
# # l = getoptimumChangePerProductNeg(r,d)
# # print(l)
#
#
#
#
# x,y = getRestrictionsProduce(d['maxProduction'] , r['produce'], d['productionPlan'], r['demand_per_Product'], d['excessdemand'])
# print(x,y)

