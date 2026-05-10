
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from .forms import LoginForm, SignupForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid email or password. Please try again.", "danger")
    return render_template("auth/login.html", form=form, title="Sign In")


@auth_bp.route("/demo-login", methods=["POST"])
def demo_login():
    demo_user = User.query.filter_by(email="demo@traveloop.com").first()
    if demo_user:
        login_user(demo_user)
        flash("Logged in as Guest (Demo User). Welcome!", "success")
        return redirect(url_for("dashboard.index"))
    flash("Demo user not found. Please run the seed script.", "danger")
    return redirect(url_for("auth.login"))


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Account created! Welcome to Traveloop, {user.name}!", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("auth/signup.html", form=form, title="Create Account")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login")
