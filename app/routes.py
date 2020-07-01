from app import app
from app import miniZinc
from app.forms import CalculateForm, EditForm, CreateForm, CreateNewForm
from flask import render_template, request, url_for, redirect, flash
from minizinc import Instance, Model, Solver, CLI
import os

colors = ['rgba(065, 105, 225, 0.5)','rgba(54, 162, 235, 0.5)','rgba(255, 206, 86, 0.5)',
               'rgba(75, 192, 192, 0.5)','rgba(153, 102, 255, 0.5)','rgba(255, 159, 64, 0.5)',
              'rgba(255, 127, 036, 0.5)','rgba(255, 048, 048, 0.5)', 'rgba(200, 048, 048, 0.5)',
          'rgba(240, 048,	048, 0.5)']

userdirectory ="/app/app/"

modelfile_final = userdirectory + "MiniZincFiles/Vertriebsplanung_10.mzn"

datafiles = []
datafiles_name = []
for root, dirs, files in os.walk(userdirectory +"DataFiles/"):
    for file in files:
        if file.endswith('.dzn'):
            datafile = str(root)+str(file)
            datafile_name = str(file)
            datafiles_name.append(datafile_name)
            datafiles.append(datafile)

datafiles_name.sort()
datafiles.sort()

def refreshDataFiles():
    datafiles_new = []
    datafiles_name_new= []
    for root, dirs, files in os.walk(userdirectory + "DataFiles/"):
        for file in files:
            if file.endswith('.dzn'):
                datafile = str(root) + str(file)
                datafile_name_new = str(file)
                datafiles_name_new.append(datafile_name_new)
                datafiles_new.append(datafile)

    datafiles_new.sort()
    datafiles_name_new.sort()
    return datafiles_new, datafiles_name_new


dataList_final = {'nproducts', 'nsites', 'ncustomers', 'eb', 'weight', 'pname', 'sname', 'cname', 'productionPlan',
            'supercredit', 'demand', 'maxProduction',
            'emissionWLTP', 'payperfine', 'excessdemand'}

decisionList_final = {"totalweight", "delivered", "produce", "emissionPerCar", "soldCars", "sold", "total", "wltpavg", "emissionRealFine",
            "emissionlimit", "avgweight", "totalSales", "demand_per_Product", "soldCarsPerSite", "carsforWLTP_supercredit", "totalSales_perCustomer", "totalSales_perProduct", "emission"}


@app.route('/', methods=['GET', 'POST'])
@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    form = CalculateForm()
    datafiles, datafiles_name = refreshDataFiles()
    form.option.choices = [(str(i), datafiles_name[i-1] + '  Scenario - ' + str(i)) for i in range(1, len(datafiles)+1)]
    form.option2.choices = [(str(i), datafiles_name[i-1] + '  Scenario - ' + str(i)) for i in range(1, len(datafiles)+1)]
    o1 = form.option.data
    o2 = form.option2.data
    if form.validate_on_submit():
        if 'show' in request.form:
            return redirect(url_for('calcandshow', option=o1, option2=o2))
        else:
            return redirect(url_for('index', option=o1, option2=o2))
    return render_template('calculate.html', title='Home', form=form)

@app.route('/createscenario_start', methods=['GET', 'POST'])
def createscenario_start():
    form = CreateForm()
    datafiles, datafiles_name = refreshDataFiles();
    form.option.choices = [(str(i), datafiles_name[i-1] + '  Scenario - ' + str(i)) for i in range(1, len(datafiles) + 1)]
    o1 = form.option.data
    if form.validate_on_submit():
        if 'create' in request.form:
            return redirect(url_for('createscenario_edit', title='Home', option=o1))
        elif 'createNew' in request.form:
            return redirect(url_for('createscenario_new'))
    return render_template('calculate.html', title='Home', form=form)

@app.route('/createscenario_new', methods=['GET', 'POST'])
def createscenario_new():
    if 'createNew1' in request.form:
        formvalues = request.form
        nproducts = 0
        nsites = 0
        ncustomers = 0
        for key in formvalues:
            if key.startswith('nproducts'):
                nproducts = int(request.form[key])

            if key.startswith('nsites'):
                nsites = int(request.form[key])

            if key.startswith('ncustomers'):
                ncustomers = int(request.form[key])

        return redirect(url_for('createscenario_new1', nsites=nsites, nproducts=nproducts, ncustomers=ncustomers ))

    return render_template('createscenario_new.html')


