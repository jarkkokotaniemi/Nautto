from . import db

set_layouts = db.Table(
    "set_layouts",
    db.Column("set_id", db.Integer, db.ForeignKey("set.id"), primary_key=True),
    db.Column("layout_id", db.Integer, db.ForeignKey("layout.id"), primary_key=True)
)

layout_widgets = db.Table(
    "layout_widgets",
    db.Column("layout_id", db.Integer, db.ForeignKey("layout.id"), primary_key=True),
    db.Column("widget_id", db.Integer, db.ForeignKey("widget.id"), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=True)

    widgets = db.relationship("Widget", back_populates="user", cascade="all, delete-orphan")
    layouts = db.relationship("Layout", back_populates="user", cascade="all, delete-orphan")
    sets = db.relationship("Set", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f'{self.name} <{self.id}>'

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "type": "string"
        }
        props["name"] = {
            "description": "User's name",
            "type": "string"
        }
        props["description"] = {
            "description": "Description of the user",
            "type": "string"
        }
        return schema

class Set(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    user = db.relationship("User", back_populates="sets", uselist=False)
    layouts = db.relationship("Layout", secondary=set_layouts, back_populates="sets")

    def __repr__(self):
        return f'{self.name} <{self.id}>'
    
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "type": "string"
        }
        props["name"] = {
            "description": "Set's name",
            "type": "string"
        }
        props["description"] = {
            "description": "Description of the set",
            "type": "string"
        }
        props["items"] = {
            "description": "Layout ids of the set",
            "type": "array"
        }
        return schema

class Layout(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    user = db.relationship("User", back_populates="layouts", uselist=False)
    widgets = db.relationship("Widget", secondary=layout_widgets, back_populates="layouts")
    sets = db.relationship("Set", secondary=set_layouts, back_populates="layouts")

    def __repr__(self):
        return f'{self.name} <{self.id}>'
    
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "type": "string"
        }
        props["name"] = {
            "description": "Layout's name",
            "type": "string"
        }
        props["description"] = {
            "description": "Description of the layout",
            "type": "string"
        }
        props["items"] = {
            "description": "Widget ids of the layout",
            "type": "array"
        }
        return schema

class Widget(db.Model):
    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    type = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))

    user = db.relationship("User", back_populates="widgets", uselist=False)
    layouts = db.relationship("Layout", secondary=layout_widgets, back_populates="widgets")

    def __repr__(self):
        return f'{self.name} <{self.id}>'
    
    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "type", "content"]
        }
        props = schema["properties"] = {}
        props["id"] = {
            "type": "string"
        }
        props["name"] = {
            "description": "Widget's name",
            "type": "string"
        }
        props["description"] = {
            "description": "Description of the widget",
            "type": "string"
        }
        props["type"] = {
            "description": "Type of the widget",
            "type": "string"
        }
        props["content"] = {
            "description": "Content of the widget content",
            "type": "string"
        }
        return schema


import click
from flask.cli import with_appcontext

@click.command("db-init")
@with_appcontext
def db_init_cmd():
    db.create_all()
    print("done")

@click.command("db-drop")
@with_appcontext
def db_drop_cmd():
    db.drop_all()
    print("done")

@click.command("db-populate")
@with_appcontext
def db_populate_cmd():
    u1 = User(name="Mikko Mallikas")
    db.session.add(u1)
    u2 = User(name="Pasi Anssi")
    db.session.add(u2)
    
    w1 = Widget(
        type="HTML",
        name="widget1",
        content="<h1> Test Header </h1> <p> Testing widget 1 </p>",
        user=u1
    )
    db.session.add(w1)
    w2 = Widget(
        type="HTML",
        name="widget2",
        content="<h1> Test Header </h1> <p> Testing widget 2 </p>", 
        user=u2
    )
    db.session.add(w2)
    db.session.commit()

    l1 = Layout(
        user=u1,
        name="layout1"
    )
    l1.widgets.append(w1)
    l1.widgets.append(w2)
    db.session.add(l1)
    l2 = Layout(
        user=u2,
        name="layout2"
    )
    l2.widgets.append(w1)
    db.session.add(l2)

    s1 = Set(user=u1, name="set1")
    s1.layouts.append(l1)
    s1.layouts.append(l2)
    db.session.add(s1)
    s2 = Set(user=u2, name="set2")
    db.session.add(s2)

    db.session.commit()
    print("done")
    
