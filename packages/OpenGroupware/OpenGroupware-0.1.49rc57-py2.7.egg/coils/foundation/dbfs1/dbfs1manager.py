#
# Copyright (c) 2010, 2011, 2013
# Adam Tauno Williams <awilliam@whitemice.org>
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
class DBFS1Manager(object):
    ''' The DBFS1Manager supports versions documents and document editing; this is compatible
        with the DB Project in Legacy OpenGroupware'''

    def __init__(self, project_id):
        self._project_id = project_id

    def get_path(self, document, extension=None, version=None):

        path = None

        if version is not None:
            for revision in document.versions:
                if revision.version == version:

                    if document.extension:
                        extension = '.{0}'.format( revision.extension )
                    else:
                        extension = ''

                    path = 'documents/{0}/{1}/{2}{3}'.format( self._project_id,
                                                              ( ( ( revision.object_id ) / 1000 ) * 1000 ),
                                                              revision.object_id,
                                                              extension )
        else:

            if extension:
                extension = '.{0}'.format( extension )
            elif document.extension:
                extension = '.{0}'.format( document.extension )
            else:
                extension = ''

            path = 'documents/{0}/{1}/{2}{3}'.format( self._project_id,
                                                       ( ( ( document.object_id ) / 1000 ) * 1000 ),
                                                       document.object_id,
                                                       extension )
        return path


    def extension_change(self, document, old_extension):
        if document.extension == old_extension:
            return False, None, None

        old_path = self.get_path( document, extension=old_extension )

        new_path = self.get_path( document )

        return True, old_path, new_path

    def create_path(self, document, version):

        folder_path = 'documents/{0}/{1}'.format( self._project_id, ( ( ( version.object_id ) / 1000 ) * 1000 ) )

        if document.extension:
            file_name   = '{1}.{2}'.format( folder_path, version.object_id, document.extension, )
        else:
            file_name   = '{1}'.format( folder_path, version.object_id, )

        return ( folder_path, file_name )

