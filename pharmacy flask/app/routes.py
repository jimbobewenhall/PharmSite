from app import app
from app.forms import LoginForm, AddForm

from flask import render_template, send_file, redirect, request

from datetime import datetime, timedelta
import dateutil.parser

import pandas as pd
import numpy



### Home page ###

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

#################

### Find script###

@app.route('/find', methods=['GET', 'POST'])
def find():
    form = LoginForm()
    data = pd.read_csv('./app/outputs/patient_list.csv')
    
    if form.validate_on_submit():
        name = form.name.data
        try:
            surname, forename = name.lower().split()
        except:
            surname = name.lower()

        try:
            results = data[data['Last_Name'].str.lower().str.contains(surname, na=False)
                   & data['First_Name'].str.lower().str.contains(forename, na=False)]
        except:
            results = data[data['Last_Name'].str.lower().str.contains(surname, na=False)]

        for i in range(len(results)):
            results.loc[results.index[i], 'Url'] = str('<a href="/find/'+str(results.index[i])+'">Select</a>')
        results = results[['Url', 'Last_Name', 'First_Name', 'DOB',
                           'Post_Code', 'Location']]
        table=[results.to_html(escape=False, index=False)]
        
        return render_template('table.html', table=table, titles=data.columns.values)
    
    return render_template('namefind.html', form=form)

@app.route('/find/<int:id>', methods=['GET', 'POST'])
def found(id):
    data = pd.read_csv('./app/outputs/patient_list.csv')
    if data.loc[id, 'Location'] != '0':
        result = 'Script is in: '+data.loc[id, 'Location']
    else:
        result = 'No Script Found'
    
    data.to_csv('./app/outputs/patient_list.csv', index=False)
    return render_template('found.html', id=id, result=result)

@app.route('/find/<int:id>/paid', methods=['GET', 'POST'])
def paid(id):
    data=pd.read_csv('./app/outputs/patient_list.csv')
    data.loc[id, 'Location'] = '0'
    paid_data = pd.read_csv('./app/outputs/paid.csv')

    new_row = {'Last_Name':data.loc[id, 'Last_Name'],
                           'First_Name':data.loc[id, 'First_Name']}

    paid_data = paid_data.append(new_row, ignore_index=True)
    paid_data.to_csv('./app/outputs/paid.csv', index=False)

    return redirect('/index')

@app.route('/find/<int:id>/exempt', methods=['GET', 'POST'])
def exempt(id):
    data=pd.read_csv('./app/outputs/patient_list.csv')
    data.loc[id, 'Location'] = '0'
    exempt_data = pd.read_csv('./app/outputs/exempt.csv')

    new_row = {'Last_Name':data.loc[id, 'Last_Name'],
                           'First_Name':data.loc[id, 'First_Name']}
    print(new_row)

    exempt_data = exempt_data.append(new_row, ignore_index=True)
    exempt_data.to_csv('./app/outputs/exempt.csv', index=False)

    return redirect('/index')
#####################

### File script ###

@app.route('/file', methods=['GET', 'POST'])
def file():
    form = LoginForm()
    data = pd.read_csv('./app/outputs/patient_list.csv')
    
    if form.validate_on_submit():
        name = form.name.data
        try:
            surname, forename = name.lower().split()
        except:
            surname = name.lower()

        try:
            results = data[data['Last_Name'].str.lower().str.contains(surname, na=False)
                   & data['First_Name'].str.lower().str.contains(forename, na=False)]
        except:
            results = data[data['Last_Name'].str.lower().str.contains(surname, na=False)]

        if results.empty:
            return redirect('/file/add_name')
            
        for i in range(len(results)):
            results.loc[results.index[i], 'Url'] = str('<a href="/filed/'+str(results.index[i])+'">Select</a>')
        results = results[['Url', 'Last_Name', 'First_Name', 'DOB',
                           'Post_Code', 'Location']]
        table=[results.to_html(escape=False, index=False)]
        
        return render_template('table.html', table=table, titles=data.columns.values)
    
    return render_template('namefind.html', form=form)

@app.route('/filed/<int:id>', methods=['GET', 'POST'])
def filed(id):
    form = LoginForm()
    data = pd.read_csv('./app/outputs/patient_list.csv')
    result = data.loc[id, 'Location']
    if result != '0':
        if form.validate_on_submit():
            new_loc = form.name.data
            data.loc[id, 'Location'] = new_loc
            data.loc[id, 'Date_filed'] = pd.to_datetime(datetime.now())
            data.to_csv('./app/outputs/patient_list.csv', index=False)
            return redirect('/index')
        return render_template('exists.html', loc='Old script found in: ' + result, form=form)

    else:
        if form.validate_on_submit():
            new_loc = form.name.data
            new_loc = form.name.data
            data.loc[id, 'Location'] = new_loc
            data.loc[id, 'Date_filed'] = pd.to_datetime(datetime.now())
            data.to_csv('./app/outputs/patient_list.csv', index=False)
            return redirect('/index')
        return render_template('exists.html', loc='', form=form)

