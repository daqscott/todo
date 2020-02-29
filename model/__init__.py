# -*- coding: utf-8 -*-
from datetime import datetime

from flask.ext.migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref, relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

if 'db' not in locals() or 'db' not in globals():
    db = SQLAlchemy()

DATE_FORMAT = "%Y-%m-%d"

migrate = Migrate()


def get_id_column():
    return Column(Integer(), primary_key=True)


def get_name_column(length=32):
    return Column(String(length), unique=True, nullable=False)


def get_datetime_column(*args, default_now=False):
    if default_now:
        return Column(DateTime(), default=datetime.now(), *args)
    return Column(DateTime(), *args)


class BaseModel:
    def __repr__(self):  # FIXME: unit test
        ret = f"<{self.__class__.__name__}"
        if hasattr(self, "name"):
            ret += f"name=\"{self.name}\""
        if hasattr(self, "creation_date"):
            ret += f" creation_date={self.creation_date.strftime(DATE_FORMAT)}"
        ret += ">"
        return ret

    def __str__(self):
        if hasattr(self, "name"):
            return self.name
        return super.__str__(self)


class User(db.Model, BaseModel):
    """ The actor in our system. Can own task lists, create projects, and work on work days """
    user_id = get_id_column()
    name = get_name_column()
    creation_date = get_datetime_column(default_now=True)  # FIXME: make date


class Project(db.Model, BaseModel):
    """ A collection of tasks to comprise a larger project
    # TODO: describe columns
    """
    project_id = get_id_column()
    name = get_name_column(length=128)
    description = Column(String())
    user_id = Column(Integer(), ForeignKey("user.user_id"))
    git_branch = Column(String(128))
    creation_date = get_datetime_column(default_now=True)  # FIXME: make all these datetimes to date
    start_date = get_datetime_column()
    end_date = get_datetime_column()
    creator = relationship("User", backref="projects")
    tasks = relationship("Task", backref="project")
    # If this was truly multi user we might have a property for all users assigned to this project


class WorkDay(db.Model, BaseModel):
    """ Enumerate a tasks worked on a particular work day for a given user.
    # TODO: describe columns
    """
    work_day_id = get_id_column()
    # TODO: add date, make start_time, end_time time
    start_time = get_datetime_column(default_now=True)
    end_time = get_datetime_column()  # FIXME: make a constraint that guarantees this is on the same date as start time
    user_id = Column(Integer(), ForeignKey("user.user_id"))
    user = relationship("User", backref="work_days")
    tasks = relationship("Task", secondary="work_day_task", backref="work_days")

    def __repr__(self):
        ret = f"<{self.__class__.__name__} "
        # ret += f"user: {self.user} "
        ret += f"start_time: {self.start_time.strftime(DATE_FORMAT)}"
        ret += ">"
        return ret

    def __str__(self):
        return self.start_time.strftime(DATE_FORMAT)


class TodoList(db.Model, BaseModel):
    """ A list of tasks that a user is assigned to complete
    # TODO: describe columns
    """
    todo_list_id = get_id_column()
    name = get_name_column()
    user_id = Column(Integer(), ForeignKey("user.user_id"))
    creation_date = get_datetime_column(default_now=True)  # FIXME: make date
    user = relationship("User", backref="user")
    tasks = relationship("Task", backref="todo_list")  # For now a task can only appear on one Todo list


class Task(db.Model, BaseModel):
    """ An individual task which can be part of a work day, a todo list, and a project (all at the same time).
    If parent_id is populated this is a sub-task of another task item.

    TODO: describe all parameters
    """
    task_id = get_id_column()
    name = get_name_column()
    description = Column(String())
    notes = Column(String())
    parent_task_id = Column(Integer(), ForeignKey(task_id))
    parent_task = relationship("Task", remote_side=[task_id])
    project_id = Column(Integer(), ForeignKey("project.project_id"))  # tasks can only be assigned to one project
    todo_list_id = Column(Integer(), ForeignKey("todo_list.todo_list_id"))  # for now tasks can only be on one todo list
    creation_date = get_datetime_column(default_now=True)  # FIXME: REMOVE
    start_date = get_datetime_column()  # FIXME: make date
    end_date = get_datetime_column()  # FIXME: make data
    git_branch = Column(String(128))


class WorkDayTask(db.Model):
    work_day_id = Column(Integer, ForeignKey("work_day.work_day_id"), primary_key=True)
    task_id = Column(Integer, ForeignKey("task.task_id"), primary_key=True)
    task = relationship("Task")
