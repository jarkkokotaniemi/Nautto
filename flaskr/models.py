import click
from flask.cli import with_appcontext
from flaskr import db


class Widget(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    type = db.Column(db.String(), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))

    layout = db.relationship("Layout", back_populates="widgets")


class Layout(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    widget_id = db.Column(db.Integer, db.ForeignKey("widget.id", ondelete="SET NULL"))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))

    widgets = db.relationship("Widget", back_populates="layout")
    sets = db.relationship("Set", back_populates="layouts")


class Set(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    layout_id = db.Column(db.Integer, db.ForeignKey("layout.id", ondelete="SET NULL"))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"))

    layouts = db.relationship("Layout", back_populates="sets")


class User(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(120), nullable=False)


    widgets = db.relationship("Widget")
    layouts = db.relationship("Layout")
    sets = db.relationship("Set")


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()


@click.command("test-gen")
@with_appcontext
def gen_test_data():
    u1 = User(
        name="Mikko Mallikas"
    )
    db.session.add(u1)
    u2 = User(
        name="Pasi Anssi"
    )
    db.session.add(u2)

    w1 = Widget(
        type="HTML",
        content="<h1> Test Header </h1> <p> Testing widget 1 </p>",
        created_by=u1
    )
    db.session.add(w1)
    w2 = Widget(
        type="HTML",
        content="<h1> Test Header </h1> <p> Testing widget 2 </p>",
        created_by=u1
    )
    db.session.add(w2)

    l1 = Layout(
        created_by=u1,
        widgets=[w1, w2]
    )
    db.session.add(l1)
    l2 = Layout(
        created_by=u2,
        widgets=[w1]
    )
    db.session.add(l2)

    s1 = Set(
        created_by=u1,
        layouts=[l1, l2]
    )
    db.session.add(s1)
    s2 = Set(
        created_by=u2,
        layouts=[]
    )
    db.session.add(s2)

    db.session.commit()
    