@app.route('/file/add_name', methods=['GET', 'POST'])
def add_name():
    form = AddForm()
    data = pd.read_csv('./app/outputs/patient_list.csv')
    
    if form.validate_on_submit():
        new_row = [{'Last_Name':form.surname.data,
                    'First_Name':form.forename.data,
                    'DOB':form.DOB.data,
                    'Address1':form.Address1.data,
                    'Address2':form.Address2.data,
                    'Town':form.Town.data,
                    'County':form.County.data,
                    'Post_Code':form.Post_code.data,
                    'Location':'0',
                    'Date_filed':numpy.nan}]
        data = data.append(new_row)
        data.to_csv('./app/outputs/patient_list.csv', index=False)
        return redirect('/file')
    return render_template('add_name.html', form=form)
#######################

### Other ###

@app.route('/other', methods=['GET', 'POST'])
def other():
    return render_template('other.html')

@app.route('/old_files', methods=['GET', 'POST'])
def old_files():
    data = pd.read_csv('./app/outputs/patient_list.csv')
    data = data.dropna(subset=['Date_filed'])

    data['Date_filed'] = pd.to_datetime(data['Date_filed'])
        
    results = data[pd.to_datetime(data['Date_filed']) < (pd.to_datetime(datetime.now()-timedelta(days=84)))]
    results = results[['Last_Name', 'First_Name', 'Date_filed']]

    for i in range(len(results)):
            results.loc[results.index[i], 'Url'] = str('<form action="" method="post"> <button name="submit_button" type="submit" value="'+str(results.index[i])+'">Dismantled</button></form>')
    if request.method == 'POST':
        data = pd.read_csv('./app/outputs/patient_list.csv')
        id = data.index[int(request.form['submit_button'])]
        data.loc[id,'Date_filed']=numpy.nan
        data.loc[id,'Location']='0'
        data.to_csv('./app/outputs/patient_list.csv', index=False)
        return redirect('/old_files')
        
    return render_template('old_files.html', tables=[results.to_html(escape=False, index=False)],
                           titles=results.columns.values)

@app.route('/old_files/clear', methods=['GET', 'POST'])
def clear_files():
    data = pd.read_csv('./app/outputs/patient_list.csv')
    results = data.dropna(subset=['Date_filed'])

    results['Date_filed'] = pd.to_datetime(results['Date_filed'])
        
    results = results[pd.to_datetime(results['Date_filed']) < (pd.to_datetime(datetime.now()-timedelta(days=84)))]
    for i in range(len(results)):
        data.loc[results.index[i], 'Date_filed']=numpy.nan

    data.to_csv('./app/outputs/patient_list.csv', index=False)

    return redirect('/old_files')

@app.route('/collect', methods=['GET', 'POST'])
def collect():
    df = pd.DataFrame(columns=['Last_Name', 'First_Name'])
    df.to_csv('./app/outputs/paid.csv')
    df.to_csv('./app/outputs/exempt.csv')
    return redirect('/index')

@app.route('/view', methods=['GET', 'POST'])
def view():
    data = pd.read_csv('./app/outputs/exempt.csv')
    data2 = pd.read_csv('./app/outputs/paid.csv')
    return render_template('view.html', tables=[data.to_html(index=False)],
                           titles=data.columns.values, tables2=[data2.to_html(index=False)],
                           titles2=data2.columns.values)

@app.route('/download_exempt', methods=['GET', 'POST'])
def download_exempt():
    return send_file('outputs/exempt.csv',
                     mimetype='text/csv',
                     attachment_filename='exempt.csv',
                     as_attachment=True)

@app.route('/download_paid', methods=['GET', 'POST'])
def download_paid():
    return send_file('outputs/paid.csv',
                     mimetype='text/csv',
                     attachment_filename='paid.csv',
                     as_attachment=True)

@app.route('/download_CD', methods=['GET', 'POST'])
def download_CD():
    writer = pd.ExcelWriter('./app/outputs/CD.xlsx', engine='xlsxwriter')
    data2 = pd.read_excel('./app/outputs/Dispensed_CD.xlsx')
    data3 = pd.read_excel('./app/outputs/Filed_CD.xlsx')
    data4 = pd.read_excel('./app/outputs/Collected_CD.xlsx')
    main = pd.read_excel('./app/outputs/CD.xlsx')

    data2.to_excel(writer, sheet_name='Sheet1')
    data3.to_excel(writer, sheet_name='Sheet2')
    data4.to_excel(writer, sheet_name='Sheet3')

    writer.save()
    return send_file('outputs/CD.xlsx',
                     mimetype='text/xlsx',
                     attachment_filename='CD.xlsx',
                     as_attachment=True)


