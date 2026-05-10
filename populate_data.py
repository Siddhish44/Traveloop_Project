import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prince_portfolio.settings')
django.setup()

from portfolio.models import Profile, Skill, Project, Education
from datetime import date

# Clear existing data
Profile.objects.all().delete()
Skill.objects.all().delete()
Project.objects.all().delete()
Education.objects.all().delete()

# Create Profile
Profile.objects.create(
    name="Prince Raj Kiran",
    bio="I am a B.Tech CSE student passionate about Software Development. I see my future in Python-related technologies and building scalable web applications.",
    email="princeofficial0805@gmail.com",
    linkedin="https://www.linkedin.com/in/princerajkiranofficial/",
    github="https://github.com/PrinceRajKiranOfficial"
)

# Create Skills
skills = [
    ("Python", 90, "fab fa-python"),
    ("Django", 85, "fas fa-layer-group"),
    ("HTML5", 95, "fab fa-html5"),
    ("CSS3", 80, "fab fa-css3-alt"),
    ("JavaScript", 70, "fab fa-js"),
    ("SQL", 75, "fas fa-database"),
    ("Git", 80, "fab fa-git-alt"),
]

for name, prof, icon in skills:
    Skill.objects.create(name=name, proficiency=prof, icon_class=icon)

# Create Education
Education.objects.create(
    institution="University/College Name",
    degree="B.Tech Computer Science & Engineering",
    start_date=date(2023, 1, 1), # Approximate
    description="Studying core computer science subjects including Data Structures, Algorithms, and Web Development."
)

# Create Projects
Project.objects.create(
    title="Portfolio Website",
    description="A fully responsive portfolio website built with Django and vanilla CSS, featuring a modern dark theme and glassmorphism design.",
    technologies="Django, Python, CSS, HTML",
    github_link="https://github.com/princerajkiran/portfolio"
)

Project.objects.create(
    title="Python Automation Scripts",
    description="A collection of Python scripts to automate daily tasks, including file organization and web scraping.",
    technologies="Python, BeautifulSoup, Selenium",
    github_link="https://github.com/princerajkiran/scripts"
)

print("Data populated successfully!")