@app.route('/createscenario_new1/<nsites>/<nproducts>/<ncustomers>', methods=['GET', 'POST'])
def createscenario_new1(nsites, nproducts, ncustomers):
    nsites = int(nsites)
    nproducts = int(nproducts)
    ncustomers = int(ncustomers)
    if 'createNew2' in request.form:
        formvalues = request.form

        pname = ["" for x in range(0, int(nproducts))]
        for key in formvalues:
            for i in range(0, int(nproducts)):
                if key.startswith('pname_' + str(i)):
                    pname[i] = str(request.form[key])

        sname = ["" for x in range(0, int(nsites))]
        for key in formvalues:
            for i in range(0, int(nsites)):
                if key.startswith('sname_' + str(i)):
                    sname[i] = str(request.form[key])

        cname = ["" for x in range(0, int(ncustomers))]
        for key in formvalues:
            for i in range(0, int(ncustomers)):
                if key.startswith('cname_' + str(i)):
                    cname[i] = str(request.form[key])

        global pname_global
        global sname_global
        global cname_global

        global nproducts_global
        global nsites_global
        global ncustomers_global

        pname_global = pname
        cname_global = cname
        sname_global = sname
        nsites_global = int(nsites)
        nproducts_global = int(nproducts)
        ncustomers_global = int(ncustomers)

        return redirect(url_for('createscenario_new2'))

    return render_template('createscenario_new1.html', nsites=nsites, nproducts=nproducts, ncustomers=ncustomers)


@app.route('/createscenario_new2', methods=['GET', 'POST'])
def createscenario_new2():
    d = {}
    d['nproducts'] = nproducts_global
    d['nsites'] = nsites_global
    d['ncustomers'] = ncustomers_global
    d['pname'] = pname_global
    d['cname'] = cname_global
    d['sname'] = sname_global

    if 'saveData' in request.form:
        formvalues = request.form
        print(formvalues)

        for key in formvalues:
            if key.startswith('nameScenario'):
                nameScenario = str(request.form[key])

        eb = [[0 for x in range(0, d['nproducts'])] for y in range(0, d['ncustomers'])]
        for key in formvalues:
            for i in range(0, d['ncustomers']):
                for j in range(0, d['nproducts']):
                    if key.startswith('eb_' + str(i) + '_' + str(j)):
                        eb[i][j] = int(request.form[key])

        for key in formvalues:
            if key.startswith('payperfine'):
                payperfine = int(request.form[key])

        productionPlan = [[0 for x in range(0, d['nproducts'])] for y in range(0, d['nsites'])]
        for key in formvalues:
            for i in range(0, d['nsites']):
                for j in range(0, d['nproducts']):
                    if key.startswith('productionPlan_' + str(i) + '_' + str(j)):
                        productionPlan[i][j] = int(request.form[key])

        supercredit = [0 for x in range(0, d['nproducts'])]
        for key in formvalues:
            for i in range(0, d['nproducts']):
                if key.startswith('supercredit_' + str(i)):
                    supercredit[i] = float(request.form[key])
                    supercredit[i] = int(supercredit[i] * 100)

        demand = [[0 for x in range(0, d['nproducts'])] for y in range(0, d['ncustomers'])]
        for key in formvalues:
            for i in range(0, d['ncustomers']):
                for j in range(0, d['nproducts']):
                    if key.startswith('demand_' + str(i) + '_' + str(j)):
                        demand[i][j] = int(request.form[key])

        excessdemand = [0 for x in range(0, d['nproducts'])]
        for key in formvalues:
            for i in range(0, d['nproducts']):
                if key.startswith('excessdemand_' + str(i)):
                    excessdemand[i] = float(request.form[key])

        maxProduction = [0 for x in range(0, d['nsites'])]
        for key in formvalues:
            for i in range(0, d['nsites']):
                if key.startswith('maxProduction_' + str(i)):
                    maxProduction[i] = int(request.form[key])

        emissionWLTP = [0 for x in range(0, d['nproducts'])]
        for key in formvalues:
            for i in range(0, d['nproducts']):
                if key.startswith('emissionWLTP_' + str(i)):
                    emissionWLTP[i] = int(request.form[key])

        weight = [0 for x in range(0, d['nproducts'])]
        for key in formvalues:
            for i in range(0, d['nproducts']):
                if key.startswith('weight_' + str(i)):
                    weight[i] = int(request.form[key])



        saveData = {}
        saveData['nproducts'] = d['nproducts']
        saveData['nsites'] = d['nsites']
        saveData['ncustomers'] = d['ncustomers']
        saveData['maxProduction'] = maxProduction
        saveData['emissionWLTP'] = emissionWLTP
        saveData['weight'] = weight
        saveData['excessdemand'] = excessdemand
        saveData['supercredit'] = supercredit
        saveData['productionPlan'] = productionPlan
        saveData['payperfine'] = payperfine
        saveData['demand'] = demand
        saveData['eb'] = eb
        saveData['pname'] = d['pname']
        saveData['cname'] = d['cname']
        saveData['sname'] = d['sname']

        miniZinc.saveDataFile(saveData, nameScenario)

        return redirect(url_for('calculate'))

    return render_template('createscenario_new2.html', input=d)