@app.route('/CD', methods=['GET', 'POST'])
def CD():
    form = LoginForm()
    data = pd.read_csv('./app/outputs/patient_list.csv')
    if form.validate_on_submit():
        name = form.name.data
        try:
            surname, forename = name.lower().split()
        except:
            surname = name.lower()

        try:
            results = data[data['Last_Name'].str.lower().str.contains(surname, na=False)
                   & data['First_Name'].str.lower().str.contains(forename, na=False)]
        except:
            results = data[data['Last_Name'].str.lower().str.contains(surname, na=False)]

        for i in range(len(results)):
            results.loc[results.index[i], 'Url'] = str('<a href="/CD/'+str(results.index[i])+'">Select</a>')
        results = results[['Url', 'Last_Name', 'First_Name', 'DOB',
                           'Post_Code', 'Location']]
        table=[results.to_html(escape=False, index=False)]
        
        return render_template('table.html', table=table, titles=data.columns.values)
    return render_template('find.html', form=form)

@app.route('/CD/<int:id>', methods=['GET', 'POST'])
def CD_selection(id):
    return render_template('CD.html', id=id)

@app.route('/CD/<int:id>/printed', methods=['GET', 'POST'])
def CD_printed(id):
    data = pd.read_csv('./app/outputs/patient_list.csv')
    writer = pd.ExcelWriter('./app/outputs/Dispensed_CD.xlsx', engine='xlsxwriter')
    data2 = pd.read_excel('./app/outputs/Dispensed_CD.xlsx')

    new_row = [{'Last_Name':data.loc[id,'Last_Name'],
            'First_Name':data.loc[id,'First_Name'],
            'DOB':data.loc[id,'DOB'],
            'Date_Dispensed':pd.to_datetime(datetime.now())
           }]
    data2 = data2.append(new_row, ignore_index=True)

    data2.to_excel('./app/outputs/Dispensed_CD.xlsx', index=False)
    return redirect('/index')

@app.route('/CD/<int:id>/filed', methods=['GET', 'POST'])
def CD_filed(id):
    data = pd.read_csv('./app/outputs/patient_list.csv')
    writer = pd.ExcelWriter('./app/outputs/Filed_CD.xlsx', engine='xlsxwriter')
    data2 = pd.read_excel('./app/outputs/Filed_CD.xlsx')
    new_row = [{'Last_Name':data.loc[id,'Last_Name'],
                'First_Name':data.loc[id,'First_Name'],
                'DOB':data.loc[id,'DOB'],
                'Date_Filed':pd.to_datetime(datetime.now())
               }]
    data2 = data2.append(new_row, ignore_index=True)
    data2.to_excel('./app/outputs/Filed_CD.xlsx', index=False)
    result = data.loc[id, 'Location']
    form = LoginForm()
    if result != '0':
        if form.validate_on_submit():
            new_loc = form.name.data
            data.loc[id, 'Location'] = new_loc
            data.loc[id, 'Date_filed'] = pd.to_datetime(datetime.now())
            data.to_csv('./app/outputs/patient_list.csv', index=False)
            return redirect('/index')
        return render_template('exists.html', loc='Old script found in: ' + result, form=form)

    else:
        if form.validate_on_submit():
            new_loc = form.name.data
            new_loc = form.name.data
            data.loc[id, 'Location'] = new_loc
            data.loc[id, 'Date_filed'] = pd.to_datetime(datetime.now())
            data.to_csv('./app/outputs/patient_list.csv', index=False)
            return redirect('/index')
        return render_template('exists.html', loc='', form=form)
    
@app.route('/CD/<int:id>/collected', methods=['GET', 'POST'])
def CD_collected(id):
    data = pd.read_csv('./app/outputs/patient_list.csv')
    writer = pd.ExcelWriter('./app/outputs/Collected_CD.xlsx', engine='xlsxwriter')
    data2 = pd.read_excel('./app/outputs/Collected_CD.xlsx')
    new_row = [{'Last_Name':data.loc[id,'Last_Name'],
                'First_Name':data.loc[id,'First_Name'],
                'DOB':data.loc[id,'DOB'],
                'Date_Collected':pd.to_datetime(datetime.now())
               }]
    data2 = data2.append(new_row, ignore_index=True)
    data2.to_excel('./app/outputs/Collected_CD.xlsx', index=False)
    if data.loc[id, 'Location'] != '0':
        result = data.loc[id, 'Location']
    else:
        result = 'No Script Found'
    
    data.to_csv('./app/outputs/patient_list.csv', index=False)
    return render_template('found.html', id=id, result=result)