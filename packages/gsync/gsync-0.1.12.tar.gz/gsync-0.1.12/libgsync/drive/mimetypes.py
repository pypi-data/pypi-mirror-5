# Copyright (C) 2013 Craig Phillips.  All rights reserved.

from __future__ import absolute_import

class MimeTypes(object):
    NONE = "none/unknown-mimetype"
    FOLDER = "application/vnd.google-apps.folder"
    BINARY_FILE = "application/octet-stream"

    @staticmethod
    def get(path):
        mimeType = None
        try:
            import magic
            if callable(magic.from_file):
                mimeType = magic.from_file(path, mime = True)
        except Exception, e:
            import mimetypes
            mimeType = mimetypes.guess_type(path)[0]

        if mimeType is not None:
            return mimeType

        return MimeTypes.NONE
