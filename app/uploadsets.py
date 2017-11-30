# -*- coding:utf-8 -*-

from app import app
from flask_uploads import UploadSet, configure_uploads, patch_request_class


XLS = ('xls',)
IMG = ('jpg','jpeg','png')

patch_request_class(app, 10 * 1024 * 1024)

xls = UploadSet('xls', XLS)
configure_uploads(app, xls)

img = UploadSet('img',IMG)
configure_uploads(app,img)