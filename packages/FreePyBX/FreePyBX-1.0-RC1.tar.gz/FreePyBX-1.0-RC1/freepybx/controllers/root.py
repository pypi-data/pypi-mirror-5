"""
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is FreePyBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan,
    Copyright (c) 2011-2013 VoiceWARE Communications, Inc. All Rights Reserved.

    http://www.vwci.com/

    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations
    of liability) contained within the Source Code Form of the Covered Software,
    except that You may alter any license notices to the extent required to
    remedy known factual inaccuracies.
"""
import os
import sys
import math
import urllib
import urllib2
import re
import imaplib
import logging

from datetime import datetime

import formencode
from formencode import validators
from decorator import decorator

import simplejson as json
from simplejson import loads, dumps

from pylons import request, response, session, config, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators.rest import restrict
from pylons.decorators import validate

from genshi import HTML

from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import db
from freepybx.lib.validators import *
from freepybx.lib.auth import *
from freepybx.lib.util import *


log = logging.getLogger(__name__)
credential = HasCredential
logged_in = IsLoggedIn()

DEBUG=False

fs_vm_dir = config['app_conf']['fs_vm_dir']

class RootController(BaseController):
    def index(self, **kw):
        return self.login()

    def logout(self, **kw):
        try:
            if 'user' in session:
                session.invalidate()
                del session['user']
        except:
            pass
        return self.login()

    def login(self, **kw):
        try:
            if 'user' in session:
                session.invalidate()
                del session['user']
        except:
            pass
            session.invalidate()
        return render('pbx/login.html')

    @restrict("POST")
    def auth_user(self, **kw):
        errors = {}
        schema = LoginForm()

        try:
            form_result = schema.to_python(request.params)
            username = form_result["username"]
            password = form_result["password"]
            shift_start = form_result.get('shift_start', False)
        except:
            return AuthenticationError("User not logged in.")

        if not authenticate(username, password):
            return self.login()
        return self.main()

    @authorize(logged_in)
    def main(self, **kw):
        if 'group_id' in session:
            c.is_admin = True if session['group_id'] == 1 else False
        else:
            redirect("/logout")
        c.has_crm = session['has_crm']
        c.has_call_center = session['has_call_center']
        c.queues = get_queue_directory()
        if c.has_crm:
            c.campaigns = get_campaigns()
        return render('pbx/main.html')

    @authorize(credential('pbx_admin'))
    def user_add(self, **kw):
        c.has_crm = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('pbx/user_add.html')

    @authorize(logged_in)
    def pbx_users_list(self, **kw):
        return render('pbx/pbx_users_list.html')

    @authorize(logged_in)
    def broker_users(self, **kw):
        c.is_admin = True if session['group_id'] == 1 else False
        c.has_crm = session['has_crm']
        c.has_call_center = session['has_call_center']
        c.flashvars = "sid="+session.id+"&user_id="+str(session['user_id'])+"&my_name="+session['name']
        return render('pbx/broker_users.html')

    @authorize(credential('pbx_admin'))
    def ext_edit(self, **kw):
        c.has_crm  = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('pbx/ext_edit.html')

    @authorize(credential('pbx_admin'))
    def extension_add(self, **kw):
        c.has_crm  = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('pbx/extension_add.html')

    @authorize(credential('pbx_admin'))
    def resi_add(self, **kw):
        return render('pbx/residential_add.html')

    @authorize(credential('pbx_admin'))
    def resi_edit(self, **kw):
        return render('pbx/resi_edit.html')

    @authorize(credential('pbx_admin'))
    def user_edit(self, **kw):
        c.has_crm  = session['has_crm']
        c.has_call_center = session['has_call_center']
        return render('pbx/user_edit.html')

    @authorize(credential('pbx_admin'))
    def ticket_view(self, id):
        notes = []
        ticket = Ticket.query.filter_by(customer_id=session['customer_id']).filter(Ticket.id==int(id)).first()
        user = User.query.filter_by(id=ticket.opened_by).first()

        for note in TicketNote.query.filter_by(ticket_id=ticket.id).all():
            notes.append({'id': note.id, 'ticket_id': note.ticket_id,
                          'user_id': note.user_id,
                          'created': note.created.strftime("%m/%d/%Y %I:%M:%S %p"),
                          'subject': note.subject,
                          'description': note.description})
        c.ticket = ticket
        c.notes = notes
        c.u = user
        return render('pbx/ticket_view.html')





