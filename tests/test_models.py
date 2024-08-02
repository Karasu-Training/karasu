import json
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.karasu.models.models import (
    Base,
    Exercise,
    Program,
    Block,
    Workout,
    Set
)


@pytest.fixture(scope='session')
def engine():
    return create_engine('sqlite://')


@pytest.fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    

@pytest.fixture
def session(engine, tables):
    conn = engine.connect()
    transaction = conn.begin()
    session = Session(bind=conn)

    yield session

    session.close()
    transaction.rollback()
    conn.close()


@pytest.fixture
def seed(session):
    program = Program(name='test_program')
    block = Block(days_per_week=4, name='block0')
    exercise = Exercise(name='SQUAT', movement='squat', classification='competition', targets=['quads', 'glutes'])
    workout = Workout()
    set = Set(exercise.id, reps=5, pct=0.6)

    workout.sets.append(set)
    block.workouts.append(workout)
    program.blocks.append(block)

    session.add_all([program, block, exercise, workout, set])
    session.commit()


class TestProgram:
    def test_program_valid(self, seed, session):
        program: Program = session.query(Program).one()
        assert program.id is not None
        assert len(program.blocks) == 1

    def test_block_valid(self, seed, session):
        block: Block = session.query(Block).one()
        assert block.id is not None
        assert block.days_per_week == 4
        assert len(block.workouts) == 1

    def test_programblock_append(self, seed, session):
        newBlock = Block(days_per_week=4, name='block1')
        program: Program = session.query(Program).one()
        program.blocks.append(newBlock)
        session.commit()

        # query for the program again
        program: Program = session.query(Program).one()
        assert len(program.blocks) == 2
        assert program.blocks[0].name == 'block0'
        assert program.blocks[1].name == 'block1'

    def test_programblock_insert(self, seed, session):
        newBlock = Block(days_per_week=4, name='block1')
        program: Program = session.query(Program).one()
        program.blocks.insert(0, newBlock)
        session.commit()

        program: Program = session.query(Program).one()
        assert len(program.blocks) == 2
        assert program.blocks[0].name == 'block1'
        assert program.blocks[1].name == 'block0'

    def test_exercise_valid(self, seed, session):
        transient_attrs = ['movement', 'classification', 'targets']
        exercise: Exercise = session.query(Exercise).one()

        col_names = [col.key for col in exercise.__table__.columns]
        assert all([attr not in col_names for attr in transient_attrs])
        assert exercise.movement == 'squat'
        assert exercise.classification == 'competition'
        assert len(exercise.targets) == 2

    def test_workout_valid(self, seed, session):
        workout: Workout = session.query(Workout).one()
        assert len(workout.sets) == 1

    def test_set_valid(self, seed, session):
        set: Set = session.query(Set).one()

        assert set.reps == 5
        assert set.pct == 0.6
