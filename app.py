from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_artifacts():
    with open(os.path.join(BASE_DIR, 'model.pkl'), 'rb') as f:
        model = pickle.load(f)
    with open(os.path.join(BASE_DIR, 'scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    with open(os.path.join(BASE_DIR, 'columns.pkl'), 'rb') as f:
        columns = pickle.load(f)
    return model, scaler, columns

model, scaler, columns = load_artifacts()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            gender          = request.form.get('gender')
            married         = request.form.get('married')
            dependents      = request.form.get('dependents')
            education       = request.form.get('education')
            self_employed   = request.form.get('self_employed')
            applicant_income    = float(request.form.get('applicant_income'))
            coapplicant_income  = float(request.form.get('coapplicant_income'))
            loan_amount         = float(request.form.get('loan_amount'))
            loan_amount_term    = float(request.form.get('loan_amount_term'))
            credit_history      = float(request.form.get('credit_history'))
            property_area   = request.form.get('property_area')

            gender_val          = 1 if gender == 'Male' else 0
            married_val         = 1 if married == 'Yes' else 0
            dependents_val      = 4 if dependents == '3+' else int(dependents)
            education_val       = 1 if education == 'Graduate' else 0
            self_employed_val   = 1 if self_employed == 'Yes' else 0
            property_area_val   = {'Rural': 0, 'Semiurban': 1, 'Urban': 2}.get(property_area, 0)

            input_dict = {
                'Gender': gender_val,
                'Married': married_val,
                'Dependents': dependents_val,
                'Education': education_val,
                'Self_Employed': self_employed_val,
                'ApplicantIncome': applicant_income,
                'CoapplicantIncome': coapplicant_income,
                'LoanAmount': loan_amount,
                'Loan_Amount_Term': loan_amount_term,
                'Credit_History': credit_history,
                'Property_Area': property_area_val
            }

            input_data   = pd.DataFrame([input_dict])[columns]
            input_scaled = scaler.transform(input_data)
            prediction   = model.predict(input_scaled)
            proba        = model.predict_proba(input_scaled)[0]

            result       = "Loan Approved" if prediction[0] == 1 else "Loan Rejected"
            result_class = "approved" if prediction[0] == 1 else "rejected"
            confidence   = round(max(proba) * 100, 1)

            return render_template('predict.html',
                                   prediction_text=result,
                                   result_class=result_class,
                                   confidence=confidence)
        except Exception as e:
            return render_template('predict.html',
                                   prediction_text=f"Error: {str(e)}",
                                   result_class="rejected",
                                   confidence=None)

    return render_template('predict.html')

@app.route('/introduction')
def introduction():
    return render_template('intro.html')

@app.route('/future_scope')
def future_scope():
    return render_template('future.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
