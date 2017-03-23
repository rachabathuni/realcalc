#!/usr/bin/python

import pickle
import math
import locale

SAVE_FILE = "/tmp/house.save"
PROP_TAX_PERCENT = 1.2

class MonthlyPayment:
	def __init__(self, month, payment, interest, principal, cumulativeInterest, cumulativePrincipal):
		self.payment = payment
		self.month = month
		self.interest = interest
		self.principal = principal
		self.cumulativeInterest = cumulativeInterest
		self.cumulativePrincipal = cumulativePrincipal

	def __str__(self):
		return "%d: %s, %s, %s, %s" % (self.month, self.interest, self.cumulativeInterest, self.principal, self.cumulativePrincipal)

def get_monthly_payment(loanAmt, annualInterestPercent, numPayments):
	monthlyInterest = annualInterestPercent / 12.0 / 100.0
	k = math.pow((monthlyInterest+1), numPayments)
	monthly = (monthlyInterest * loanAmt * k) / (k - 1)

	monthlyPayments = []
	cumulativePrincipal = 0
	cumulativeInterest = 0
	for i in xrange(0, int(numPayments)):
		remaining = loanAmt - cumulativePrincipal
		mIntAmt = remaining * monthlyInterest
		mPrinc = monthly - mIntAmt
		cumulativeInterest += mIntAmt
		cumulativePrincipal += mPrinc
		monthlyPayments.append(MonthlyPayment((i+1), monthly, mIntAmt, mPrinc, cumulativeInterest, cumulativePrincipal))

	return monthlyPayments


class Params:
	def __init__(self):
		self.price = 400000
		self.downPayment = 150000
		self.interestRate = 4.5
		self.rent = 2000
		self.propTaxPercent = PROP_TAX_PERCENT
		self.duration = 10
		self.expectedGrowthPercent = 10
		self.otherExpenses = 10000
		self.insurance = 1000
		self.managementPercent = 8
		self.loanYears = 30
		self.hoa = 300
		self.mortageTaxDeduction = "Y"
		self.sellingCostsPercent = 6
                self.sellingCostsExtra = 4000 # Closing costs etc.


def get_user_number(msg, default):
	while True:
		prompt = "%s [%s]: " % (msg, default)
		x = raw_input(prompt).strip()
		if x == "":
			return default
		try:
			return float(x)
		except:
			pass

def get_user_string(msg, default):
	while True:
		prompt = "%s [%s]: " % (msg, default)
		x = raw_input(prompt).strip()
		if x == "":
			return default
		return x

def load_params():
	try:
		f = open(SAVE_FILE, "r")
		if f:
			params = pickle.load(f)
			f.close()
		else:
			params = Params()
	except:
		params = Params()

	return params


def save_params(params):
	#try:
	f = open(SAVE_FILE, "w")
	pickle.dump(params, f)
	f.close()
	#except:
	#	print "Failed to save pickle"
	#	pass


##### MAIN ######

locale.setlocale(locale.LC_ALL, 'en_US')
	
params = load_params()
params.price = get_user_number("House price", params.price)
params.downPayment = get_user_number("Down payment", params.downPayment)
params.interestRate  = get_user_number("Interest rate", params.interestRate)
params.loanYears = get_user_number("Loan years", params.loanYears)
params.rent = get_user_number("Average monthly rent expected", params.rent)
params.insurance = get_user_number("Insurance per year", params.insurance)
params.managementPercent = get_user_number("Prop management %/month", params.managementPercent)
params.hoa = get_user_number("HOA per month", params.hoa)
params.otherExpenses = get_user_number("Other expenses per year", params.otherExpenses)
params.duration = get_user_number("How long do you plan to keep this property", params.duration)
params.expectedGrowthPercent = get_user_number("Expected growth percent in that time", params.expectedGrowthPercent)
params.mortageTaxDeduction = get_user_string("Is mortgage interest tax deductable (y/n)?", params.mortageTaxDeduction)
params.sellingCostsPercent = get_user_number("Selling costs %", params.sellingCostsPercent)
params.sellingCostsExtra = get_user_number("Selling Extra (closing etc.)", params.sellingCostsExtra)
params.propTaxPercent = PROP_TAX_PERCENT
save_params(params)

print "============"

durationMonths = params.duration*12
loan_amount = params.price-params.downPayment
monthly = get_monthly_payment(loan_amount, params.interestRate, params.loanYears*12)

#total_monthly = insurance + propmgmt + repairs + proptax
total_monthly = params.hoa + (params.insurance/12.0) + (params.rent * params.managementPercent /100) + (params.otherExpenses/12.0) \
						+ (((params.propTaxPercent * params.price)/100.0) / 12.0)
total_monthly_expense = monthly[0].payment + total_monthly

print "$%s: Monthly mortgage payment" % locale.format("%d", monthly[0].payment, grouping=True)
print "$%s: Total monthly expenses" % locale.format("%d", total_monthly_expense, grouping=True)
print "$%s: Monthly income" % locale.format("%d", params.rent, grouping=True)
print "$%s: Monthly cashflow" % locale.format("%d", params.rent-total_monthly_expense, grouping=True)

print "============"

if durationMonths >= params.loanYears*12:
	cumulativeInterest = monthly[int(params.loanYears*12-1)].cumulativeInterest 
	cumulativePrincipal = monthly[int(params.loanYears*12-1)].cumulativePrincipal
else:
	cumulativeInterest = monthly[int(durationMonths)].cumulativeInterest 
	cumulativePrincipal = monthly[int(durationMonths)].cumulativePrincipal

growth = params.price * params.expectedGrowthPercent / 100
sale_price = params.price + growth
selling_cost = sale_price*params.sellingCostsPercent/100 + params.sellingCostsExtra
total_income = (durationMonths * params.rent ) + growth
total_investment_cost = (total_monthly * durationMonths) + cumulativeInterest + selling_cost
if params.mortageTaxDeduction == "Y" or params.mortageTaxDeduction == "y":
	total_investment_cost = total_investment_cost - monthly[int(durationMonths)].cumulativeInterest*0.33
remaining_loan_amount = loan_amount - cumulativePrincipal 
cash_out = sale_price - remaining_loan_amount - selling_cost 

print "$%s: Interest in %d years" % (locale.format("%d", cumulativeInterest, grouping=True), params.duration)
print "$%s: Cost of invesement in %d years " % (locale.format("%d", total_investment_cost, grouping=True), params.duration)
print "$%s: Total income in %d years" % (locale.format("%d", params.rent * durationMonths, grouping=True), params.duration)
print "$%s: Total income with appreciation" % locale.format("%d",total_income, grouping=True)
print "$%s: Sale price" % locale.format("%d", sale_price, grouping=True)
print "$%s: Remaining loan at time of sale" % locale.format("%d", remaining_loan_amount, grouping=True)
print "$%s: Cash in hand at sale (after selling expenses)" % locale.format("%d", cash_out, grouping=True)
print "$%s: Net gain/loss"  % locale.format("%d", total_income - total_investment_cost, grouping=True)

print "============"

