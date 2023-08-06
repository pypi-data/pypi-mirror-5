#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from werkzeug.wrappers import Response

def captcha_html(app, environ, request, version):
    return Response('<img src="http://posativ.org/scratch.png" \
    width="298px" height="130" style="overflow-x: scroll; overflow-y: hidden;" />', content_type="text/html")
