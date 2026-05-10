import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, logout_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from werkzeug.utils import secure_filename
from app.models import db, User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    language_pref = SelectField(
        "Language",
        choices=[("hi", "Hindi"), ("en", "English"), ("ta", "Tamil"), ("te", "Telugu"), ("bn", "Bengali"), ("mr", "Marathi")],
    )
    profile_photo = FileField("Profile Photo", validators=[FileAllowed(["jpg", "jpeg", "png", "gif", "webp"])])
    submit = SubmitField("Save Changes")


@profile_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = ProfileForm(obj=current_user)
    # Clear file field since it can't be pre-populated from the model
    if request.method == "GET":
        form.profile_photo.data = None
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data.lower()
        current_user.language_pref = form.language_pref.data
        photo = form.profile_photo.data
        # FileStorage object when file uploaded, empty string or None otherwise
        if photo and hasattr(photo, 'filename') and photo.filename:
            filename = secure_filename(photo.filename)
            unique_name = f"{os.urandom(8).hex()}_{filename}"
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name))
            current_user.profile_photo = unique_name
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.settings"))
    return render_template("profile/settings.html", title="Profile Settings", form=form)


@profile_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Your account has been deleted.", "info")
    return redirect(url_for("auth.signup"))
