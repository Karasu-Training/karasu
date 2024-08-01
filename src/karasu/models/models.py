from typing import List, Any
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from .base import Base


class Program(Base):
    __tablename__ = 'program'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    _blocks: Mapped[List['ProgramBlock']] = relationship(back_populates='program',
                                                         order_by='ProgramBlock.index',
                                                         collection_class=ordering_list('index'))
    blocks: AssociationProxy[List['Block']] = association_proxy('_blocks', 'block',
                                                                creator=lambda block: ProgramBlock(block=block))
    
    def __init__(self, name: str, id: UUID | None = None):
        self.id = id if id is not None else uuid4()
        self.name = name


class Block(Base):
    __tablename__ = 'block'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    days_per_week: Mapped[int]

    _workouts: Mapped[List['BlockWorkout']] = relationship(back_populates='block',
                                                           order_by='BlockWorkout.index',
                                                           collection_class=ordering_list('index'))
    workouts: AssociationProxy[List['Workout']] = association_proxy('_workouts', 'workout',
                                                                    creator=lambda workout: BlockWorkout(workout=workout))
    
    def __init__(self, days_per_week: int, id: UUID | None = None, name: str | None = None):
        self.id = id if id is not None else uuid4()
        self.days_per_week = days_per_week
        self.name = name


# TODO: decide if we can remove this class and store sets right under blocks
class Workout(Base):
    __tablename__ = 'workout'

    id: Mapped[UUID] = mapped_column(primary_key=True)

    _sets: Mapped[List['WorkoutSet']] = relationship(back_populates='workout',
                                                     order_by='WorkoutSet.index',
                                                     collection_class=ordering_list('index'))
    sets: AssociationProxy[List['Set']] = association_proxy('_sets', 'set',
                                                            creator=lambda set: WorkoutSet(set=set))
    
    def __init__(self, id: UUID | None = None):
        self.id = id if id is not None else uuid4()


class Set(Base):
    __tablename__ = 'set'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    exercise_id: Mapped[UUID] = mapped_column(ForeignKey('exercise.id'))

    reps: Mapped[int]
    pct: Mapped[float]

    def __init__(self, exercise_id: UUID, reps: int, pct: int, id: UUID | None = None):
        self.id = id if id is not None else uuid4()
        self.exercise_id = exercise_id
        self.reps = reps
        self.pct = pct


class Exercise(Base):
    __tablename__ = 'exercise'

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    object_data: Mapped[dict[str, Any]] = mapped_column(JSON(none_as_null=True))

    def __init__(self,
                 name: str,
                 movement: str,
                 classification: str,
                 targets: List[str],
                 id: UUID | None = None):
        self.id = id if id is not None else uuid4()
        self.name = name.upper()
        self.object_data = {
            'movement': movement,
            'classification': classification,
            'targets': targets
        }

    @property
    def movement(self):
        return self.object_data['movement']
    
    @property
    def classification(self):
        return self.object_data['classification']
    
    @property
    def targets(self):
        return self.object_data['targets']
    

class ProgramBlock(Base):
    __tablename__ = 'program_block'

    program_id: Mapped[UUID] = mapped_column(ForeignKey('program.id'), primary_key=True)
    block_id: Mapped[UUID] = mapped_column(ForeignKey('block.id'), primary_key=True)
    index: Mapped[int]

    program: Mapped['Program'] = relationship(back_populates='_blocks')
    block: Mapped['Block'] = relationship()


class BlockWorkout(Base):
    __tablename__ = 'block_workout'

    block_id: Mapped[UUID] = mapped_column(ForeignKey('block.id'), primary_key=True)
    workout_id: Mapped[UUID] = mapped_column(ForeignKey('workout.id'), primary_key=True)
    index: Mapped[int]

    block: Mapped['Block'] = relationship(back_populates='_workouts')
    workout: Mapped['Workout'] = relationship()


class WorkoutSet(Base):
    __tablename__ = 'workout_set'

    workout_id: Mapped[UUID] = mapped_column(ForeignKey('workout.id'), primary_key=True)
    set_id: Mapped[UUID] = mapped_column(ForeignKey('set.id'), primary_key=True)
    index: Mapped[int]
    complete: Mapped[bool] = mapped_column(default=False)
    rpe: Mapped[int | None]

    workout: Mapped['Workout'] = relationship(back_populates='_sets')
    set: Mapped['Set'] = relationship()
