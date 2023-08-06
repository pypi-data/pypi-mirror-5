'''
    This Source Code Form is subject to the terms of the Mozilla Public 
    License, v. 2.0. If a copy of the MPL was not distributed with this 
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an "AS IS"
    basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
    License for the specific language governing rights and limitations
    under the License.

    The Original Code is PythonPBX/VoiceWARE.

    The Initial Developer of the Original Code is Noel Morgan, VoiceWARE, Inc.
    Copyright (c) 2011-2013 VoiceWARE, Inc. All Rights Reserved.
    
    http://www.vwna.com/ 
    
    You may not remove or alter the substance of any license notices (including
    copyright notices, patent notices, disclaimers of warranty, or limitations 
    of liability) contained within the Source Code Form of the Covered Software, 
    except that You may alter any license notices to the extent required to 
    remedy known factual inaccuracies.   
    
'''

import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from freepybx.model import *
from freepybx.model.meta import db
from pylons.decorators.rest import restrict
from genshi import HTML
from freepybx.lib.auth import *
from decorator import decorator
import formencode
from formencode import validators
from pylons.decorators import validate
from freepybx.lib import helpers as h
import pylons
import simplejson as json
from simplejson import loads, dumps
import cgitb; cgitb.enable()

log = logging.getLogger(__name__)

def authenticate(username, password):
    auth_user = User.query.filter(User.username==username).first()
    if not auth_user:
        log.debug("No user named: '%s'", username)
        return False        
    elif not auth_user.password:
        log.error("Bad user/pass:'%s'")
        return False
    elif password != auth_user.password:
        log.debug("database password for user '%s'", username)
        return False
    else:
        session['username'] = auth_user.username
        session['password'] = auth_user.password
        session['customer_id'] = auth_user.customer_id
        session['user_id'] = auth_user.id
        session['name'] = auth_user.first_name+' '+auth_user.last_name
        session["last_login"] = auth_user.last_login
        session['has_crm'] = auth_user.has_crm 
        session['customer_name'] = auth_user.get_customer_name(auth_user.customer_id)

        if auth_user.has_crm:
            ea = auth_user.get_email_account()
            session['email_server'] = ea.mail_server
            session['email'] = ea.email
            session['email_password'] = ea.password    
                
        if auth_user.has_call_center():
            session['has_call_center'] = True
        else:
            session['has_call_center'] = False
            
        session['is_agent'] = auth_user.is_agent()
        session['context'] = auth_user.get_context()
        session['ext'] = auth_user.get_extension()

        request.environ["REMOTE_USER"] = auth_user.username
        request.environ["HTTP_REMOTE_USER"] = auth_user.username      
      
    if auth_user and not auth_user.active: 
        return False

    session["perms"] = auth_user.permissions
    session['group_id'] = auth_user.group_id
    session["user"] = auth_user     
    session.save()
    auth_user.register_login(username, session, request)

    return True

def authenticate_admin(username, password):
    
    auth_user = AdminUser.query.filter(AdminUser.username==username).first()

    if not auth_user:
        log.debug("No user named: '%s'", username)
        return False        
    elif not auth_user.password:
        log.error("Bad username/pass:'%s'")
        return False
    elif password != auth_user.password:
        log.debug("Database password for user '%s'", username)
        return False
    else:
        request.environ["REMOTE_USER"] = auth_user.username
        request.environ["HTTP_REMOTE_USER"] = auth_user.username

    session["perms"]= auth_user.permissions
    session["user"] = auth_user
    session["name"] = auth_user.name
    session['user_id'] = auth_user.id

    auth_user.register_login(username, session, request)
    db.flush()
    session.save()
    return True


class AuthenticationError(Exception):
    message="Authentication error or incorrect permissions."

    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)


class HasCredential(object):

    error_msg = u'Needs to have at least this permission.'

    def __init__(self, *args):
        self.credentials = args

    def check(self):
        if 'user' in session:
            user = User.query.filter(User.id==session['user_id']).filter_by(session_id=session.id).first()
            if not user:
                session.invalidate()
                raise AuthenticationError(self.error_msg)
            for perm in user.permissions:
                for cred in self.credentials:
                    if str(cred) == str(perm.name):
                        return True
            raise AuthenticationError(self.error_msg)
        else:
            redirect("/admin/logout")


class IsLoggedIn(object):
    def check(self):
        if 'user' in session:
            return True
        redirect("/login")


class IsSuperUser(object):
    def check(self):
        try:
            if 'user' in session:
                row = AdminUser.query.filter_by(id=session['user_id']).filter_by(session_id=session.id).first()
                if not row:
                    session.invalidate()
                    redirect("/admin/logout")
                c.perms = row.permissions
                for p in c.perms:
                    if 'superuser' in p:
                        return True
                raise AuthenticationError("You have no rights here.")
            else:
                redirect("/admin/logout")
        except:
            redirect("/admin/logout")


def authorize(valid):
    def validate(func, self, *args, **kwargs):
        try:
            valid.check()
        except AuthenticationError, e:
            return AuthenticationError(e)
        return func(self, *args, **kwargs)
    return decorator(validate)

