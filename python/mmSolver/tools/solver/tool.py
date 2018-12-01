"""
Solver tool functions - everything the solver tool can do.
"""

import uuid

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.selection.filternodes as filternodes
import mmSolver.tools.solver.constant as const
import mmSolver.tools.solver.scene_data as scene_data
import mmSolver.tools.solver.solver_step as solver_step


LOG = mmSolver.logger.get_logger()


def _get_channel_box_ui_name():
    cmd = (
        'global string $gChannelBoxName;'
        'string $temp = $gChannelBoxName;'
    )
    return maya.mel.eval(cmd)


def _get_selected_attributes():
    name = _get_channel_box_ui_name()
    attrs = maya.cmds.channelBox(
        name, query=True,
        selectedMainAttributes=True
    ) or []
    return attrs


def set_scene_selection(nodes):
    maya.cmds.select(nodes, replace=True)
    return


def get_current_frame():
    time = maya.cmds.currentTime(query=True)
    return int(time)


def get_timeline_range_inner():
    s = maya.cmds.playbackOptions(query=True, minTime=True)
    e = maya.cmds.playbackOptions(query=True, maxTime=True)
    return int(s), int(e)


def get_timeline_range_outer():
    s = maya.cmds.playbackOptions(query=True, animationStartTime=True)
    e = maya.cmds.playbackOptions(query=True, animationEndTime=True)
    return int(s), int(e)


def prompt_for_new_node_name(title, message, text):
    name = None
    result = maya.cmds.promptDialog(
        title=title,
        message=message,
        text=text,
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
    )
    if result == 'OK':
        name = maya.cmds.promptDialog(query=True, text=True)
    return name


def get_markers_from_selection():
    """
    Given a selection of nodes, find the associated markers.

    :return: list of Marker objects.
    """
    nodes = maya.cmds.ls(long=True, selection=True) or []
    node_categories = filternodes.get_nodes(nodes)
    marker_nodes = list(node_categories['marker'])

    camera_nodes = list(node_categories['camera'])
    for node in camera_nodes:
        tfm_node = None
        if maya.cmds.nodeType(node) == 'camera':
            cam = mmapi.Camera(shape=node)
            tfm_node = cam.get_transform_node()
        below_nodes = maya.cmds.ls(tfm_node, dag=True, long=True)
        marker_nodes += filternodes.get_marker_nodes(below_nodes)

    marker_group_nodes = list(node_categories['markergroup'])
    for node in marker_group_nodes:
        below_nodes = maya.cmds.ls(node, dag=True, long=True)
        marker_nodes += filternodes.get_marker_nodes(below_nodes)

    # Convert nodes into Marker objects.
    marker_nodes = list(set(marker_nodes))
    marker_list = []
    for node in marker_nodes:
        mkr = mmapi.Marker(name=node)
        marker_list.append(mkr)
    return marker_list


def get_selected_maya_attributes():
    attrs = _get_selected_attributes()
    nodes = maya.cmds.ls(sl=True, long=True)
    attr_list = []
    for n in nodes:
        for a in attrs:
            attr = mmapi.Attribute(node=n, attr=a)
            if attr.get_name() is not None:
                attr_list.append(attr)
    return attr_list


def get_active_collection():
    uid = scene_data.get_scene_data(const.SCENE_DATA_ACTIVE_COLLECTION_UID)
    if uid is None:
        return None
    nodes = maya.cmds.ls(uid, long=True) or []
    col = None
    if len(nodes) > 0:
        col = mmapi.Collection(name=nodes[0])
    return col


def set_active_collection(col):
    uid = col.get_node_uid()
    if uid is None:
        return
    scene_data.set_scene_data(const.SCENE_DATA_ACTIVE_COLLECTION_UID, uid)
    return


def get_collections():
    nodes = maya.cmds.ls(type='objectSet', long=True) or []
    node_categories = filternodes.get_nodes(nodes)
    cols = []
    for col_node in node_categories['collection']:
        col = mmapi.Collection(name=col_node)
        cols.append(col)
    return cols


