"""
Handles mapping
"""
from __future__ import absolute_import
import logging
import ordereddict
from collections import namedtuple
from seedbox.workflow import Taskflow

log = logging.getLogger(__name__)

# leverage namedtuple to hold ordered list with named attributes for
# simple and effective access while using lease amount of memory
_TaskInfo = namedtuple('TaskInfo', ['task', 'action'])
_Phase = namedtuple('Phase', ['name', 'tasks'])

# initialize the map to an empty ordered dictionary
# order will be important
_procmap = ordereddict.OrderedDict()

# using our defined Workflow and the related transistions/phases
# generate a list of phases (in order: see tuple) 
# based on existing configuration we will remove the last item which
# is the cancel phase which is not runnable ;-)
_run_phases = tuple([tran.name for tran in Taskflow.transitions][:-1])

# could use a function, but to avoid creating new variables over and over
# again just to access a name value of a state for a specified phase seemed
# overkill, so using a lambda. Provides a simple mapping of phase to state.
# based on configuration we know it is always only one related state
_phase_to_state = lambda phase: (Taskflow.transitions[phase]).source[0].name

_state_to_phase = lambda state: list(Taskflow.transitions.available_from(state))[0].name


def get_tasks(state):
    """
    retrieve the task details
    """
    return _procmap[state]


def get_state(phase):
    """
    determine my state
    """
    return _phase_to_state(phase)

def get_phase(state):
    """
    determine my phase
    """
    return _state_to_phase(state)

def get_run_phases():
    """
    Retrieves a list of run phases (ie those phases where execution can/will occur)

    args:
        N/A
    returns:
        an ordered tuple of phase names
    """
    return _run_phases

def init(phasemap):
    """
    initializes the map
    """

    for phase in phasemap.keys():                
        task_list = []
        for task in sorted(phasemap[phase], key=lambda plug: plug.phase_handlers[phase], reverse=True):
            task_list.append(_TaskInfo(task, task.phase_handlers[phase]))
        
        _procmap[_phase_to_state(phase)] = _Phase(phase, tuple(task_list))

    log.trace('proc_map = %s', _procmap)
