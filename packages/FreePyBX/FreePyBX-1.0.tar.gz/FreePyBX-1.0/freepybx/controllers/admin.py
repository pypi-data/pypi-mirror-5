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
import formencode
import shutil
import urllib
import logging
import cgitb; cgitb.enable(format='text')
from webob import Request, Response

from pylons import config
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators.rest import restrict
from pylons.decorators import validate, jsonify

import formencode
from formencode import validators

from freepybx.lib.base import BaseController, render
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import db
from freepybx.lib.auth import *
from freepybx.lib.forms import *
from freepybx.lib.util import *
from freepybx.lib.util import PbxError, DataInputError, PbxEncoder
from freepybx.lib.validators import *

from genshi import HTML
from decorator import decorator

import simplejson as json
from simplejson import loads, dumps

from sqlalchemy import Date, cast, desc, asc
from sqlalchemy.orm import join


# Import Auth decorators etc.
logged_in = IsLoggedIn()
super_user = IsSuperUser()
credentials = HasCredential(object)
log = logging.getLogger(__name__)

fs_vm_dir = config['app_conf']['fs_vm_dir']
fs_profile = config['app_conf']['fs_profile']


class CredentialError(Exception):
    message=""
    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)


class AdminController(BaseController):
    """Admin controller:

    This admin module is reponsible for the majority of the applications
    adminstrative functionality and is mainly for restricted use.

    """
    @authorize(super_user)
    def index(self, **kw):
        c.sid = session.id
        c.my_name = session["name"]
        c.profiles = PbxProfile.query.all()
        return render('admin/admin.html')

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
        return render('admin/login.html')

    @restrict("POST")
    def auth_admin(self, **kw):
        schema = LoginForm()
        try:
            form_result = schema.to_python(request.params)
            username = form_result.get("username")
            password = form_result.get("password")
        except:
            return AuthenticationError("Auth error...")

        if not authenticate_admin(username, password):
            return self.login()
        else:
            session.save()
        c.sid = session.id
        c.my_name = session["name"]
        c.profiles = PbxProfile.query.all()
        return render('admin/admin.html')

    @authorize(super_user)
    def main(self, **kw):
        c.sid = session.id
        c.my_name = session["name"]
        c.profiles = PbxProfile.query.all()

        return render('admin/admin.html')

    @authorize(super_user)
    @jsonify
    def users(self):
        items=[]
        try:
            for user in User.query.order_by(asc(User.id)).all():
                extensions = []
                for endpoint in PbxEndpoint.query.filter(
                                PbxEndpoint.user_id==user.id
                ).filter_by(user_context=user.context).all():
                    extensions.append(endpoint.auth_id)
                if not len(extensions) > 0:
                    extension_cell = "No Extension"
                else:
                    extension_cell = ", ".join(extensions)

                items.append({'id': user.id, 'extension': extension_cell,
                              'username': user.username,
                              'password': user.password,
                              'first_name': user.first_name,
                              'name': user.first_name +' '+user.last_name,
                              'context': user.context,
                              'last_name': user.last_name,
                              'address': user.address,
                              'address_2': user.address_2,
                              'city': user.city, 'state': user.state,
                              'zip': user.zip, 'tel': user.tel,
                              'mobile': user.mobile, 'notes': user.notes,
                              'created': user.created.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'updated': user.updated.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'active': user.active, 'group_id': user.group_id,
                              'last_login': user.last_login.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'remote_addr': user.remote_addr,
                              'session_id': user.session_id,
                              'customer_id': user.customer_id})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def customers(self):
        items=[]
        try:
            for customer in Customer.query.all():
                items.append({'id': customer.id, 'name': customer.name, 'active': customer.active, 'tel': customer.tel})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def customer_store(self):
        items=[]
        try:
            for customer in Customer.query.all():
                items.append({'id': customer.id, 'name': customer.name, 'active': customer.active, 'tel': customer.tel})

                return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @jsonify
    @authorize(super_user)
    def customer_by_id(self, id, **kw):
        items=[]

        try:
            customer = Customer.query.filter(Customer.id==id).first()

            if customer is None:
                raise Exception("No customer with that ID.")

            profile = PbxProfile.query.filter_by(id=customer.pbx_profile_id).first()

            items.append({'id': customer.id, 'name': customer.name,  'profile': profile.name, 'email': customer.email,
                          'address': customer.address, 'address_2': customer.address_2,
                          'city': customer.city, 'state': customer.state, 'zip': customer.zip, 'default_gateway': customer.default_gateway,
                          'tel': customer.tel, 'url': customer.url, 'active': customer.active, 'context': customer.context,
                          'has_crm': customer.has_crm, 'has_call_center': customer.has_call_center,
                          'contact_name': customer.contact_name, 'contact_phone': customer.contact_phone, 'contact_mobile': customer.contact_mobile,
                          'contact_title': customer.contact_title, 'contact_email': customer.contact_email, 'notes': customer.notes,
                          'pbx_profile_id': customer.pbx_profile_id,
                          'has_international': customer.has_international,
                          'inbound_channel_limit': customer.inbound_channel_limit,
                          'outbound_channel_limit': customer.outbound_channel_limit,
                          'max_extensions': customer.max_extensions,
                          'hard_channel_limit': customer.hard_channel_limit,
                          'channel_audio': customer.channel_audio})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    def update_customer_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                customer = Customer.query.filter_by(id=i['id']).first()
                customer.active = i['active']
                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated Customer."

    @authorize(super_user)
    def add_customer(self):
        schema = CustomerForm()
        try:
            form_result = schema.to_python(request.params)
            customer = Customer()
            customer.name = form_result.get('name')
            customer.tel = form_result.get('cust_tel')
            customer.address = form_result.get('address')
            customer.address_2 = form_result.get('address_2')
            customer.city = form_result.get('city')
            customer.state = form_result.get('state')
            customer.zip = form_result.get('zip')
            customer.url = form_result.get('url')
            customer.context = form_result.get('context')
            customer.email = form_result.get('contact_email')
            customer.contact_name = form_result.get('contact_name')
            customer.contact_phone = form_result.get('contact_phone')
            customer.contact_mobile = form_result.get('contact_mobile')
            customer.contact_title = form_result.get('contact_title')
            customer.contact_email = form_result.get('contact_email')
            customer.active = True if form_result.get('active')=="true" else False
            customer.has_international = True if form_result.get('has_international')=="true" else False
            customer.has_crm = True if form_result.get('has_crm')=="true" else False
            customer.has_call_center = True if form_result.get('has_call_center')=="true" else False
            customer.default_gateway = form_result.get('default_gateway')
            customer.pbx_profile_id = form_result.get('pbx_profile_id')
            customer.inbound_channel_limit = form_result.get('inbound_channel_limit')
            customer.channel_audio = form_result.get('channel_audio')

            try:
                os.makedirs(fs_vm_dir+str(customer.context)+'/recordings')
                os.makedirs(fs_vm_dir+str(customer.context)+'/system/recordings')
                os.makedirs(fs_vm_dir+str(customer.context)+'/queue-recordings')
                os.makedirs(fs_vm_dir+str(customer.context)+'/extension-recordings')
                os.makedirs(fs_vm_dir+str(customer.context)+'/faxes')
            except:
                pass

            db.add(customer)
            db.flush()

            context = PbxContext(customer.id, form_result.get('domain'), form_result.get('context'), form_result.get('default_gateway'),
                customer.profile, customer.name, customer.tel)

            db.add(context)
            customer.pbx_contexts.append(context)

            db.add(PbxDid(form_result.get('cust_add_did'), customer.id,
                form_result.get('context'), form_result.get('domain'), form_result.get('t38', False), form_result.get('e911', False),
                form_result.get('cnam', False), True))

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully created customer."

    @authorize(super_user)
    @jsonify
    def customers_id(self):
        items=[]
        try:
            for customer in Customer.query.all():
                items.append({'id': customer.id, 'name': customer.name, 'active': customer.active, 'tel': customer.tel})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    def edit_customer(self):
        schema = CustomerEditForm()
        try:
            form_result = schema.to_python(request.params)
            customer = Customer.query.filter_by(id=form_result.get('edit_customer_id')).first()
            customer.name = form_result.get('customer_name')
            customer.tel = form_result.get('cust_tel')
            customer.address = form_result.get('address')
            customer.address_2 = form_result.get('address_2')
            customer.city = form_result.get('city')
            customer.state = form_result.get('state')
            customer.zip = form_result.get('zip')
            customer.url = form_result.get('url')
            customer.email = form_result.get('contact_email')
            customer.contact_name = form_result.get('contact_name')
            customer.contact_phone = form_result.get('contact_phone')
            customer.contact_mobile = form_result.get('contact_mobile')
            customer.contact_title = form_result.get('contact_title')
            customer.contact_email = form_result.get('contact_email')
            customer.active = True if form_result.get('active')=="true" else False
            customer.has_international = True if form_result.get('has_international')=="true" else False
            customer.has_crm = True if form_result.get('find_me')=="true" else False
            customer.has_call_center = True if form_result.get('has_call_center')=="true" else False
            customer.default_gateway = form_result.get('default_gateway')
            customer.pbx_profile_id = form_result.get('pbx_profile_id')
            customer.max_extensions = form_result.get('max_extensions')
            customer.hard_channel_limit = form_result.get('hard_channel_limit')
            customer.inbound_channel_limit = form_result.get('inbound_channel_limit')
            customer.outbound_channel_limit = form_result.get('outbound_channel_limit')
            customer.channel_audio = form_result.get('channel_audio')

            db.commit()

            return "Successfully edited customer."

        except validators.Invalid, error:
            return 'Error: %s' % error

    @authorize(super_user)
    def update_customer_grid(self, **kw):
        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                customer = Customer.query.filter_by(id=i['id']).first()
                customer.active = i['active']

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated Customer."

    @authorize(super_user)
    def del_customer(self, **kw):

        customer = Customer.query.filter_by(id=request.params.get("id")).first()
        try:
            if customer and customer.context:
                if not delete_customer(customer.context):
                    raise Exception("Failed deleting {0}".format(customer.name))
            else:
                raise Exception("Failed to delete customer.")
        except Exception, e:
            return 'Error: %s' % e

        return "Successfully deleted {0}.".format(customer.name)

    @authorize(logged_in)
    @jsonify
    def user_groups(self, **kw):
        items=[]
        try:
            for group in Group.query.all():
                items.append({'id': group.id, 'name': group.name, 'description': group.description})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def profiles(self, **kw):
        items=[]
        try:
            for profile in  PbxProfile.query.all():
                items.append({'name': profile.name,
                              'ext_rtp_ip': profile.ext_rtp_ip,
                              'ext_sip_ip': profile.ext_sip_ip,
                              'sip_port': profile.sip_port,
                              'accept_blind_reg': profile.accept_blind_reg,
                              'auth_calls': profile.auth_calls,
                              'email_domain': profile.email_domain})

            return {'identifier': 'name', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'name', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def get_profile_by_id(self, id, **kw):
        items=[]
        try:
            profile = PbxProfile.query.filter_by(id=id).first()
            items.append({'id': profile.id, 'name': profile.name,
                          'odbc_credentials': profile.odbc_credentials,
                          'manage_presence': profile.manage_presence,
                          'presence_hosts': profile.presence_hosts,
                          'send_presence_on_register': profile.send_presence_on_register,
                          'delete_subs_on_register': profile.delete_subs_on_register,
                          'caller_id_type': profile.caller_id_type,
                          'auto_jitterbuffer_msec': profile.auto_jitterbuffer_msec,
                          'dialplan': profile.dialplan,
                          'ext_rtp_ip': profile.ext_rtp_ip,
                          'ext_sip_ip': profile.ext_sip_ip,
                          'rtp_ip': profile.rtp_ip,
                          'sip_ip': profile.sip_ip,
                          'sip_port': profile.sip_port,
                          'nonce_ttl': profile.nonce_ttl,
                          'sql_in_transactions': profile.sql_in_transactions,
                          'use_rtp_timer': profile.use_rtp_timer,
                          'codec_prefs': profile.codec_prefs,
                          'inbound_codec_negotiation': profile.inbound_codec_negotiation,
                          'rtp_timeout_sec': profile.rtp_timeout_sec,
                          'rfc2833_pt': profile.rfc2833_pt,
                          'dtmf_duration': profile.dtmf_duration,
                          'dtmf_type': profile.dtmf_type,
                          'session_timeout': profile.session_timeout,
                          'multiple_registrations': profile.multiple_registrations,
                          'vm_from_email': profile.vm_from_email,
                          'accept_blind_reg': profile.accept_blind_reg,
                          'auth_calls': profile.auth_calls,
                          'email_domain': profile.email_domain,
                          'rtp_timer_name': profile.rtp_timer_name,
                          'presence_db_name': profile.presence_db_name,
                          'codec_ms': profile.codec_ms,
                          'disable_register': profile.disable_register,
                          'log_auth_failures': profile.log_auth_failures,
                          'auth_all_packets':profile.auth_all_packets,
                          'minimum_session_expires': profile.minimum_session_expires})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def profiles_ids(self, **kw):
        items=[]
        try:
            for profile in  PbxProfile.query.all():
                items.append({'id': profile.id, 'name': profile.name, 'ext_rtp_ip': profile.ext_rtp_ip,
                              'ext_sip_ip': profile.ext_sip_ip, 'sip_port': profile.sip_port})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def add_profile(self):
        schema = ProfileForm()
        try:
            form_result = schema.to_python(request.params)
            profile = PbxProfile()
            profile.name = form_result.get('name')
            profile.odbc_credentials = form_result.get('odbc_credentials')
            profile.manage_presence = True if form_result.get('manage_presence')=="true" else False
            profile.presence_db_name = form_result.get('dbname', None)
            profile.presence_hosts = form_result.get('presence_hosts', None)
            profile.send_presence_on_register = True if form_result.get('send_presence_on_register')=="true" else False
            profile.delete_subs_on_register = True if form_result.get('delete_subs_on_register')=="true" else False
            profile.caller_id_type = form_result.get('caller_id_type', u'rpid')
            profile.auto_jitterbuffer_msec = form_result.get('auto_jitterbuffer_msec', 120)
            profile.dialplan = form_result.get('dialplan', u'XML,enum')
            profile.ext_rtp_ip = form_result.get('ext_rtp_ip', None)
            profile.ext_sip_ip = form_result.get('ext_sip_ip', None)
            profile.rtp_ip = form_result.get('rtp_ip', None)
            profile.sip_ip = form_result.get('sip_ip', None)
            profile.sip_port = form_result.get('sip_port', 5060)
            profile.nonce_ttl = form_result.get('nonce_ttl', 60)
            profile.sql_in_transactions = True if form_result.get('sql_in_transactions')=="true" else False
            profile.use_rtp_timer = True if form_result.get('use_rtp_timer')=="true" else False
            profile.rtp_timer_name =  form_result.get('rtp_timer_name', u'soft')
            profile.codec_prefs = form_result.get('codec_prefs', u'PCMU,PCMA,G722,G726,H264,H263')
            profile.inbound_codec_negotiation = form_result.get('inbound_codec_negotiation', u'generous')
            profile.codec_ms = form_result.get('codec_ms', 20)
            profile.rtp_timeout_sec = form_result.get('rtp_timeout_sec', 300)
            profile.rtp_hold_timeout_sec = form_result.get('rtp_hold_timeout_sec', 1800)
            profile.rfc2833_pt = form_result.get('rfc2833_pt', 101)
            profile.dtmf_duration = form_result.get('dtmf_duration', 100)
            profile.dtmf_type = form_result.get('dtmf_type', u'rfc2833')
            profile.session_timeout = form_result.get('session_timeout', 1800)
            profile.multiple_registrations = form_result.get('multiple_registrations', u'contact')
            profile.vm_from_email = form_result.get('vm_from_email', u'voicemail@freeswitch')
            profile.accept_blind_reg = True if form_result.get('accept_blind_reg')=="true" else False
            profile.auth_calls = True if form_result.get('auth_calls')=="true" else False
            profile.email_domain = form_result.get('email_domain', u'freeswitch.org')
            profile.auth_all_packets = True if form_result.get('auth_all_packets')=="true" else False
            profile.log_auth_failures = True if form_result.get('log_auth_failures')=="true" else False
            profile.disable_register = True if form_result.get('disable_register')=="true" else False
            profile.minimum_session_expires = form_result.get('minimum_session_expires', 120)

            db.add(profile)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Validation Error: %s' % error

        return "Successfully added profile."

    @authorize(super_user)
    def edit_profile(self):
        schema = ProfileEditForm()
        try:
            form_result = schema.to_python(request.params)
            profile = PbxProfile.query.filter_by(id=form_result.get('id',0)).first()
            profile.odbc_credentials = form_result.get('odbc_credentials')
            profile.manage_presence = True if form_result.get('manage_presence')=="true" else False
            profile.presence_db_name = form_result.get('dbname', None)
            profile.presence_hosts = form_result.get('presence_hosts', None)
            profile.send_presence_on_register = True if form_result.get('send_presence_on_register')=="true" else False
            profile.delete_subs_on_register = True if form_result.get('delete_subs_on_register')=="true" else False
            profile.caller_id_type = form_result.get('caller_id_type', u'rpid')
            profile.auto_jitterbuffer_msec = form_result.get('auto_jitterbuffer_msec', 120)
            profile.dialplan = form_result.get('dialplan', u'XML,enum')
            profile.ext_rtp_ip = form_result.get('ext_rtp_ip', None)
            profile.ext_sip_ip = form_result.get('ext_sip_ip', None)
            profile.rtp_ip = form_result.get('rtp_ip', None)
            profile.sip_ip = form_result.get('sip_ip', None)
            profile.sip_port = form_result.get('sip_port', 5060)
            profile.nonce_ttl = form_result.get('nonce_ttl', 60)
            profile.sql_in_transactions = True if form_result.get('sql_in_transactions')=="true" else False
            profile.use_rtp_timer = True if form_result.get('use_rtp_timer')=="true" else False
            profile.rtp_timer_name =  form_result.get('rtp_timer_name', u'soft')
            profile.codec_prefs = form_result.get('codec_prefs', u'PCMU,PCMA,G722,G726,H264,H263')
            profile.inbound_codec_negotiation = form_result.get('inbound_codec_negotiation', u'generous')
            profile.codec_ms = form_result.get('codec_ms', 20)
            profile.rtp_timeout_sec = form_result.get('rtp_timeout_sec', 300)
            profile.rtp_hold_timeout_sec = form_result.get('rtp_hold_timeout_sec', 1800)
            profile.rfc2833_pt = form_result.get('rfc2833_pt', 101)
            profile.dtmf_duration = form_result.get('dtmf_duration', 100)
            profile.dtmf_type = form_result.get('dtmf_type', u'rfc2833')
            profile.session_timeout = form_result.get('session_timeout', 1800)
            profile.multiple_registrations = form_result.get('multiple_registrations', u'contact')
            profile.vm_from_email = form_result.get('vm_from_email', u'voicemail@freeswitch')
            profile.accept_blind_reg = True if form_result.get('accept_blind_reg')=="true" else False
            profile.auth_calls = True if form_result.get('auth_calls')=="true" else False
            profile.email_domain = form_result.get('email_domain', u'freeswitch.org')
            profile.auth_all_packets = True if form_result.get('auth_all_packets')=="true" else False
            profile.log_auth_failures = True if form_result.get('log_auth_failures')=="true" else False
            profile.disable_register = True if form_result.get('disable_register')=="true" else False
            profile.minimum_session_expires = form_result.get('minimum_session_expires', 120)

            db.add(profile)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Validation Error: %s' % error

        return "Successfully updated profile."

    @authorize(super_user)
    @jsonify
    def gateways(self, **kw):
        items=[]
        try:
            for gateway in PbxGateway.query.all():
                profile = PbxProfile.query.filter_by(id=gateway.pbx_profile_id).first()
                items.append({'id': gateway.id,'name': gateway.name, 'proxy': gateway.proxy, 'mask': gateway.mask, 'register': gateway.register,
                              'profile': profile.name})

            return {'identifier': 'name', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'name', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def gateway_store(self, **kw):
        items=[]
        try:
            for gateway in PbxGateway.query.all():
                profile = PbxProfile.query.filter_by(id=gateway.pbx_profile_id).first()
                items.append({'id': gateway.id,'name': gateway.name, 'proxy': gateway.proxy, 'mask': gateway.mask, 'register': gateway.register,
                              'profile': profile.name})

                return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def gateway_by_id(self, id, **kw):
        items=[]
        try:
            gateway = PbxGateway.query.filter(PbxGateway.id==id).first()
            profile = PbxProfile.query.filter_by(id=gateway.pbx_profile_id).first()
            items.append({'id': gateway.id, 'name': gateway.name, 'pbx_profile_id': gateway.pbx_profile_id,
                          'username': gateway.username, 'password': gateway.password,
                          'proxy': gateway.proxy, 'register': gateway.register,
                          'register_transport': gateway.register_transport,
                          'reg_id': gateway.reg_id, 'rfc5626': gateway.rfc5626,
                          'extension': gateway.extension, 'realm': gateway.realm,
                          'from_domain': gateway.from_domain, 'expire_seconds': gateway.expire_seconds,
                          'retry_seconds': gateway.retry_seconds,
                          'ping': gateway.ping, 'context': gateway.context,
                          'caller_id_in_from': gateway.caller_id_in_from,
                          'mask': gateway.mask, 'contact_params': gateway.contact_params, })

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    def add_gateway(self, **kw):
        schema = GatewayForm()
        try:
            form_result = schema.to_python(request.params)
            gateway = PbxGateway()
            gateway.name = form_result.get('name')
            gateway.pbx_profile_id = form_result.get('pbx_profile_id')
            gateway.username = form_result.get('gateway_username')
            gateway.password = form_result.get('password')
            gateway.realm = form_result.get('realm')
            gateway.proxy = form_result.get('proxy')
            gateway.register = form_result.get('register', False)
            gateway.register_transport = form_result.get('register_transport')
            gateway.extension = form_result.get('extension')
            gateway.from_domain = form_result.get('from_domain')
            gateway.expire_seconds = form_result.get('expire_seconds')
            gateway.retry_seconds = form_result.get('retry_seconds')
            gateway.ping = form_result.get('ping')
            gateway.context = form_result.get('context')
            gateway.caller_id_in_from = form_result.get('caller_id_in_from')
            gateway.mask =  form_result.get('mask')
            gateway.rfc5626 = form_result.get('rfc5626', True)
            gateway.reg_id = form_result.get('reg_id', 1)
            gateway.contact_params = form_result.get('contact_params', u'tport=tcp')

            db.add(gateway)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully added gateway."

    @authorize(super_user)
    def edit_gateway(self):
        schema = GatewayEditForm()
        try:
            form_result = schema.to_python(request.params)
            gateway = PbxGateway.query.filter(PbxGateway.id==form_result.get('gateway_id')).first()
            gateway.name = form_result.get('name')
            gateway.pbx_profile_id = form_result.get('pbx_profile_id')
            gateway.username = form_result.get('gateway_username')
            gateway.password = form_result.get('password')
            gateway.proxy = form_result.get('proxy')
            gateway.register = form_result.get('register', False)
            gateway.register_transport = form_result.get('register_transport')
            gateway.extension = form_result.get('extension')
            gateway.realm = form_result.get('realm')
            gateway.from_domain = form_result.get('from_domain')
            gateway.expire_seconds = form_result.get('expire_seconds')
            gateway.retry_seconds = form_result.get('retry_seconds')
            gateway.ping = form_result.get('ping')
            gateway.context = form_result.get('context')
            gateway.caller_id_in_from = form_result.get('caller_id_in_from')
            gateway.mask =  form_result.get('mask')
            gateway.rfc5626 = form_result.get('rfc5626', True)
            gateway.reg_id = form_result.get('reg_id', 1)
            gateway.contact_params = form_result.get('contact_params', u'tport=tcp')

            db.add(gateway)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully edited gateway."

    @authorize(super_user)
    def update_gw_grid(self, **kw):
        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                gateway = PbxGateway.query.filter_by(id=i['id']).first()
                profile = PbxProfile.query.filter_by(name=i['profile']).first()
                gateway.register = i['register']
                gateway.pbx_profile_id = profile.id

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated Gateway."

    @authorize(super_user)
    def del_gateway(self, **kw):

        try:
            PbxGateway.query.filter_by(id=request.params.get("id")).delete()
            db.commit()

        except Exception, e:
            db.rollback()
            return "Exception: %s" % e

        return "Successfully deleted gateway."

    @authorize(super_user)
    @jsonify
    def outbound_routes(self, **kw):
        items=[]
        try:
            for outbound_route in db.query(PbxOutboundRoute.id, PbxOutboundRoute.name, PbxOutboundRoute.customer_id, PbxOutboundRoute.gateway_id, PbxOutboundRoute.pattern,
                                Customer.name).filter(PbxOutboundRoute.customer_id==Customer.id).all():
                items.append({'id': outbound_route[0],'name': outbound_route[1], 'customer_id': outbound_route[2],
                              'gateway_id': outbound_route[3], 'pattern': outbound_route[4], 'customer_name': outbound_route[5],
                              'gateway': get_gateway(outbound_route[3])})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def outroute_by_id(self, id, **kw):
        items=[]
        try:
            for outbound_route in db.query(PbxOutboundRoute.id, PbxOutboundRoute.name, PbxOutboundRoute.customer_id, PbxOutboundRoute.gateway_id, PbxOutboundRoute.pattern,
                Customer.name).filter(PbxOutboundRoute.customer_id==Customer.id).filter(PbxOutboundRoute.id==id).all():
                items.append({'id': outbound_route[0],'name': outbound_route[1], 'customer_id': outbound_route[2],
                              'gateway_id': outbound_route[3], 'pattern': outbound_route[4], 'customer_name': outbound_route[5],
                              'gateway': get_gateway(outbound_route[3])})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    def add_outroute(self, **kw):
        schema = OutboundRouteForm()
        try:
            form_result = schema.to_python(request.params)
            outbound_route = PbxOutboundRoute()

            outbound_route.name = form_result.get('name')
            outbound_route.customer_id = form_result.get('customer_id')
            outbound_route.gateway_id = form_result.get('gateway_id')
            outbound_route.pattern = form_result.get('pattern')

            db.add(outbound_route)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully added outbound route."

    @authorize(super_user)
    def edit_outroute(self, **kw):
        schema = OutboundRouteForm()
        try:
            form_result = schema.to_python(request.params)
            outbound_route = PbxOutboundRoute.query.filter_by(id=form_result.get('outroute_id')).first()

            outbound_route.name = form_result.get('name')
            outbound_route.customer_id = form_result.get('customer_id')
            outbound_route.gateway_id = form_result.get('gateway_id')
            outbound_route.pattern = form_result.get('pattern')

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully edited outbound route."

    @authorize(super_user)
    def del_outroute(self, **kw):
        try:
            PbxOutboundRoute.query.filter_by(id=request.params.get('id')).delete()
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully deleted outbound route."

    @authorize(super_user)
    @jsonify
    def dids(self):
        items=[]
        try:
            for did in db.query(PbxDid.id, PbxDid.did, Customer.name, Customer.id, Customer.context,
                        PbxDid.active, PbxDid.t38, PbxDid.cnam, PbxDid.e911).filter(Customer.id==PbxDid.customer_id).order_by(PbxDid.did).all():
                items.append({'did': did[1],'customer_name': did[2], 'customer_id': did[3],
                              'context': did[4], 'active': did[5], 't38': did[6], 'cnam': did[7], 'e911': did[8]})

            return {'identifier': 'did', 'label': 'did', 'items': items}

        except Exception, e:
            return {'identifier': 'did', 'label': 'did', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    def add_did(self, **kw):
        schema = DIDForm()
        try:
            form_result = schema.to_python(request.params)
            customer = Customer.query.filter_by(id=form_result.get('customer_id', 0)).first()
            if customer:
                db.add(PbxDid(form_result.get('did', None), customer.id,
                    customer.context, customer.context, form_result.get('t38', False), form_result.get('e911', False),
                    form_result.get('cnam', False), form_result.get('active', True)))

                db.commit()
            else:
                return "Error: Failed to insert DID."

        except validators.Invalid, error:
            db.rollback()
            return 'Validation Error: %s' % error

        return "Successfully added DID."

    @authorize(super_user)
    def del_did(self, **kw):

        did = PbxDid.query.filter_by(did=request.params.get("did"), customer_id=request.params.get("customer_id")).first()

        try:
            if did:
                delete_did(did.context, did.id)
        except Exception, e:
            return 'Error: %s' % e

        return "Successfully deleted DID."

    @authorize(super_user)
    def update_did_grid(self, **kw):
        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:

                if i['customer_name'].isdigit():
                    customer = Customer.query.filter_by(id=i['customer_name']).first()
                else:
                    customer = Customer.query.filter_by(name=i['customer_name']).first()

                did = PbxDid.query.filter(PbxDid.did==i['did']).first()
                did.customer_id = customer.id
                did.context = customer.context
                did.domain = customer.context
                did.t38 = i['t38']
                did.cnam = i['cnam']
                did.e911 = i['e911']
                did.pbx_route_id = 0
                did.active = i['active']

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated DID."

    @authorize(logged_in)
    @jsonify
    def system_recordings(self):
        items = []
        try:
            dir = fs_vm_dir+session['context']+"/recordings/"
            try:
                for i in os.listdir(dir):
                    fo = generateFileObject(i, "",  dir)
                    items.append({'id': '1,'+fo["name"], 'name': 'Recording: '+fo["name"] , 'data': fo["path"], 'type': 1, 'real_id': ""})

            except:
                pass

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(logged_in)
    def upload_system_recording(self):

        myfile = request.params['uploadedfiles[]']

        if not myfile.filename.endswith(".wav"):
            return "Error uploading file. File must have .wav extension."

        try:
            dir = fs_vm_dir + "/"+session['context']+"/system/recordings/"
            permanent_file = open(os.path.join(dir,myfile.filename.lstrip(os.sep)), 'w')
            shutil.copyfileobj(myfile.file, permanent_file)
            myfile.file.close()
            permanent_file.close()

        except:
            return "Error uploading file. The administrator has been contacted."

        return "Successfully uploaded recording."

    @authorize(super_user)
    @jsonify
    def contexts(self, **kw):
        items=[]
        try:
            for context in PbxContext.query.all():
                customer = Customer.query.filter(Customer.id==context.customer_id).first()
                items.append({'id': context.id, 'context': context.context, 'profile': context.profile, 'caller_id_name': context.caller_id_name,
                              'caller_id_number': context.caller_id_number, 'customer_name': customer.name,
                              'gateway': context.gateway, 'customer_id': customer.id})

            return {'identifier': 'id', 'label': 'name', 'items': items}
        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def context_by_id(self, id, **kw):
        items=[]
        try:
            context = PbxContext.query.filter(PbxContext.id==id).first()
            customer = Customer.query.filter(Customer.id==context.customer_id).first()
            items.append({'id': context.id, 'context': context.context, 'profile': context.profile, 'caller_id_name': context.caller_id_name,
                          'caller_id_number': context.caller_id_number, 'customer_name': customer.name, 'gateway': context.gateway})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    def update_context_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:

                if i['profile'].isdigit():
                    profile = PbxProfile.query.filter_by(id=i['profile']).first()
                else:
                    profile = PbxProfile.query.filter_by(name=i['profile']).first()

                if i['default_gateway'].isdigit():
                    gateway = PbxGateway.query.filter_by(
                        id=int(i['default_gateway'])).first()
                else:
                    gateway = PbxGateway.query.filter_by(
                        name=i['default_gateway']).first()

                customer = Customer.query.filter_by(context=i['context']).first()

                context = PbxContext.query.filter_by(id=i['id']).first()
                context.pbx_profile_id = profile.id
                customer.default_gateway = gateway.name

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated Gateway."

    @authorize(super_user)
    def add_context(self, **kw):
        schema = ContextForm()
        try:
            form_result = schema.to_python(request.params)
            context = PbxContext()
            context.customer_id = form_result.get('customer_id')
            context.profile = form_result.get('profile')
            context.domain = form_result.get('context')
            context.context = form_result.get('context')
            context.caller_id_name = form_result.get('caller_id_name')
            context.caller_id_number = form_result.get('caller_id_number')
            context.gateway = u'default'

            db.add(context)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully added context."

    @authorize(super_user)
    def edit_context(self, **kw):
        schema = ContextEditForm()
        try:
            form_result = schema.to_python(request.params)
            context = PbxContext.query.filter(PbxContext.id==form_result.get('id')).first()
            context.profile = form_result.get('profile')
            context.caller_id_name = form_result.get('caller_id_name')
            context.caller_id_number = form_result.get('caller_id_number')
            context.gateway = form_result.get('gateway')

            db.add(context)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully edited context."

    @authorize(super_user)
    @jsonify
    def admins(self, **kw):
        items=[]
        try:
            for admin in AdminUser.query.all():
                for perm in admin.permissions:
                    log.debug("%s" % perm)
                items.append({'id': admin.id, 'name': admin.first_name+' '+admin.last_name,
                              'username': admin.username, 'password': admin.password, 'active': admin.active})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items,'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def admin_by_id(self, id, **kw):
        items=[]
        try:
            admin = AdminUser.query.filter(AdminUser.id==id).first()
            items.append({'id': admin.id, 'first_name': admin.first_name,
                          'last_name': admin.last_name, 'username': admin.username, 'password': admin.password})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    def add_admin(self, **kw):
        schema = AdminUserForm()
        try:
            form_result = schema.to_python(request.params)
            username = form_result.get('username')
            password = form_result.get('password')
            first_name = form_result.get('first_name')
            last_name = form_result.get('last_name')

            admin_user = AdminUser(username,password,first_name,last_name)
            db.add(admin_user)

            admin_group = AdminGroup.query.filter_by(id=1).first()
            admin_group.admin_users.append(admin_user)
            db.add(admin_group)

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully added admin user."

    @authorize(super_user)
    def edit_admin(self, **kw):
        schema = AdminEditUserForm()
        try:
            form_result = schema.to_python(request.params)
            user = AdminUser.query.filter(AdminUser.id==form_result.get('id')).first()
            user.password = form_result.get('password')
            user.first_name = form_result.get('first_name')
            user.last_name = form_result.get('last_name')

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully edited admin user."

    @authorize(super_user)
    def update_admin_grid(self, **kw):
        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                admin = AdminUser.query.filter_by(id=i['id']).first()
                admin.active = i['active']

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated admin."

    @authorize(super_user)
    def delete_admin(self, **kw):

        if not len(AdminUser.query.all())>1:
            return "You only have one admin! Create another, then delete this one."
        try:
            if request.params.get('id', 0) == session['user_id']:
                logout=True
            admin = AdminUser.query.filter(AdminUser.id==request.params.get('id', 0)).delete()

            db.commit()

        except Exception, e:
            db.rollback()
            return "Error deleting admin: %s" % e

        return  "Successfully deleted admin."


    @authorize(super_user)
    @jsonify
    def cust_admins(self, **kw):
        items=[]
        try:
            for user in User.query.all():
                perms=[]
                for perm in user.permissions:
                    perms.append(perm.name)
                if 'pbx_admin' in perms:
                    items.append({'id': user.id, 'customer_name': user.get_customer_name(user.customer_id),
                                  'active': user.active, 'perms': ','.join(perms),
                                  'name': user.first_name+' '+user.last_name, 'first_name': user.first_name,
                                  'last_name': user.last_name, 'username': user.username, 'password': user.password})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def cust_admin_by_id(self, id, **kw):
        items=[]
        try:
            user = User.query.filter_by(id=id).first()

            items.append({'id': user.id, 'customer_name': user.get_customer_name(user.customer_id),
                          'first_name': user.first_name, 'last_name': user.last_name,
                          'username': user.username, 'password': user.password,
                          'customer_id': user.customer_id, 'group_id': user.group_id})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'iss_error': True, 'message': str(e)}

    @authorize(super_user)
    def add_cust_admin(self, **kw):
        schema = CustUserAdminForm()
        try:
            form_result = schema.to_python(request.params)
            username = form_result.get('username')
            password = form_result.get('password')
            first_name = form_result.get('first_name')
            last_name = form_result.get('last_name')

            user = User(first_name, last_name, username, password, form_result.get('customer_id'), True)
            db.add(user)

            group = Group.query.filter(Group.name=='pbx_admin').first()
            group.users.append(user)

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully added admin user."

    @authorize(super_user)
    def edit_cust_admin(self, **kw):
        schema = AdminUserForm()

        try:
            form_result = schema.to_python(request.params)
            user = User.query.filter(User.id==form_result.get('id')).first()
            user.password = form_result.get('password')
            user.first_name = form_result.get('first_name')
            user.last_name = form_result.get('last_name')

            db.execute("UPDATE user_groups set group_id = :group_id WHERE user_id = :user_id",
                        {'group_id': form_result.get('group_id'), 'user_id': user.id})

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully edited admin user."

    @authorize(super_user)
    def update_cust_admin_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                u = User.query.filter_by(id=i['id']).first()
                u.active = i['active']

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully updated admin."

    @authorize(super_user)
    def billing(self, **kw):
        return render('admin/billing.html')

    @authorize(super_user)
    @jsonify
    def active_tickets(self):
        items=[]
        try:
            for ticket in Ticket.query.filter(Ticket.ticket_status_id!=4).all():
                items.append({'id': ticket.id, 'customer_id': ticket.customer_id, 'opened_by': ticket.opened_by,
                              'status': ticket.ticket_status_id, 'priority': ticket.ticket_priority_id,
                              'type': ticket.ticket_type_id, 'created': ticket.created.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'expected_resolve_date': ticket.expected_resolve_date.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'subject': ticket.subject, 'description': ticket.description})

            return {'identifier': 'id', 'label': 'id', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'id', 'items': items, 'is_message': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def closed_tickets(self):
        items=[]
        try:
            for ticket in Ticket.query.filter(Ticket.ticket_status_id==4).all():
                items.append({'id': ticket.id, 'customer_id': ticket.customer_id, 'opened_by': ticket.opened_by,
                              'status': ticket.ticket_status_id, 'priority': ticket.ticket_priority_id,
                              'type': ticket.ticket_type_id, 'created': ticket.created.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'expected_resolve_date': ticket.expected_resolve_date.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'subject': ticket.subject, 'description': ticket.description})

            return {'identifier': 'id', 'label': 'id', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'id', 'items': items, 'is_message': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def internal_tickets(self):
        items=[]
        try:
            for ticket in Ticket.query.filter(Ticket.ticket_status_id==7).all():
                items.append({'id': ticket.id, 'customer_id': ticket.customer_id, 'opened_by': ticket.opened_by,
                              'status': ticket.ticket_status_id, 'priority': ticket.ticket_priority_id,
                              'type': ticket.ticket_type_id, 'created': ticket.created.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'expected_resolve_date': ticket.expected_resolve_date.strftime("%m/%d/%Y %I:%M:%S %p"),
                              'subject': ticket.subject, 'description': ticket.description})

            return {'identifier': 'id', 'label': 'id', 'items': items}
        except Exception, e:
            return {'identifier': 'id', 'label': 'id', 'items': items, 'is_message': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def ticket_data(self):
        ticket_status_id =[]
        ticket_status_name =[]
        ticket_type_id = []
        ticket_type_name = []
        ticket_priority_id = []
        ticket_priority_name = []
        opened_by_id = []
        opened_by_name = []

        try:
            for ticket_status in TicketStatus.query.all():
                ticket_status_id.append(ticket_status.id)
                ticket_status_name.append(ticket_status.name)
            for ticket_type in TicketType.query.all():
                ticket_type_id.append(ticket_type.id)
                ticket_type_name.append(ticket_type.name)
            for ticket_priority in TicketPriority.query.all():
                ticket_priority_id.append(ticket_priority.id)
                ticket_priority_name.append(ticket_priority.name)
            for admin_user in AdminUser.query.all():
                opened_by_id.append(admin_user.id)
                opened_by_name.append(admin_user.first_name+' '+admin_user.last_name)

            return {'ticket_status_names': ticket_status_name, 'ticket_status_ids': ticket_status_id,
                        'ticket_type_names': ticket_type_name, 'ticket_type_ids': ticket_type_id,
                        'ticket_priority_names': ticket_priority_name, 'ticket_priority_ids': ticket_priority_id,
                        'opened_by_names': opened_by_name, 'opened_by_ids': opened_by_id}

        except Exception, e:
            return {'identifier': 'id', 'label': 'id', 'items': items, 'is_message': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def ticket_types(self):
        items=[]
        try:
            for ticket_type in TicketType.query.all():
                items.append({'id': ticket_type.id, 'name': ticket_type.name, 'description': ticket_type.description})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def ticket_statuses(self):
        items=[]
        try:
            for ticket_status in TicketStatus.query.all():
                items.append({'id': ticket_status.id, 'name': ticket_status.name, 'description': ticket_status.description})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}


    @authorize(super_user)
    @jsonify
    def ticket_priorities(self):
        items=[]
        try:
            for ticket_priority in TicketPriority.query.all():
                items.append({'id': ticket_priority.id, 'name': ticket_priority.name, 'description': ticket_priority.description})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    def ticket_add(self, **kw):
        schema = TicketForm()
        try:
            form_result = schema.to_python(request.params)
            ticket = Ticket()
            ticket.subject = form_result.get('subject')
            ticket.description = form_result.get('description')
            ticket.customer_id = form_result.get('customer_id')
            ticket.opened_by = form_result.get('user_id')
            ticket.ticket_status_id = form_result.get('status_id')
            ticket.ticket_priority_id = form_result.get('priority_id')
            ticket.ticket_type_id = form_result.get('type_id')
            ticket.expected_resolution_date = form_result.get('expected_resolution_date')

            db.add(ticket)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Validation Error: %s' % error

        return "Successfully added ticket."

    @authorize(super_user)
    def update_ticket_grid(self, **kw):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                ticket = Ticket.query.filter_by(id=i['id']).first()
                ticket.ticket_status_id = int(i['status'])
                ticket.ticket_type_id = int(i['type'])
                ticket.ticket_priority_id = int(i['priority'])

                db.commit()

            return "Successfully updated ticket."

        except Exception, e:
            db.rollback()
            return "Error updating ticket: %s" % e

    @authorize(logged_in)
    @jsonify
    def channel_audio(self):

        def gen_file_object(filename, dir, root, expand=False, showHiddenFiles=False):
            path = dir+filename
            fullPath = path

            fObj = {}
            fObj["name"] = filename
            fObj["parentDir"] = dir
            fObj["path"] = path
            fObj["directory"] = os.path.isdir(fullPath)
            fObj["size"] = os.path.getsize(fullPath)
            fObj["modified"] = str(modification_date(fullPath)).strip("\"")

            children = []
            if os.path.isdir(fullPath):
                for o in os.listdir(fullPath):
                    if os.path.isdir(os.path.join(fullPath, o)):
                        fullpath =  os.path.join(fullPath, o)
                        path_arr = fullpath.split("/")
                        pts = path_arr[:-1]
                        dir = '/'.join(pts[5:])
                        children.append(gen_file_object(o, dir, root))
                    else:
                        children.append(o)
            fObj["children"] = children
            return fObj

        items = []
        dir = "/usr/local/freeswitch/recordings/channel_audio/"

        try:
            for i in os.listdir(dir):
                fo = gen_file_object(i, dir, "")
                items.append({'id': fo["name"], 'name': 'Recording: '+fo["name"] , 'data': fo["path"], 'type': 1, 'real_id': ""})
        except Exception, e:
            os.makedirs(dir)

        return {'identifier': 'id', 'label': 'name', 'items': items}

    @authorize(logged_in)
    def upload_channel_audio(self):

        myfile = request.params['uploadedfiles[]']

        if not myfile.filename.endswith(".wav"):
            return "Error uploading file. File must have .wav extension."
        try:
            dir = "/usr/local/freeswitch/recordings/channel_audio/"
            permanent_file = open(os.path.join(dir,myfile.filename.lstrip(os.sep)), 'w')
            shutil.copyfileobj(myfile.file, permanent_file)
            myfile.file.close()
            permanent_file.close()
        except:
            return "Error uploading file."

        return "Successfully uploaded recording."

    def residential_bulk_endpoint_add(self, user, customer, did, did_password):
        try:
            endpoint = PbxEndpoint()
            endpoint.auth_id = did
            endpoint.password = did_password
            endpoint.outbound_caller_id_name = user.name
            endpoint.outbound_caller_id_number = did
            endpoint.vm_email = user.username
            endpoint.vm_password = did[len(did)-4:]
            endpoint.vm_attach_email = False
            endpoint.vm_notify_email = False
            endpoint.vm_save = False
            endpoint.transfer_fallback_extension = 'operator'
            endpoint.accountcode = did
            endpoint.call_timeout = 20
            endpoint.timeout_destination = 0
            endpoint.user_id = user.id
            endpoint.user_context = customer.context
            endpoint.force_transfer_context = customer.context
            endpoint.user_originated = u'true'
            endpoint.toll_allow = u'domestic'
            endpoint.accountcode = did
            endpoint.calling_rule_id = 0
            endpoint.find_me = False
            endpoint.auto_provision = False
            endpoint.device_type_id = 0
            endpoint.account_type = 2
            endpoint.include_xml_directory = False
            endpoint.mac = None

            db.add(endpoint)
            db.flush()

            route = PbxRoute()
            route.context = customer.context
            route.domain = customer.context
            route.name = did
            route.continue_route = True
            route.voicemail_enable = True
            route.voicemail_ext = did
            route.pbx_route_type_id = 13
            route.pbx_to_id = endpoint.id

            db.add(route)
            db.flush()

            condition = PbxCondition()
            condition.context = customer.context
            condition.domain = customer.context
            condition.field = u'destination_number'
            condition.expression = u'^('+did+')$'
            condition.pbx_route_id = route.id

            db.add(condition)
            db.flush()

            action = PbxAction()
            action.pbx_condition_id = condition.id
            action.context = customer.context
            action.domain = customer.context
            action.precedence = 1
            action.application = u'set'
            action.data = u'hangup_after_bridge=true'

            db.add(action)
            db.flush()

            action = PbxAction()
            action.pbx_condition_id = condition.id
            action.context = customer.context
            action.domain = customer.context
            action.precedence = 1
            action.application = u'set'
            action.data = u'continue_on_fail=true'

            db.add(action)
            db.flush()

            action = PbxAction()
            action.pbx_condition_id = condition.id
            action.context = customer.context
            action.domain = customer.context
            action.precedence = 2
            action.application = u'set'
            action.data = u'call_timeout=20'

            db.add(action)
            db.flush()

            action = PbxAction()
            action.pbx_condition_id = condition.id
            action.context = customer.context
            action.domain = customer.context
            action.precedence = 3
            action.application = u'bridge'
            action.data = u'{force_transfer_context='+customer.context+'}sofia/' \
                          +'gmi/'+did+'%'+customer.context

            db.add(action)
            db.flush()

            db.add(PbxDid(did, customer.id,
                          customer.context, customer.context, False, False,
                          False, True, route.id))
        except Exception, e:
            return False

        return True

    @authorize(super_user)
    def upload_residential(self):

        myfile = request.params['uploadedfiles[]']
        cust_id = request.params['cust_id']
        ret = request.params['retention']

        if not myfile.filename.endswith(".xls"):
            return "Error uploading file. File must have .xls extension."

        try:
            dir = "/tmp"
            permanent_file = open(os.path.join(dir,myfile.filename.lstrip(os.sep)), 'w')
            shutil.copyfileobj(myfile.file, permanent_file)
            myfile.file.close()
            permanent_file.close()
        except:
            log.debug("Error uploading file.")

        import xlrd

        try:
            log.debug("/tmp/"+str(myfile.filename))
            wb = xlrd.open_workbook("/tmp/"+str(myfile.filename))
            sh = wb.sheet_by_index(0)

            #Customer Name, Address, City, State, Zip, Email, Web Password, DID, DID Password
            for i in xrange(sh.nrows):
                user = User()
                user.customer_id = cust_id
                user.first_name = str(sh.col(0)[i].value).split()[0]
                user.last_name = str(sh.col(0)[i].value).split()[1]
                user.address = str(sh.col(1)[i].value)
                user.city = str(sh.col(2)[i].value)
                user.state = str(sh.col(3)[i].value)
                user.zip = str(sh.col(4)[i].value)
                user.username = str(sh.col(5)[i].value)
                user.password = str(sh.col(6)[i].value)
                user.active = True

                db.add(user)
                db.flush()

                customer = Customer.query.filter_by(id=cust_id).first()
                if not residential_bulk_endpoint_add(user, customer,
                                              str(sh.col(7)[i].value),
                                              str(sh.col(8)[i].value)):
                    raise Exception("Failed to insert residential user.")

                db.commit()
        except:
            log.debug("Error parsing file. Please check the format and try again.")

        log.debug("Successfully uploaded residential customers.")

    @authorize(super_user)
    @jsonify
    def termination_customers(self):
        items=[]

        try:
            for tc in TerminationCustomer.query.all():
                items.append({'id': tc.id, 'name': tc.name,
                              'ips': tc.ips,
                              'escaped_ips': '\.'.join(tc.ips.split(".")),
                              'pattern': tc.pattern,
                              'context': tc.context,
                              'termination_gateway_id': tc.termination_gateway_id,
                              'termination_gateway_ips': TerminationGateway.query.filter_by(
                                  id=tc.termination_gateway_id).first().ips,
                              'term_gateway_ip_arr': TerminationGateway.query.filter_by(id=tc.termination_gateway_id).first().ips.split("|"),
                              'active': tc.active})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def termination_customer_by_id(self, id, **kw):
        items=[]
        try:
            term_cust = TerminationCustomer.query.filter(TerminationCustomer.id==id).first()
            if term_cust:
                items.append({'id': term_cust.id, 'ips': term_cust.ips,
                              'customer_id': term_cust.customer_id,
                              'termination_gateway_id': term_cust.termination_gateway_id,
                              'active': term_cust.active, 'context': term_cust.context,
                              'pattern': term_cust.pattern})

                return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    @jsonify
    def termination_gateway_by_id(self, id, **kw):
        items=[]
        try:
            term_gateway = TerminationGateway.query.filter(TerminationGateway.id==id).first()
            if term_gateway:
                items.append({'id': term_gateway.id,
                              'ips': term_gateway.ips,
                              'name': term_gateway.name})

                return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name',
                    'items': items, 'is_error': True, 'message': str(e)}

    @authorize(super_user)
    def add_term_cust(self):
        schema = TerminationCustomerForm()
        try:
            res = schema.to_python(request.params)
            term_cust = TerminationCustomer()
            term_cust.name = Customer.query.filter_by(id=res.get('customer_id')).first().name
            term_cust.customer_id = res.get('customer_id')
            term_cust.termination_gateway_id = res.get('termination_gateway_id')
            term_cust.context = res.get('context')
            term_cust.ips = res.get('ips')
            term_cust.pattern = res.get('pattern')
            term_cust.active = res.get('active', 'false') == "true"

            db.add(term_cust)
            db.commit()

        except Exception, e:
            db.rollback()
            return 'Error: %s' % e

        return "Successfully created termination customer."

    @authorize(super_user)
    def edit_term_cust(self):
        schema = TerminationCustomerForm()
        try:
            res = schema.to_python(request.params)
            term_cust = TerminationCustomer.query.filter_by(id=res.get('orig_term_customer_id', 0)).first()
            if term_cust:
                term_cust.name = Customer.query.filter_by(id=res.get('customer_id')).first().name
                term_cust.customer_id = res.get('customer_id')
                term_cust.termination_gateway_id = res.get('termination_gateway_id')
                term_cust.context = res.get('context')
                term_cust.ips = res.get('ips')
                term_cust.pattern = res.get('pattern')
                term_cust.active = res.get('active', 'false') == "true"
            else:
                raise Exception("No Term Customer!")

            db.commit()

        except Exception, e:
            db.rollback()
            return 'Error: %s' % e

        return "Successfully edited termination customer."

    @authorize(super_user)
    def delete_term_cust(self, **kw):

        try:
            TerminationCustomer.query.filter_by(id=request.params.get("id")).delete()
            db.commit()

        except Exception, e:
            db.rollback()
            return "Exception: %s" % e

        return "Successfully deleted termination customer."

    @authorize(super_user)
    def add_term_gateway(self):
        schema = TerminationGatewayForm()

        try:
            res = schema.to_python(request.params)
            term_gateway = TerminationGateway()
            term_gateway.name = res.get('name')
            term_gateway.ips = res.get('ips')

            db.add(term_gateway)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully created termination gateway."

    @authorize(super_user)
    def edit_term_gateway(self):
        schema = TerminationGatewayForm()

        try:
            res = schema.to_python(request.params)
            term_gateway = TerminationGateway.query.filter_by(id=res.get('id', 0)).first()
            term_gateway.name = res.get('name')
            term_gateway.ips = res.get('ips')

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s' % error
        except Exception, e:
            return "Exception: {0}".format(e)

        return "Successfully edited termination gateway."

    @authorize(super_user)
    def delete_term_gateway(self, **kw):

        try:
            TerminationGateway.query.filter_by(id=request.params.get("id")).delete()
            db.commit()

        except Exception, e:
            db.rollback()
            return "Exception: %s" % e

        return "Successfully deleted termination gateway."

    @authorize(super_user)
    @jsonify
    def termination_gateways(self):
        items=[]
        try:
            for tc in TerminationGateway.query.all():
                items.append({'id': tc.id, 'name': tc.name, 'ips': tc.ips})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(super_user)
    @jsonify
    def termination_gateway_store(self):
        items=[]
        try:
            for gateway in TerminationGateway.query.all():
                items.append({'id': gateway.id, 'name': gateway.name, 'ips': gateway.ips})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'messages': str(e)}

    @authorize(logged_in)
    def cdr(self, id, **kw):
        import csv
        from cStringIO import StringIO

        sdate = request.params.get("sdate", 'TIMESTAMP')
        edate = request.params.get("edate", 'CURRENT_TIMESTAMP')

        sdate = "TIMESTAMP '"+sdate+"'" if sdate != 'TIMESTAMP' else "CURRENT_TIMESTAMP - INTERVAL '1 MONTH'"
        edate = "TIMESTAMP '"+edate+"' + interval '1 day'" if edate != 'CURRENT_TIMESTAMP' else 'CURRENT_TIMESTAMP'

        s = StringIO()
        writer = csv.writer(s)
        writer.writerow(['id', 'caller_id_name', 'caller_id_number', 'destination_number', 'start_stamp',
                         'answer_stamp', 'end_stamp', 'duration', 'billsec', 'hangup_cause'])

        for cdr in db.execute("SELECT * "
                              "FROM cdr "
                              "WHERE context = :context "
                              "AND cdr.start_stamp > CURRENT_TIMESTAMP - INTERVAL '1 MONTH' AND cdr.end_stamp < CURRENT_TIMESTAMP "
                              "ORDER BY start_stamp DESC", {'context': id}).fetchall():

            writer.writerow([cdr.id, cdr.caller_id_name, cdr.caller_id_number, cdr.destination_number,
                   fix_date(cdr.start_stamp), fix_date(cdr.answer_stamp),
                       fix_date(cdr.end_stamp), cdr.duration, cdr.billsec, cdr.hangup_cause])

        body = s.getvalue()

        response = Response()
        response.headers['Content-type'] = 'text/csv'
        response.headers['Content-disposition'] = 'attachment; filename='+id+'.csv'
        response.body = body

        return response(request.environ, self.start_response)