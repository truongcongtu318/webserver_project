from flask import Blueprint, render_template
import os

views = Blueprint('views',__name__, template_folder='templates')

@views.route('/')
def signup():
    return render_template("signup.html")


@views.route('/home')
def login():
    return render_template("home.html")