@app.route('/createscenario_edit/<option>', methods=['GET', 'POST'])
def createscenario_edit(option):
    form = CreateForm()
    datafiles, datafiles_name = refreshDataFiles()
    form.option.choices = [(str(i), datafiles_name[i-1] + '  Scenario - ' + str(i)) for i in range(1, len(datafiles) + 1)]
    o1 = form.option.data
    modelfile = modelfile_final
    for i in range(1, len(datafiles) + 1):
        if option == str(i):
            data: str = datafiles[i - 1]

    couenne = "couenne"
    option = option
    model = Model()
    solver = Solver.lookup(couenne)
    mini = miniZinc.MiniZincModel(model, solver, data, modelfile)
    dataList = dataList_final
    d = mini.getdatainput(dataList)
    inputdata = {}
    inputdata['option1'] = d
    if form.validate_on_submit():
        if 'create' in request.form:
            return redirect(url_for('createscenario_edit', option=o1, form=form))
        elif 'createNew' in request.form:
            return redirect(url_for('createscenario_new'))
        else:
            formvalues = request.form
            for key in formvalues:
                if key.startswith('nameScenario'):
                    nameScenario = str(request.form[key])

            eb = [[0 for x in range(0, d['nproducts'])] for y in range(0, d['ncustomers'])]
            for key in formvalues:
                for i in range(0, d['ncustomers']):
                    for j in range(0, d['nproducts']):
                        if key.startswith('eb_' + str(i) + '_' + str(j)):
                            eb[i][j] = int(request.form[key])

            for key in formvalues:
                if key.startswith('nproducts'):
                    nproducts = int(request.form[key])

            for key in formvalues:
                if key.startswith('nsites'):
                    nsites = int(request.form[key])

            for key in formvalues:
                if key.startswith('ncustomers'):
                    ncustomers = int(request.form[key])

            for key in formvalues:
                if key.startswith('payperfine'):
                    payperfine = int(request.form[key])

            productionPlan = [[0 for x in range(0, d['nproducts'])] for y in range(0, d['nsites'])]
            for key in formvalues:
                for i in range(0, d['nsites']):
                    for j in range(0, d['nproducts']):
                        if key.startswith('productionPlan_' + str(i) + '_' + str(j)):
                            productionPlan[i][j] = int(request.form[key])

            supercredit = [0 for x in range(0, d['nproducts'])]
            for key in formvalues:
                for i in range(0, d['nproducts']):
                    if key.startswith('supercredit_' + str(i)):
                        supercredit[i] = float(request.form[key])
                        supercredit[i] = int(supercredit[i]* 100)

            demand = [[0 for x in range(0, d['nproducts'])] for y in range(0, d['ncustomers'])]
            for key in formvalues:
                for i in range(0, d['ncustomers']):
                    for j in range(0, d['nproducts']):
                        if key.startswith('demand_' + str(i) + '_' + str(j)):
                            demand[i][j] = int(request.form[key])

            excessdemand = [0 for x in range(0, d['nproducts'])]
            for key in formvalues:
                for i in range(0, d['nproducts']):
                    if key.startswith('excessdemand_' + str(i)):
                        excessdemand[i] = float(request.form[key])

            maxProduction = [0 for x in range(0, d['nsites'])]
            for key in formvalues:
                for i in range(0, d['nsites']):
                    if key.startswith('maxProduction_' + str(i)):
                        maxProduction[i] = int(request.form[key])

            emissionWLTP = [0 for x in range(0, d['nproducts'])]
            for key in formvalues:
                for i in range(0, d['nproducts']):
                    if key.startswith('emissionWLTP_' + str(i)):
                        emissionWLTP[i] = int(request.form[key])

            weight = [0 for x in range(0, d['nproducts'])]
            for key in formvalues:
                for i in range(0, d['nproducts']):
                    if key.startswith('weight_' + str(i)):
                        weight[i] = int(request.form[key])

            saveData = {}
            saveData['nproducts'] = nproducts
            saveData['nsites'] = nsites
            saveData['ncustomers'] = ncustomers
            saveData['maxProduction'] = maxProduction
            saveData['emissionWLTP'] = emissionWLTP
            saveData['weight'] = weight
            saveData['excessdemand'] = excessdemand
            saveData['supercredit'] = supercredit
            saveData['productionPlan'] = productionPlan
            saveData['payperfine'] = payperfine
            saveData['demand'] = demand
            saveData['eb'] = eb
            saveData['pname'] = d['pname']
            saveData['cname'] = d['cname']
            saveData['sname'] = d['sname']

            miniZinc.saveDataFile(saveData, nameScenario)

            return redirect(url_for('calculate'))

    return render_template('createscenario_edit.html', title='Home', form=form, option=option, input=d)


