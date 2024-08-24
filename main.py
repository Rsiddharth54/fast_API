from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI()

# Smpty lists
employees = []
employers = []
payroll_periods = []
wage_and_hours = []
earnings = []
withholdings_and_deductions = []
net_pays = []
tax_reportings = []

# Pydantic Models
class Employee(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    social_security_number: str
    date_of_birth: date
    address: str
    city: str
    state: str
    zip_code: str
    hire_date: date
    position: str
    employment_status: str
    exempt_status: bool
    pay_type: str
    department: str

class Employer(BaseModel):
    employer_id: str
    company_name: str
    federal_ein: str
    state_tax_id: str
    local_tax_id: str
    address: str
    city: str
    state: str = "PA"
    zip_code: str
    payroll_frequency: str

class PayrollPeriod(BaseModel):
    payroll_period_id: str
    employer_id: str
    start_date: date
    end_date: date
    pay_date: date

class WageAndHours(BaseModel):
    wage_hours_id: str
    employee_id: str
    payroll_period_id: str
    regular_hours: float
    overtime_hours: float
    overtime_rate: float = 1.5  # Pennsylvania overtime rule: 1.5x pay for hours over 40/week
    shift_differential: Optional[float] = None

class Earnings(BaseModel):
    earnings_id: str
    employee_id: str
    payroll_period_id: str
    gross_earnings: float
    regular_wages: float
    overtime_wages: float
    bonuses: Optional[float] = 0.0
    commissions: Optional[float] = 0.0
    total_gross: float

class WithholdingsAndDeductions(BaseModel):
    deduction_id: str
    employee_id: str
    payroll_period_id: str
    federal_income_tax: float
    state_income_tax: float = 3.07  # Pennsylvania flat rate of 3.07%
    local_income_tax: float  # This varies by jurisdiction
    social_security: float = 6.2  # Standard rate
    medicare: float = 1.45  # Standard rate
    additional_medicare: Optional[float] = 0.0
    unemployment_insurance: float
    other_withholdings: Optional[float] = 0.0
    voluntary_deductions: Optional[float] = 0.0
    total_deductions: float

class NetPay(BaseModel):
    net_pay_id: str
    employee_id: str
    payroll_period_id: str
    total_gross: float
    total_deductions: float
    net_pay: float
    payment_method: str

class TaxReporting(BaseModel):
    report_id: str
    employer_id: str
    payroll_period_id: str
    filing_type: str  # Quarterly, Monthly, Semi-Monthly, Semi-Weekly (as per PA rules)
    filing_due_date: date
    filing_status: str

# Example routes for Pennsylvania-specific rules and regulations

@app.post("/employee/", response_model=Employee)
def create_employee(employee: Employee):
    employees.append(employee)
    return employee

@app.get("/employee/{employee_id}", response_model=Employee)
def get_employee(employee_id: str):
    for employee in employees:
        if employee.employee_id == employee_id:
            return employee
    raise HTTPException(status_code=404, detail="Employee not found")

@app.get("/employees/", response_model=List[Employee])
def list_employees():
    return employees

@app.post("/employer/", response_model=Employer)
def create_employer(employer: Employer):
    employers.append(employer)
    return employer

@app.get("/employer/{employer_id}", response_model=Employer)
def get_employer(employer_id: str):
    for employer in employers:
        if employer.employer_id == employer_id:
            return employer
    raise HTTPException(status_code=404, detail="Employer not found")

# Adding more routes for payroll processing and tax reporting

@app.post("/payroll_period/", response_model=PayrollPeriod)
def create_payroll_period(payroll_period: PayrollPeriod):
    payroll_periods.append(payroll_period)
    return payroll_period

@app.post("/wage_hours/", response_model=WageAndHours)
def record_wage_hours(wage_hours: WageAndHours):
    wage_and_hours.append(wage_hours)
    return wage_hours

@app.post("/earnings/", response_model=Earnings)
def calculate_earnings(earnings: Earnings):
    earnings.total_gross = earnings.regular_wages + earnings.overtime_wages + earnings.bonuses + earnings.commissions
    earnings.append(earnings)
    return earnings

@app.post("/withholdings/", response_model=WithholdingsAndDeductions)
def calculate_withholdings(withholdings: WithholdingsAndDeductions):
    withholdings.total_deductions = (withholdings.federal_income_tax +
                                     withholdings.state_income_tax +
                                     withholdings.local_income_tax +
                                     withholdings.social_security +
                                     withholdings.medicare +
                                     withholdings.additional_medicare +
                                     withholdings.unemployment_insurance +
                                     withholdings.other_withholdings +
                                     withholdings.voluntary_deductions)
    withholdings_and_deductions.append(withholdings)
    return withholdings

@app.post("/net_pay/", response_model=NetPay)
def calculate_net_pay(net_pay: NetPay):
    net_pay.net_pay = net_pay.total_gross - net_pay.total_deductions
    net_pays.append(net_pay)
    return net_pay

@app.post("/tax_reporting/", response_model=TaxReporting)
def record_tax_report(tax_report: TaxReporting):
    tax_reportings.append(tax_report)
    return tax_report

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Pennsylvania Payroll System API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
