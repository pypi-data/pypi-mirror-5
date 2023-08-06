#!/usr/bin/env python
# -*- encoding: utf-8 -*-

WEAVE_ILLEGAL_METH = "1"          # Illegal method/protocol
WEAVE_INVALID_CAPTCHA = "2"       # Incorrect/missing captcha
WEAVE_INVALID_USER = "3"          # Invalid/missing username
WEAVE_INVALID_WRITE = "4"         # Attempt to overwrite data that can't be
WEAVE_WRONG_USERID = "5"          # Userid does not match account in path
WEAVE_MALFORMED_JSON = "6"        # Json parse failure
WEAVE_MISSING_PASSWORD = "7"      # Missing password field
WEAVE_INVALID_WBO = "8"           # Invalid Weave Basic Object
WEAVE_WEAK_PASSWORD = "9"         # Requested password not strong enough
WEAVE_INVALID_RESET_CODE = "10"   # Invalid/missing password reset code
WEAVE_UNSUPPORTED_FUNC = "11"     # Unsupported function
WEAVE_NO_EMAIL_ADRESS = "12"      # No email address on file
WEAVE_INVALID_COLLECTION = "13"   # Invalid collection
WEAVE_OVER_QUOTA = "14"           # User over quota

import os
import json
import sqlite3

from werkzeug.wrappers import Response
from weave.minimal.utils import login


@login(['DELETE', 'POST'])
def index(app, environ, request, version, uid):

    # Returns 1 if the uid is in use, 0 if it is available.
    if request.method in ['HEAD']:
        return Response('', 200)

    elif request.method in ['GET']:
        if not [p for p in os.listdir(app.data_dir) if p.split('.', 1)[0] == uid]:
            code = '0' if app.registration else '1'
        else:
            code = '1'
        return Response(code, 200)

    # Requests that an account be created for uid
    elif request.method == 'PUT':
        if app.registration and not [p for p in os.listdir(app.data_dir) if p.startswith(uid)]:

            try:
                passwd = json.loads(request.get_data(as_text=True))['password']
            except ValueError:
                return Response(WEAVE_MALFORMED_JSON, 400)
            except KeyError:
                return Response(WEAVE_MISSING_PASSWORD, 400)

            try:
                con = sqlite3.connect(app.dbpath(uid, passwd))
                con.commit()
                con.close()
            except IOError:
                return Response(WEAVE_INVALID_WRITE, 400)
            return Response(uid, 200)

        return Response(WEAVE_INVALID_WRITE, 400)

    elif request.method == 'POST':
        return Response('Not Implemented', 501)

    elif request.method == 'DELETE':
        if request.authorization.username != uid:
            return Response('Not Authorized', 401)

        try:
            os.remove(app.dbpath(uid, request.authorization.password))
        except OSError:
            pass
        return Response('0', 200)


@login(['POST'])
def change_password(app, environ, request, version, uid):
    """POST https://server/pathname/version/username/password"""

    if not [p for p in os.listdir(app.data_dir) if p.split('.', 1)[0] == uid]:
        return Response(WEAVE_INVALID_USER, 404)

    if len(request.get_data(as_text=True)) == 0:
        return Response(WEAVE_MISSING_PASSWORD, 400)
    elif len(request.get_data(as_text=True)) < 4:
        return Response(WEAVE_WEAK_PASSWORD, 400)

    old_dbpath = app.dbpath(uid, request.authorization.password)
    new_dbpath = app.dbpath(uid, request.get_data(as_text=True))
    try:
        os.rename(old_dbpath, new_dbpath)
    except OSError:
        return Response(WEAVE_INVALID_WRITE, 503)

    return Response('success', 200)