@app.route('/calcandshow/<option>/<option2>', methods=['GET', 'POST'])
def calcandshow(option, option2):
    form = CalculateForm()
    datafiles, datafiles_name = refreshDataFiles()
    form.option.choices = [(str(i), datafiles_name[i-1] + '  Scenario - ' + str(i)) for i in range(1, len(datafiles) + 1)]
    form.option2.choices = [(str(i), datafiles_name[i-1] + '  Scenario - ' + str(i)) for i in range(1, len(datafiles) + 1)]
    modelfile = modelfile_final
    print(datafiles_name)
    for i in range(1, len(datafiles)+1):
        if option == str(i):
            data: str = datafiles[i-1]

        if option2 == str(i):
            data2: str = datafiles[i - 1]

    couenne = "couenne"
    option = option
    option_array = [option, option2]
    option2 = option2
    data_name = [0 for i in range(0,2)]
    data_name[0] = datafiles_name[int(option) - 1]
    data_name[1] = datafiles_name[int(option2) - 1]
    model = Model()
    model2 = Model()
    solver = Solver.lookup(couenne)
    mini = miniZinc.MiniZincModel(model, solver, data, modelfile)
    mini2 = miniZinc.MiniZincModel(model2, solver, data2, modelfile)
    dataList = dataList_final
    optionList_final = ['option1', 'option2']
    d = mini.getdatainput(dataList)
    d2 = mini2.getdatainput(dataList)
    inputdata = {}
    inputdata['option1'] = d
    inputdata['option2'] = d2
    o1 = form.option.data
    o2 = form.option2.data

    if form.validate_on_submit():
        if 'show' in request.form:
            return redirect(url_for('calcandshow', title='Home', option=o1, option2=o2))
        elif 'editDataoption1' in request.form:
            editoption = 1
            return redirect(url_for('editdata', title='Home', editoption=editoption, option=option, option2=option2, option_array=option_array))
        elif 'editDataoption2' in request.form:
            editoption = 2
            return redirect(url_for('editdata', title='Home', editoption=editoption, option=option, option2=option2, option_array=option_array))
        else:
            result = mini.getresults()
            result2 = mini2.getresults()
            decision = decisionList_final
            try:
                r = mini.getdecisionvariable(decision, result)
                r2 = mini2.getdecisionvariable(decision, result2)
            except KeyError:
                flash('No Solution for this data')
                return redirect(url_for('calcandshow', option=option, option2=option2))

            produceRestriction2, restrictionConstraint2 = mini2.getRestrictionsProduce(d2['maxProduction'], r2['produce'], d2['productionPlan'],
                                                               r2['demand_per_Product'],
                                                               d2['excessdemand'])
            produceRestriction, restrictionConstraint = mini2.getRestrictionsProduce(d['maxProduction'], r['produce'], d['productionPlan'],
                                                              r['demand_per_Product'],
                                                              d['excessdemand'])
            deliveredRestriction = mini.getRestrictionsDelivery(produceRestriction, r['delivered'], d['demand'],
                                                                d['productionPlan'])
            deliveredRestriction2 = mini2.getRestrictionsDelivery(produceRestriction2, r2['delivered'], d2['demand'],
                                                                  d2['productionPlan'])

            finePerProduct, finePerSingleCar = miniZinc.getFinePerProduct(r['soldCars'], d['emissionWLTP'],
                                                                          r['emission'], r['emissionRealFine'])
            finePerProduct2, finePerSingleCar2 = miniZinc.getFinePerProduct(r2['soldCars'], d2['emissionWLTP'],
                                                                            r2['emission'], r2['emissionRealFine'])

            optimumChangePerProductNeg = miniZinc.getoptimumChangePerProductNeg(r, d)
            optimumChangePerProductPos = miniZinc.getoptimumChangePerProductPos(r, d)
            optimumChangePerProductNeg2 = miniZinc.getoptimumChangePerProductNeg(r2, d2)
            optimumChangePerProductPos2 = miniZinc.getoptimumChangePerProductPos(r2, d2)

            saving, finePerCar_oldWLTP, emissionFine_without_supercredit = miniZinc.getSavingandFine(r['soldCars'], r['sold'], r['emissionlimit'], d['emissionWLTP'], d['payperfine'], r['emission'], r['emissionRealFine'], d['supercredit'])
            saving2, finePerCar_oldWLTP2, emissionFine_without_supercredit2  = miniZinc.getSavingandFine(r2['soldCars'], r2['sold'], r2['emissionlimit'], d2['emissionWLTP'], d2['payperfine'], r2['emission'], r2['emissionRealFine'], d2['supercredit'])

            return render_template('index.html', title='Home', inputdata=d, inputdata2=d2,
                                   option=option, option2=option2, data_name=data_name, colors=colors, input=inputdata,
                                   options=optionList_final, option_array=option_array, result2=r2, result=r,
                                   produceRestriction2=produceRestriction2, produceRestriction=produceRestriction,
                                   deliveredRestriction=deliveredRestriction, deliveredRestriction2=deliveredRestriction2,
                                   restrictionConstraint2=restrictionConstraint2, restrictionConstraint=restrictionConstraint,
                                   finePerProduct=finePerProduct, finePerProduct2=finePerProduct2,
                                   finePerSingleCar=finePerSingleCar, finePerSingleCar2= finePerSingleCar2,
                                   saving=saving, saving2=saving2,
                                   finePerCar_oldWLTP=finePerCar_oldWLTP, finePerCar_oldWLTP2=finePerCar_oldWLTP2,
                                   optimumChangePerProductNeg=optimumChangePerProductNeg,
                                   optimumChangePerProductNeg2=optimumChangePerProductNeg2,
                                   optimumChangePerProductPos=optimumChangePerProductPos,
                                   optimumChangePerProductPos2=optimumChangePerProductPos2,
                                   emissionFine_without_supercredit=emissionFine_without_supercredit,
                                   emissionFine_without_supercredit2=emissionFine_without_supercredit2)

    return render_template('calcandshow.html', title='Home', form=form, data_name=data_name, option=o1, option2=o2, input=inputdata, options=optionList_final, colors=colors, option_array=option_array)


