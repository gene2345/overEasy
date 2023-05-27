from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Portfolio
from . import db
from .calc import numericChecker
import json
import yfinance as yf

views = Blueprint("views", __name__)

@views.route('/', methods = ['GET', 'POST']) #homepage
@login_required
def home():
    if request.method == 'POST':
        note1 = request.form.get('note')
        note1 = note1.upper()
        try:
            price = yf.Ticker(note1).info['regularMarketPreviousClose']
            new_note = Note(data=note1, user_id = current_user.id, price = price)
            db.session.add(new_note)
            db.session.commit()
            flash("Added", category = "success")
        except:
            flash('Stock does not exist', category = "error")
    for items in Note.query:
        items.price = yf.Ticker(items.data).info['regularMarketPreviousClose']
        db.session.commit()
    return render_template("home.html", user = current_user)


@login_required
@views.route('/delete/<int:id>') #deleting an extra stock
def delete(id):
    note = Note.query.get(id)
    if note:
        db.session.delete(note)
        db.session.commit()
        flash("Deleted", category = "success")
    return redirect('/')

@login_required
@views.route('/CCA')
def CCA():
    return render_template("CCA.html", user = current_user)

@login_required
@views.route('/yrport', methods = ['GET', 'POST'])
def yrport():   
    if request.method == 'POST':
        stock1 = request.form.get('stock')
        stock1 = stock1.upper()
        bought_price = request.form.get('bought_price')
        bought_qty = request.form.get('bought_qty')
        if numericChecker(bought_price):
            flash("Please re enter price", category="error")
            return render_template("yrport.html", user = current_user)
        elif numericChecker(bought_qty):
            flash("Please re enter quantity", category="error")
            return render_template("yrport.html", user = current_user)
        try:
            price = yf.Ticker(stock1).info['regularMarketPreviousClose']
            profitloss = round((float(bought_price) - float(price))*float(bought_qty),2)
            new_stock = Portfolio(data=stock1, user_id = current_user.id, bought_price = bought_price, 
                                      bought_qty = bought_qty, current_price = price, profitloss = profitloss)
            db.session.add(new_stock)
            db.session.commit()
            flash("Added", category = "success")
        except:
            flash('Stock does not exist', category = "error")
    for items in Portfolio.query:
        new_price = yf.Ticker(items.data).info['regularMarketPreviousClose']
        items.current_price = new_price
        items.profitloss = round((float(new_price) - float(items.bought_price)) * float(items.bought_qty),2)
        db.session.commit()
            
    return render_template("yrport.html", user = current_user)

@login_required
@views.route('/deleteyrport/<int:id>') #deleting an extra stock
def deleteyrport(id):
    portfolio = Portfolio.query.get(id)
    if portfolio:
        db.session.delete(portfolio)
        db.session.commit()
        flash("deleted", category = "success")
    return redirect('/yrport')

@login_required
@views.route('/SA')
def SA():
    return render_template("SA.html", user = current_user)