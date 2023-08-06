#
# Copyright (c) 2009, 2011, 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from coils.core import ServerDefaultsManager
from render_object import as_string, as_integer, as_datetime, render_object
from render_task import render_task


INCLUDEDARCHIVEDPROJECTTASKS = -1


def render_project(entity, detail, ctx, favorite_ids=None):
    '''
            'comment': 'Update project comment',
            'endDate': <DateTime '20321231T18:59:00' at b796b34c>,
            'entityName': 'Project',
            'folderObjectId': 479360,
            'kind': '',
            'name': 'Updated project name',
            'number': 'P479340',
            'objectId': 479340,
            'ownerObjectId': 10160,
            'placeHolder': 0,
            'startDate': <DateTime '20070213T05:00:00' at b7964e0c>,
            'status': '',
            'version': ''}
    '''

    global INCLUDEDARCHIVEDPROJECTTASKS

    p = {
        'comment':         as_string(entity.comment),
        'endDate':         as_datetime(entity.end),
        'entityName':      'Project',
        'folderObjectId':  as_integer(entity.folder.object_id),
        'kind':            as_string(entity.kind),
        'name':            as_string(entity.name),
        'number':          as_string(entity.number),
        'objectId':        as_integer(entity.object_id),
        'ownerObjectId':   as_integer(entity.owner_id),
        'parentObjectId':  as_integer(entity.parent_id),
        'placeHolder':     as_integer(entity.is_fake),
        'startDate':       as_datetime(entity.start),
        'status':          as_string(entity.status),
        'version':         as_integer(entity.version)
    }

    if entity.parent:
        p['parentProjectName'] = entity.parent.name
        p['parentProjectNumber'] = entity.parent.number

    if detail & 1024:
        p['childProjectObjectIds'] = [x.object_id for x in entity.children]

    if detail & 4096:

        if INCLUDEDARCHIVEDPROJECTTASKS == -1:
            sd = ServerDefaultsManager()
            if sd.bool_for_default('OmphalosIncludeArchivedProjectTasks'):
                INCLUDEDARCHIVEDPROJECTTASKS = 1
            else:
                INCLUDEDARCHIVEDPROJECTTASKS = 0

        p['_TASKS'] = []
        for task in ctx.run_command('project::get-tasks', project=entity):
            if INCLUDEDARCHIVEDPROJECTTASKS or task.state != '30_archived':
                p['_TASKS'].append(render_task(task, 0, ctx))

    # TODO: there should be a relation just for the count
    p['projectActiveTaskCount'] = len(entity.active_tasks)
    p['projectArchivedTaskCount'] = len(entity.archived_tasks)

    # Contacts & Enterprises
    if (detail & 512) or (detail & 256):
        tm = ctx.type_manager
        if (detail & 512):
            p['_ENTERPRISES'] = []
        if (detail & 256):
            p['_CONTACTS'] = []
        for assignment in entity.assignments:
            kind = tm.get_type(assignment.child_id)
            if ((kind == 'Enterprise') and (detail & 512)):
                p['_ENTERPRISES'].append(
                    {'entityName':       'assignment',
                     'objectId':         as_integer(assignment.object_id),
                     'sourceEntityName': 'Project',
                     'sourceObjectId':   as_integer(assignment.parent_id),
                     'targetEntityName': 'Enterprise',
                     'targetObjectId':   as_integer(assignment.child_id), })
            elif ((kind == 'Contacts') and (detail & 256)):
                p['_CONTACTS'].append(
                    {'entityName':       'assignment',
                     'objectId':         as_integer(assignment.object_id),
                     'sourceEntityName': 'Project',
                     'sourceObjectId':   as_integer(assignment.parent_id),
                     'targetEntityName': 'Contact',
                     'targetObjectId':   as_integer(assignment.child_id), })

    # FLAGS
    flags = []
    rights = ctx.access_manager.access_rights(entity)
    if 'a' in rights:
        flags.append('ADMIN')
    if 'd' in rights:
        flags.append('DELETE')
    if 'p' in rights:
        flags.append('POST')
    if 'w' in rights:
        flags.append('WRITE')
    if 'f' in rights:
        flags.append('FORM')
    if 'i' in rights:
        flags.append('INSERT')

    if not rights.intersection(set('adiw')):
        flags.append('READONLY')

    if entity.owner_id in ctx.context_ids:
        flags.append('OWNER')

    # FAVORITE
    # TODO: Implement!
    #if entity.object_id in favorite_ids:
    #    flags.append('FAVORITE')

    empty = False
    if not entity.tasks:
        if not entity.children:
            if entity.folder:
                if not entity.folder.files and not entity.folder.folders:
                    empty = True
            else:
                empty = True
    if empty:
        flags.append('EMPTY')

    if entity.children:
        flags.append('CHILDREN')

    p['FLAGS'] = flags

    return render_object(p, entity, detail, ctx)