@app.route('/editdata/<option>/<option2>/<editoption>', methods=['GET', 'POST'])
def editdata(option, option2, editoption):
    form = EditForm()
    datafiles, datafiles_name = refreshDataFiles()
    modelfile = modelfile_final
    for i in range(1, len(datafiles)+1):
        if option == str(i):
            data: str = datafiles[i-1]

        if option2 == str(i):
            data2: str = datafiles[i - 1]
    couenne = "couenne"
    option=option
    option2=option2
    data_name = [0 for i in range(0, 2)]
    data_name[0] = datafiles_name[int(option) - 1]
    data_name[1] = datafiles_name[int(option2) - 1]
    model = Model()
    model2 = Model()
    solver = Solver.lookup(couenne)
    mini = miniZinc.MiniZincModel(model, solver, data, modelfile)
    mini2 = miniZinc.MiniZincModel(model2, solver, data2, modelfile)
    dataList = dataList_final
    decision = decisionList_final
    optionList_final = ['option1', 'option2']
    optionList_final_index = {'option1', 'option2'}
    optionList = optionList_final
    d = mini.getdatainput(dataList)
    d2 = mini2.getdatainput(dataList)
    editoption = "option" + editoption
    inputdata = {}
    inputdata['option1'] = d
    inputdata['option2'] = d2
    option_array = [option, option2]
    if editoption == 'option2':
        data = d2
    else:
        data = d

    if 'calculate' in request.form:
        formvalues = request.form
        eb = [[ 0 for x in range(0,data['nproducts'])] for y in range(0,data['ncustomers'])]
        for key in formvalues:
            for i in range(0,data['ncustomers']):
                    for j in range(0,data['nproducts']):
                        if key.startswith('eb_' + str(i) +'_' + str(j)):
                            eb[i][j] = int(request.form[key])

        demand = [[0 for x in range(0, data['nproducts'])] for y in range(0, data['ncustomers'])]
        for key in formvalues:
            for i in range(0, data['ncustomers']):
                for j in range(0, data['nproducts']):
                    if key.startswith('demand_' + str(i) + '_' + str(j)):
                        demand[i][j] = int(request.form[key])

        excessdemand = [0 for x in range(0, data['nproducts'])]
        for key in formvalues:
            for i in range(0, data['nproducts']):
                if key.startswith('excessdemand_' + str(i)):
                    excessdemand[i] = float(request.form[key])

        maxProduction = [0 for x in range(0, data['nsites'])]
        for key in formvalues:
            for i in range(0, data['nsites']):
                if key.startswith('maxProduction_' + str(i)):
                    maxProduction[i] = int(request.form[key])

        emissionWLTP = [0 for x in range(0, data['nproducts'])]
        for key in formvalues:
            for i in range(0, data['nproducts']):
                if key.startswith('emissionWLTP_' + str(i)):
                    emissionWLTP[i] = int(request.form[key])

        weight = [0 for x in range(0, data['nproducts'])]
        for key in formvalues:
            for i in range(0, data['nproducts']):
                if key.startswith('weight_' + str(i)):
                    weight[i] = int(request.form[key])

        supercredit = [0 for x in range(0, d['nproducts'])]
        for key in formvalues:
            for i in range(0, d['nproducts']):
                if key.startswith('supercredit_' + str(i)):
                    supercredit[i] = float(request.form[key])
                    supercredit[i] = int(supercredit[i] * 100)

        if editoption == 'option1':
            mini.mod._data.__setitem__('eb', eb)
            mini.mod._data.__setitem__('demand', demand)
            mini.mod._data.__setitem__('excessdemand', excessdemand)
            mini.mod._data.__setitem__('maxProduction', maxProduction)
            mini.mod._data.__setitem__('emissionWLTP', emissionWLTP)
            mini.mod._data.__setitem__('weight', weight)
            mini.mod._data.__setitem__('supercredit', supercredit)
            mini.ins = CLI.CLIInstance(solver, mini.mod)

        elif editoption == 'option2':
            mini2.mod._data.__setitem__('eb', eb)
            mini2.mod._data.__setitem__('demand', demand)
            mini2.mod._data.__setitem__('excessdemand', excessdemand)
            mini2.mod._data.__setitem__('maxProduction', maxProduction)
            mini2.mod._data.__setitem__('emissionWLTP', emissionWLTP)
            mini2.mod._data.__setitem__('weight', weight)
            mini2.mod._data.__setitem__('supercredit', supercredit)
            mini2.ins = CLI.CLIInstance(solver, mini2.mod)

        result = mini.getresults()
        result2 = mini2.getresults()
        d = mini.getdatainput(dataList)
        d2 = mini2.getdatainput(dataList)
        try:
            r = mini.getdecisionvariable(decision, result)
            r2 = mini2.getdecisionvariable(decision, result2)
        except KeyError:
            flash('No Solution for this data')
            return redirect(url_for('calcandshow', option=option, option2=option2))

        produceRestriction2, restrictionConstraint2 = mini2.getRestrictionsProduce(d2['maxProduction'], r2['produce'], d2['productionPlan'],
                                                           r2['demand_per_Product'],
                                                           d2['excessdemand'])
        produceRestriction, restrictionConstraint = mini2.getRestrictionsProduce(d['maxProduction'], r['produce'], d['productionPlan'],
                                                          r['demand_per_Product'],
                                                          d['excessdemand'])

        deliveredRestriction = mini.getRestrictionsDelivery(produceRestriction, r['delivered'], d['demand'],
                                                            d['productionPlan'])
        deliveredRestriction2 = mini2.getRestrictionsDelivery(produceRestriction2, r2['delivered'], d2['demand'],
                                                              d2['productionPlan'])

        finePerProduct, finePerSingleCar = miniZinc.getFinePerProduct(r['soldCars'], d['emissionWLTP'], r['emission'], r['emissionRealFine'])
        finePerProduct2, finePerSingleCar2 = miniZinc.getFinePerProduct(r2['soldCars'], d2['emissionWLTP'], r2['emission'], r2['emissionRealFine'])

        saving, finePerCar_oldWLTP, emissionFine_without_supercredit = miniZinc.getSavingandFine(r['soldCars'], r['sold'], r['emissionlimit'], d['emissionWLTP'], d['payperfine'], r['emission'], r['emissionRealFine'], d['supercredit'])
        saving2, finePerCar_oldWLTP2, emissionFine_without_supercredit2 = miniZinc.getSavingandFine(r2['soldCars'], r2['sold'], r2['emissionlimit'],
                                                                 d2['emissionWLTP'], d2['payperfine'], r2['emission'],
                                                                 r2['emissionRealFine'], d2['supercredit'])
        optimumChangePerProductNeg = miniZinc.getoptimumChangePerProductNeg(r, d)
        optimumChangePerProductPos = miniZinc.getoptimumChangePerProductPos(r, d)
        optimumChangePerProductNeg2 = miniZinc.getoptimumChangePerProductNeg(r2, d2)
        optimumChangePerProductPos2 = miniZinc.getoptimumChangePerProductPos(r2, d2)

        inputdata = {}
        inputdata['option1'] = d
        inputdata['option2'] = d2

        return render_template('index.html', title='Home', result=r, result2=r2, inputdata=d, inputdata2=d2,
                                option=option, option2=option2, data_name=data_name, colors=colors, input=inputdata, options=optionList, option_array=option_array,
                               produceRestriction2=produceRestriction2, produceRestriction=produceRestriction,
                               deliveredRestriction=deliveredRestriction, deliveredRestriction2=deliveredRestriction2,
                               restrictionConstraint2=restrictionConstraint2, restrictionConstraint=restrictionConstraint,
                               finePerProduct=finePerProduct, finePerProduct2=finePerProduct2,
                               saving=saving, saving2=saving2,
                               finePerSingleCar=finePerSingleCar, finePerSingleCar2=finePerSingleCar2,
                               finePerCar_oldWLTP=finePerCar_oldWLTP, finePerCar_oldWLTP2=finePerCar_oldWLTP2,
                               optimumChangePerProductNeg=optimumChangePerProductNeg,
                               optimumChangePerProductNeg2=optimumChangePerProductNeg2,
                               optimumChangePerProductPos=optimumChangePerProductPos,
                               optimumChangePerProductPos2=optimumChangePerProductPos2,
                               emissionFine_without_supercredit=emissionFine_without_supercredit,
                               emissionFine_without_supercredit2=emissionFine_without_supercredit2)

    return render_template('editdata.html', title='Home', data_name=data_name, option=option, option2=option2, input=inputdata,
                           options=optionList, colors=colors, option_array=option_array, form=form, editoption=editoption)