def create_collection():
    col = mmapi.Collection().create_node('collection1')
    sol = create_solver()
    add_solver_to_collection(sol, col)
    ensure_solver_steps_attr_exists(col)
    step = create_solver_step()
    add_solver_step_to_collection(col, step)
    return col


def rename_collection(col, new_name):
    if col is None:
        msg = 'rename_collection: Can not rename, collection invalid.'
        LOG.warning(msg)
        return
    node = col.get_node()
    if node is None or maya.cmds.objExists(node) is False:
        msg = 'rename_collection: Can not rename, node invalid.'
        LOG.warning(msg)
        return
    maya.cmds.rename(node, new_name)
    return


def delete_collection(col):
    LOG.debug('delete_collection: %r', col)
    if col is None:
        return
    node = col.get_node()
    LOG.debug('delete_collection1: %r', node)
    node = str(node)
    LOG.debug('delete_collection2: %r', node)
    del col
    LOG.debug('delete_collection3: %r', node)
    maya.cmds.delete(node)
    return


def select_collection(col):
    if col is None:
        LOG.debug('no collection given, cannot select: %r', col)
        return
    node_uid = col.get_node_uid()
    LOG.debug('select_collection node_uid=%r', node_uid)
    if node_uid is None:
        return
    node = maya.cmds.ls(node_uid)
    LOG.debug('select_collection node=%r', node)
    if node is None:
        return
    #TODO: For some strange reason, when selecting a 'set', the objects within
    # the set also get selected, which is not what the command is being told to
    # do.
    maya.cmds.select(clear=True)
    maya.cmds.select(node, ne=True)
    LOG.debug('select_collection select')
    return


def create_marker():
    raise NotImplementedError


def convert_to_marker():
    raise NotImplementedError


def add_markers_to_collection(mkr_list, col):
    if isinstance(col, mmapi.Collection) is False:
        msg = 'col argument must be a Collection: %r'
        raise TypeError(msg % col)
    col.add_marker_list(mkr_list)
    return


def remove_markers_from_collection(mkr_list, col):
    return col.remove_marker_list(mkr_list)


def get_markers_from_collection(col):
    return col.get_marker_list()


def get_attributes_from_collection(col):
    return col.get_attribute_list()


def add_attributes_to_collection(attr_list, col):
    return col.add_attribute_list(attr_list)


def remove_attr_from_collection(attr_list, col):
    return col.remove_attribute_list(attr_list)


def get_ui_node_from_index(idx, filter_model):
    if idx.isValid() is False:
        return None
    idx_map = filter_model.mapToSource(idx)
    ui_node = idx_map.internalPointer()
    return ui_node


def get_selected_ui_nodes(tree_view, filter_model):
    node_list = []
    sel_model = tree_view.selectionModel()
    selection = sel_model.selection()
    index_list = selection.indexes()
    for idx in index_list:
        ui_node = get_ui_node_from_index(idx, filter_model)
        if ui_node is None:
            continue
        node_list.append(ui_node)
    return node_list


def get_selected_ui_table_row(tree_view, model, filter_model):
    node_list = []
    sel_model = tree_view.selectionModel()
    selection = sel_model.selection()
    index_list = selection.indexes()
    all_node_list = model.nodeList()
    for idx in index_list:
        if idx.isValid() is False:
            continue
        idx_map = filter_model.mapToSource(idx)
        row = idx.row()
        ui_node = all_node_list[row]
        if ui_node is None:
            continue
        node_list.append(ui_node)
    return node_list


def convert_ui_nodes_to_nodes(ui_nodes, key):
    nodes = []
    for ui_node in ui_nodes:
        node_data = ui_node.data()
        if node_data is None:
            continue
        mkr_node = node_data.get(key)
        if mkr_node is None:
            continue
        nodes.append(mkr_node)
    return nodes


def create_solver():
    sol = mmapi.Solver()
    sol.set_max_iterations(10)
    sol.set_verbose(True)
    start, end = get_timeline_range_inner()
    for f in xrange(start, end + 1):
        frm = mmapi.Frame(f)
        sol.add_frame(frm)
    return sol


