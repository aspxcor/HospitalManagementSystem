from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, json, Response,flash, url_for, redirect, render_template, jsonify, make_response, session
import config, hashlib
from datetime import datetime, timedelta
from sqlalchemy import extract, or_,and_,create_engine
from sqlalchemy.orm import aliased
import pandas as pd
from requests import Request, Session
from flask_paginate import Pagination, get_page_parameter
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
db.create_all()
Session = sessionmaker(create_engine(config.SQLALCHEMY_DATABASE_URI))()
# 类定义开始
class User(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    name = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    isAdmin = db.Column(db.Integer)
    jobTitle = db.Column(db.String)
    sex = db.Column(db.String)
    birthday = db.Column(db.DATE)
    telephoneNum = db.Column(db.String)
    wechat = db.Column(db.String)
    mail = db.Column(db.String)
    qq = db.Column(db.String)
    def __init__(self, row_id, id, name, username, password, isAdmin, jobTitle, sex, birthday, telephoneNum, wechat, mail, qq):
        self.row_id = row_id
        self.id = id
        self.name = name
        self.username = username
        self.password = password
        self.isAdmin = isAdmin
        self.jobTitle = jobTitle
        self.sex = sex
        self.birthday = birthday
        self.telephoneNum = telephoneNum
        self.wechat = wechat
        self.mail = mail
        self.qq = qq
class Patients(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    name = db.Column(db.String)
    gender = db.Column(db.String)
    dob = db.Column(db.DateTime)
    dod = db.Column(db.DateTime)
    dod_hosp = db.Column(db.DateTime)
    dod_ssn = db.Column(db.DateTime)
    expire_flag = db.Column(db.Integer)
    def __init__(self, row_id, subject_id, name, gender, dob, dod, dod_hosp, dod_ssn, expire_flag):
        self.row_id = row_id
        self.subject_id = subject_id
        self.name = name
        self.gender = gender
        self.dob = dob
        self.dod = dod
        self.dod_hosp = dod_hosp
        self.dod_ssn = dod_ssn
        self.expire_flag = expire_flag
class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drug = db.Column(db.String)
    drug_name_poe = db.Column(db.String)
    drug_type = db.Column(db.String)
    inventory = db.Column(db.Integer)
    def __init__(self, drug, drug_name_poe, drug_type, inventory):
        self.drug = drug
        self.drug_name_poe = drug_name_poe
        self.drug_type = drug_type
        self.inventory = inventory
class Admissions(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    admittime = db.Column(db.DateTime)
    dischtime = db.Column(db.DateTime)
    deathtime = db.Column(db.DateTime)
    admission_type = db.Column(db.String)
    admission_location = db.Column(db.String)
    discharge_location = db.Column(db.String)
    insurance = db.Column(db.String)
    language = db.Column(db.String)
    religion = db.Column(db.String)
    marital_status = db.Column(db.String)
    ethnicity = db.Column(db.String)
    edregtime = db.Column(db.DateTime)
    edouttime = db.Column(db.DateTime)
    diagnosis = db.Column(db.String)
    hospital_expire_flag = db.Column(db.Integer)
    has_chartevents_data = db.Column(db.Integer)
    def __init__(self, row_id, subject_id, hadm_id, admittime, dischtime, deathtime, admission_type, admission_location, discharge_location, insurance, language, religion, marital_status, ethnicity, edregtime, edouttime, diagnosis, hospital_expire_flag, has_chartevents_data):
        self.row_id = row_id
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.admittime = admittime
        self.dischtime = dischtime
        self.deathtime = deathtime
        self.admission_type = admission_type
        self.admission_location = admission_location
        self.discharge_location = discharge_location
        self.insurance = insurance
        self.language = language
        self.religion = religion
        self.marital_status = marital_status
        self.ethnicity = ethnicity
        self.edregtime = edregtime
        self.edouttime = edouttime
        self.diagnosis = diagnosis
        self.hospital_expire_flag = hospital_expire_flag
        self.has_chartevents_data = has_chartevents_data
class Prescription(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    icustay_id = db.Column(db.Integer)
    startdate = db.Column(db.DateTime)
    enddate = db.Column(db.DateTime)
    drug_type = db.Column(db.String)
    drug = db.Column(db.String)
    drug_name_poe = db.Column(db.String)
    drug_name_generic = db.Column(db.String)
    formulary_drug_cd = db.Column(db.String)
    gsn = db.Column(db.Integer)
    ndc = db.Column(db.Integer)
    prod_strength = db.Column(db.String)
    dose_val_rx = db.Column(db.String)
    dose_unit_rx = db.Column(db.String)
    form_val_disp = db.Column(db.String)
    form_unit_disp = db.Column(db.String)
    route = db.Column(db.String)
    def __init__(self, row_id, subject_id, hadm_id, icustay_id, startdate, enddate, drug_type, drug, drug_name_poe, drug_name_generic, formulary_drug_cd, gsn, ndc, prod_strength, dose_val_rx, dose_unit_rx, form_val_disp, form_unit_disp, route):
        self.row_id = row_id
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.icustay_id = icustay_id
        self.startdate = startdate
        self.enddate = enddate
        self.drug_type = drug_type
        self.drug = drug
        self.drug_name_poe = drug_name_poe
        self.drug_name_generic = drug_name_generic
        self.formulary_drug_cd = formulary_drug_cd
        self.gsn = gsn
        self.ndc = ndc
        self.prod_strength = prod_strength
        self.dose_val_rx = dose_val_rx
        self.dose_unit_rx = dose_unit_rx
        self.form_val_disp = form_val_disp
        self.form_unit_disp = form_unit_disp
        self.route = route
class Labevents(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    itemid = db.Column(db.Integer)
    charttime = db.Column(db.DateTime)
    value = db.Column(db.String)
    valuenum = db.Column(db.String)
    valueuom = db.Column(db.String)
    flag = db.Column(db.String)
    def __init__(self, row_id, subject_id, hadm_id, itemid, charttime, value, valuenum, valueuom, flag):
        self.row_id = row_id
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.itemid = itemid
        self.charttime = charttime
        self.value = value
        self.valuenum = valuenum
        self.valueuom = valueuom
        self.flag = flag
class Datatimeevent(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    icustay_id = db.Column(db.Integer)
    itemid = db.Column(db.Integer)
    charttime = db.Column(db.DateTime)
    storetime = db.Column(db.DateTime)
    cgid = db.Column(db.Integer)
    value = db.Column(db.DateTime)
    valueuom = db.Column(db.String)
    warning = db.Column(db.Integer)
    error = db.Column(db.Integer)
    resultstatus = db.Column(db.String)
    stopped = db.Column(db.String)
    def __init__(self, row_id, subject_id, hadm_id, icustay_id, itemid, charttime, storetime, cgid, value, valueuom, warning, error, resultstatus, stopped):
        self.row_id = row_id
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.icustay_id = icustay_id
        self.itemid = itemid
        self.charttime = charttime
        self.storetime = storetime
        self.cgid = cgid
        self.value = value
        self.valueuom = valueuom
        self.warning = warning
        self.error = error
        self.resultstatus = resultstatus
        self.stopped = stopped
class DLabitems(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    itemid = db.Column(db.Integer)
    label = db.Column(db.String)
    fluid = db.Column(db.String)
    category = db.Column(db.String)
    loinc_code = db.Column(db.String)
    def __init__(self, row_id, itemid, label, fluid, category, loinc_code):
        self.row_id = row_id
        self.itemid = itemid
        self.label = label
        self.fluid  = fluid
        self.category = category
        self.loinc_code = loinc_code
class DCpt(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer)
    sectionrange = db.Column(db.String)
    sectionheader = db.Column(db.String)
    subsectionrange = db.Column(db.String)
    subsectionheader = db.Column(db.String)
    codesuffix = db.Column(db.String)
    mincodeinsubsection = db.Column(db.Integer)
    maxcodeinsubsection = db.Column(db.Integer)
    def __init__(self, row_id, category, sectionrange, sectionheader, subsectionrange, subsectionheader, codesuffix, mincodeinsubsection, maxcodeinsubsection):
        self.row_id = row_id
        self.category = category
        self.sectionrange = sectionrange
        self.sectionheader = sectionheader
        self.subsectionrange = subsectionrange
        self.subsectionheader = subsectionheader
        self.codesuffix = codesuffix
        self.mincodeinsubsection = mincodeinsubsection
        self.maxcodeinsubsection = maxcodeinsubsection
class Cpt(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    hadm_id = db.Column(db.Integer)
    costcenter = db.Column(db.String)
    chartdate = db.Column(db.DateTime)
    cpt_cd = db.Column(db.Integer)
    cpt_number = db.Column(db.Integer)
    cpt_suffix = db.Column(db.String)
    ticket_id_seq = db.Column(db.Integer)
    sectionheader = db.Column(db.String)
    subsectionheader = db.Column(db.String)
    description = db.Column(db.String)
    def __init__(self, row_id, subject_id, hadm_id, costcenter, chartdate, cpt_cd, cpt_number, cpt_suffix, ticket_id_seq, sectionheader, subsectionheader, description):
        self.row_id = row_id
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.costcenter = costcenter
        self.chartdate = chartdate
        self.cpt_cd = cpt_cd
        self.cpt_number = cpt_number
        self.cpt_suffix = cpt_suffix
        self.ticket_id_seq = ticket_id_seq
        self.sectionheader = sectionheader
        self.subsectionheader = subsectionheader
        self.description = description