@app.route('/index/<option>/<option2>', methods=['GET', 'POST'])
def index(option, option2):
    datafiles, datafiles_name = refreshDataFiles()
    modelfile = modelfile_final
    for i in range(1, len(datafiles)+1):
        if option == str(i):
            data: str = datafiles[i-1]

        if option2 == str(i):
            data2: str = datafiles[i - 1]

    couenne = "couenne"
    option = option
    option2 = option2
    option_array = [option, option2]
    data_name = [0 for i in range(0, 2)]
    data_name[0] = datafiles_name[int(option) - 1]
    data_name[1] = datafiles_name[int(option2) - 1]
    model = Model()
    model2 = Model()
    solver = Solver.lookup(couenne)
    mini = miniZinc.MiniZincModel(model, solver, data, modelfile)
    mini2 = miniZinc.MiniZincModel(model2, solver, data2, modelfile)
    result = mini.getresults()
    result2 = mini2.getresults()
    dataList = dataList_final
    decision = decisionList_final
    optionList_final = ['option1', 'option2']
    d = mini.getdatainput(dataList)
    d2 = mini2.getdatainput(dataList)

    if 'editData1' in request.form:
        editoption = 1
        return redirect(url_for('editdata', title='Home', editoption=editoption, option=option, option2=option2))
    elif 'editData2' in request.form:
        editoption = 2
        return redirect(url_for('editdata', title='Home', editoption=editoption, option=option, option2=option2))

    try:
        r = mini.getdecisionvariable(decision, result)
        r2 = mini2.getdecisionvariable(decision, result2)
    except KeyError:
        flash('No Solution for this data')
        return redirect(url_for('calculate'))

    produceRestriction2, restrictionConstraint2 = mini2.getRestrictionsProduce(d2['maxProduction'], r2['produce'],d2['productionPlan'], r2['demand_per_Product'],
                                                       d2['excessdemand'])
    produceRestriction, restrictionConstraint = mini.getRestrictionsProduce(d['maxProduction'], r['produce'], d['productionPlan'],
                                                       r['demand_per_Product'],
                                                       d['excessdemand'])
    deliveredRestriction = mini.getRestrictionsDelivery(produceRestriction, r['delivered'], d['demand'], d['productionPlan'])
    deliveredRestriction2 = mini2.getRestrictionsDelivery(produceRestriction2, r2['delivered'], d2['demand'], d2['productionPlan'])

    finePerProduct, finePerSingleCar = miniZinc.getFinePerProduct(r['soldCars'], d['emissionWLTP'], r['emission'],
                                                                  r['emissionRealFine'])
    finePerProduct2, finePerSingleCar2 = miniZinc.getFinePerProduct(r2['soldCars'], d2['emissionWLTP'], r2['emission'],
                                                                    r2['emissionRealFine'])

    saving, finePerCar_oldWLTP, emissionFine_without_supercredit = miniZinc.getSavingandFine(r['soldCars'], r['sold'], r['emissionlimit'], d['emissionWLTP'], d['payperfine'], r['emission'], r['emissionRealFine'], d['supercredit'])
    saving2, finePerCar_oldWLTP2, emissionFine_without_supercredit2 = miniZinc.getSavingandFine(r2['soldCars'], r2['sold'], r2['emissionlimit'],
                                                             d2['emissionWLTP'], d2['payperfine'], r2['emission'],
                                                             r2['emissionRealFine'], d2['supercredit'])
    optimumChangePerProductNeg = miniZinc.getoptimumChangePerProductNeg(r, d)
    optimumChangePerProductPos = miniZinc.getoptimumChangePerProductPos(r, d)
    optimumChangePerProductNeg2 = miniZinc.getoptimumChangePerProductNeg(r2, d2)
    optimumChangePerProductPos2 = miniZinc.getoptimumChangePerProductPos(r2, d2)

    inputdata = {}
    inputdata['option1'] = d
    inputdata['option2'] = d2

    return render_template('index.html', title='Home', result=r, result2=r2, inputdata=d, inputdata2=d2,
                           option=option, option2=option2, data_name=data_name, colors=colors, input=inputdata,
                           options=optionList_final, option_array=option_array, produceRestriction2=produceRestriction2,
                           produceRestriction=produceRestriction, deliveredRestriction=deliveredRestriction,
                           deliveredRestriction2=deliveredRestriction2, restrictionConstraint2=restrictionConstraint2,
                           restrictionConstraint=restrictionConstraint,
                           saving=saving, saving2=saving2,
                            finePerProduct=finePerProduct, finePerProduct2=finePerProduct2,
                           finePerSingleCar=finePerSingleCar, finePerSingleCar2=finePerSingleCar2,
                           finePerCar_oldWLTP=finePerCar_oldWLTP, finePerCar_oldWLTP2=finePerCar_oldWLTP2,
                           optimumChangePerProductNeg=optimumChangePerProductNeg, optimumChangePerProductNeg2=optimumChangePerProductNeg2,
                           optimumChangePerProductPos=optimumChangePerProductPos, optimumChangePerProductPos2=optimumChangePerProductPos2,
                           emissionFine_without_supercredit=emissionFine_without_supercredit,
                           emissionFine_without_supercredit2=emissionFine_without_supercredit2)


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', title='Hello')