def get_solvers_from_collection(col):
    sol_list = col.get_solver_list()
    return sol_list


def add_solver_to_collection(sol, col):
    return col.add_solver(sol)


def remove_solver_from_collection(sol, col):
    return col.remove_solver(sol)


def create_solver_step():
    data = const.SOLVER_STEP_DATA_DEFAULT.copy()

    data['name'] = str(uuid.uuid4())

    start, end = get_timeline_range_inner()
    frame_list = list(xrange(start, end + 1))
    data['frame_list'] = frame_list

    step = solver_step.SolverStep(data=data)
    return step


def ensure_solver_steps_attr_exists(col):
    node = col.get_node()
    attr_name = const.SOLVER_STEP_ATTR
    attrs = maya.cmds.listAttr(node)
    if attr_name in attrs:
        return
    maya.cmds.addAttr(
        node,
        longName=attr_name,
        dataType='string'
    )
    maya.cmds.setAttr(
        node + '.' + attr_name,
        lock=True
    )
    return


def get_solver_steps_from_collection(col):
    """
    Load all steps from collection.
    """
    node = col.get_node()
    ensure_solver_steps_attr_exists(col)
    data_list = mmapi.get_data_on_node_attr(node, const.SOLVER_STEP_ATTR)
    step_list = map(lambda x: solver_step.SolverStep(x), data_list)
    return step_list


def get_named_solver_step_from_collection(col, name):
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    if name not in name_list:
        msg = 'SolverStep %r could not be found in all steps: %r'
        LOG.warning(msg, name, name_list)
        return None
    idx = name_list.index(name)
    return step_list[idx]


def set_named_solver_step_to_collection(col, step):
    name = step.get_name()
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    if name not in name_list:
        raise ValueError
    idx = list(name_list).index(name)
    step_list.pop(idx)
    step_list.insert(idx, step)
    set_solver_step_list_to_collection(col, step_list)
    return


def add_solver_step_to_collection(col, step):
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    name = step.get_name()
    if name in name_list:
        raise ValueError
    step_list.insert(0, step)  # new step pushed onto the front.
    set_solver_step_list_to_collection(col, step_list)
    return


def remove_solver_step_from_collection(col, step):
    if step is None:
        msg = 'Cannot remove SolverStep, step is invalid.'
        LOG.warning(msg)
        return
    step_list = get_solver_steps_from_collection(col)
    name_list = map(lambda x: x.get_name(), step_list)
    name = step.get_name()
    if name not in name_list:
        raise ValueError
    idx = list(name_list).index(name)
    step_list.pop(idx)
    set_solver_step_list_to_collection(col, step_list)
    return


def set_solver_step_list_to_collection(col, step_list):
    node = col.get_node()
    data_list = map(lambda x: x.get_data(), step_list)
    ensure_solver_steps_attr_exists(col)
    mmapi.set_data_on_node_attr(node, const.SOLVER_STEP_ATTR, data_list)
    compile_solvers(col)
    return


def create_frame_list_from_int_list(int_list):
    return map(lambda x: mmapi.Frame(x), int_list)


def compile_solvers(col, prog_fn=None):
    sol_list = []
    step_list = get_solver_steps_from_collection(col)
    for step in step_list:
        tmp_list = step.compile()
        sol_list += tmp_list
    col.set_solver_list(sol_list)
    return


def compile_collection(col, prog_fn=None):
    compile_solvers(col, prog_fn=prog_fn)
    return col.is_valid(prog_fn=prog_fn)


def execute_collection(col, prog_fn=None):
    LOG.debug('execute_collection: col=%r prog_fn=%r', col, prog_fn)
    col.execute(prog_fn=prog_fn)
    return


def get_log_level():
    # TODO: Is the log-level stored per-collection?
    # TODO: Store and re-load the log level.
    return 'info'

def gui():
    """
    Open the Window.
    :return:
    """
    pass
