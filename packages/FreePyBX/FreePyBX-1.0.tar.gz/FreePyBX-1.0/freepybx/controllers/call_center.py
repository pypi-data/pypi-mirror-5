""" This Source Code Form is subject to the terms of the Mozilla Public
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
    remedy known factual inaccuracies."""

import os
import sys
import urllib, urllib2
import simplejson as json
import pprint
import os, sys
import logging
import cgi
import simplejson as json
from simplejson import loads, dumps

import formencode
from formencode import validators

from stat import *
from datetime import datetime

from pylons import request, response, session, config, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators.rest import restrict
from pylons.decorators import validate, jsonify

from freepybx.lib.base import BaseController, render
from freepybx.lib.util import *
from freepybx.lib.auth import *
from freepybx.lib.validators import *
from freepybx.model import meta
from freepybx.model.meta import *
from freepybx.model.meta import db

from itertools import chain
from genshi import HTML
from decorator import decorator

from webob import Request, Response
import cgitb; cgitb.enable()


logged_in = IsLoggedIn()
log = logging.getLogger(__name__)

DEBUG=False

fs_vm_dir = config['app_conf']['fs_vm_dir']
ESL_HOST = config['app_conf']['esl_host']
ESL_PORT = config['app_conf']['esl_port']
ESL_PASS = config['app_conf']['esl_pass']


class DataInputError(Exception):
    message=""
    def __init__(self, message=None):
        Exception.__init__(self, message or self.message)


class CallCenterController(BaseController):

    @authorize(logged_in)
    @jsonify
    def queues(self):
        items=[]
        try:
            for queue in CallCenterQueue.query.filter_by(context=session['context']).all():
                items.append({'id': queue.id, 'name': queue.name})

            return {'identifier': 'name', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'name', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    def ccq_add(self):
        schema = QueueForm()
        try:
            form_result = schema.to_python(request.params)
            ccq = CallCenterQueue()
            ccq.name = form_result['name']
            ccq.context = session['context']
            ccq.domain = session['context']
            ccq.audio_type = form_result.get('audio_name').split(",")[0]
            ccq.audio_name = form_result.get('audio_name').split(",")[1]
            ccq.moh_sound = form_result.get('moh_sound', 'local_stream://moh')
            ccq.time_base_score = form_result.get('time_base_score', 'system')
            ccq.max_wait_time = form_result.get('max_wait_time', 0)
            ccq.max_wait_time_with_no_agent = form_result.get('max_wait_time_with_no_agent', 0)
            ccq.max_wait_time_with_no_agent_reached = form_result.get('max_wait_time_with_no_agent_reached', 5)
            ccq.tier_rules_apply = form_result.get('tier_rules_apply', False)
            ccq.tier_rule_wait_second = form_result.get('tier_rule_wait_second', 300)
            ccq.tier_rule_wait_multiply_level = form_result.get('tier_rule_wait_multiply_level', False)
            ccq.tier_rule_agent_no_wait = form_result.get('tier_rule_agent_no_wait', False)
            ccq.discard_abandoned_after = form_result.get('discard_abandoned_after', 1800)
            ccq.abandoned_resume_allowed = form_result.get('abandoned_resume_allowed', False)
            ccq.strategy = form_result.get('strategy', 'callback')
            ccq.failed_route_id = form_result.get('failed_route_id', 0)
            ccq.record_calls = form_result.get('record_calls', False)
            ccq.announce_position = form_result.get('announce_position', False)
            announce_sound = form_result.get('announce_sound', None)
            if announce_sound:
                ccq.announce_sound = announce_sound.split(",")[1]
            else:
                ccq.announce_sound = None
                ccq.announce_frequency = form_result.get('announce_frequency', 60)
            db.add(ccq)
            db.flush()

            dir = fs_vm_dir+session['context']+"/queue-recordings/"+ccq.name

            if not os.path.exists(dir):
                os.makedirs(dir)

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s.' % error

        route = PbxRoute()
        route.context = session['context']
        route.domain = session['context']
        route.name = form_result['name']
        route.continue_route = True
        route.voicemail_enable = True
        route.voicemail_ext = form_result['name']
        route.pbx_route_type_id = 10
        route.pbx_to_id = ccq.id

        db.add(route)
        db.commit()

        return "Successfully added Call Center queue "+form_result['name']+"."

    @authorize(logged_in)
    def ccq_edit(self):
        schema = QueueEditForm()
        try:
            form_result = schema.to_python(request.params)
            ccq =  CallCenterQueue.query.filter_by(context=session['context']).filter_by(id=form_result.get('ccq_id')).first()
            ccq.context = session['context']
            ccq.domain = session['context']
            ccq.audio_type = form_result.get('audio_name').split(",")[0]
            ccq.audio_name = form_result.get('audio_name').split(",")[1]
            ccq.moh_sound = form_result.get('moh_sound', 'local_stream://moh')
            ccq.time_base_score = form_result.get('time_base_score', 'system')
            ccq.max_wait_time = form_result.get('max_wait_time', 0)
            ccq.max_wait_time_with_no_agent = form_result.get('max_wait_time_with_no_agent', 0)
            ccq.max_wait_time_with_no_agent_reached = form_result.get('max_wait_time_with_no_agent_reached', 5)
            ccq.tier_rules_apply = form_result.get('tier_rules_apply', False)
            ccq.tier_rule_wait_second = form_result.get('tier_rule_wait_second', 300)
            ccq.tier_rule_wait_multiply_level = form_result.get('tier_rule_wait_multiply_level', False)
            ccq.tier_rule_agent_no_wait = form_result.get('tier_rule_agent_no_wait', False)
            ccq.discard_abandoned_after = form_result.get('discard_abandoned_after', 1800)
            ccq.abandoned_resume_allowed = form_result.get('abandoned_resume_allowed', False)
            ccq.strategy = form_result.get('strategy')
            ccq.failed_route_id = form_result.get('failed_route_id', 0)
            ccq.record_calls = form_result.get('record_calls', False)
            ccq.announce_position = form_result.get('announce_position', False)
            ccq.announce_sound = form_result.get('announce_sound').split(",")[1]
            ccq.announce_frequency = form_result.get('announce_frequency')

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s.' % error

        return "Successfully updated Call Center queue "+ccq.name+"."

    @authorize(logged_in)
    @jsonify
    def ccq_by_id(self, id, **kw):
        items=[]
        try:
            for ccq in CallCenterQueue.query.filter_by(context=session['context']).filter_by(id=id).all():
                items.append({'id': ccq.id, 'name': ccq.name, 'audio_type': ccq.audio_type, 'audio_name': str(ccq.audio_type)+","+str(ccq.audio_name),
                              'moh_sound': ccq.moh_sound, 'time_base_score': ccq.time_base_score, 'max_wait_time': ccq.max_wait_time,
                              'max_wait_time_with_no_agent': ccq.max_wait_time_with_no_agent, 'max_wait_time_with_no_agent_reached': ccq.max_wait_time_with_no_agent_reached,
                              'tier_rules_apply': ccq.tier_rules_apply, 'tier_rule_wait_second': ccq.tier_rule_wait_second, 'tier_rule_wait_multiply_level': ccq.tier_rule_wait_multiply_level,
                              'tier_rule_agent_no_wait': ccq.tier_rule_agent_no_wait, 'discard_abandoned_after': ccq.discard_abandoned_after,
                              'abandoned_resume_allowed': ccq.abandoned_resume_allowed, 'strategy': ccq.strategy, 'failed_route_id': ccq.failed_route_id,
                              'record_calls': ccq.record_calls, 'announce_position': ccq.announce_position, 'announce_sound': "1,"+ccq.announce_sound,
                              'announce_frequency': ccq.announce_frequency})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    @jsonify
    def ccq_audio(self):
        items = []
        try:
            dir = fs_vm_dir+session['context']+"/recordings/"
            for i in os.listdir(dir):
                fo = generateFileObject(i, "",  dir)
                items.append({'id': '1,'+fo["name"], 'name': 'Recording: '+fo["name"] , 'data': fo["path"], 'type': 1, 'real_id': ""})

            items.append({'id': '0,local_stream://moh', 'name': 'Default Music on Hold' , 'data': 'local_stream://moh', 'type': 1, 'real_id': ""})
            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    def delete_queue(self, **kw):

        try:
            id = request.params.get('id', None)
            q = CallCenterQueue.query.filter(CallCenterQueue.id==id).filter(CallCenterQueue.context==session['context']).first()

            queue = CallCenterQueue.query.filter(CallCenterQueue.id==q.id).first()
            CallCenterTier.query.filter(CallCenterTier.queue_id==queue.id).delete()
            CallCenterQueue.query.filter(CallCenterQueue.id==q.id).delete()

            db.commit()

            return "Successfully removed queue."

        except Exception, e:
            db.rollback()
            return "Error: %s" % e

    @authorize(logged_in)
    @jsonify
    def agents(self):
        items=[]
        try:
            for agent in CallCenterAgent.query.filter_by(context=session['context']).all():
                items.append({'id': agent.id, 'extension': agent.extension, 'status': agent.status})

            return {'identifier': 'extension', 'label': 'extension', 'items': items}

        except Exception, e:
            return {'identifier': 'extension', 'label': 'extension', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    @jsonify
    def agent_avail_endpoints(self):
        items=[]
        try:
            ext = request.params.get('ext', None)
            if ext:
                items.append({'id': 0, 'extension': ext})

            for row in PbxEndpoint.query.filter_by(user_context=session['context'])\
                        .order_by(PbxEndpoint.auth_id).all():
                if CallCenterAgent.query.filter_by(extension=row.auth_id)\
                        .filter_by(context=session['context']).count()>0:
                    continue

                items.append({'id': row.id, 'extension': row.auth_id})

            return {'identifier': 'extension', 'label': 'extension', 'items': items}

        except Exception, e:
            return {'identifier': 'extension', 'label': 'extension', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    @jsonify
    def agent_endpoints(self):
        items=[]
        try:
            for row in PbxEndpoint.query.filter_by(user_context=session['context'])\
                    .order_by(PbxEndpoint.auth_id).all():
                items.append({'id': row.id, 'extension': row.auth_id})

            return {'identifier': 'extension', 'label': 'extension', 'items': items}

        except Exception, e:
            return {'identifier': 'extension', 'label': 'extension', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    def agent_add(self):
        schema = AgentForm()
        try:
            form_result = schema.to_python(request.params)
            cca = CallCenterAgent()
            cca.extension = form_result.get('extension')
            endpoint = PbxEndpoint.query.filter_by(user_context=session['context'])\
                        .filter(PbxEndpoint.auth_id==cca.extension).first()
            cca.context = session['context']
            cca.domain = session['context']
            cca.type = 'callback'
            cca.system = 'single_box'
            cca.name = cca.extension+"@"+session['context']
            cca.timeout = form_result.get('timeout', 30)
            cca.contact = "[call_timeout="+cca.timeout+"]user/"+cca.name
            cca.max_no_answer = form_result.get('max_no_answer', 3)
            cca.wrap_up_time = form_result.get('wrap_up_time', 30)
            cca.reject_delay_time = form_result.get('reject_delay_time', 30)
            cca.busy_delay_time = form_result.get('busy_delay_time', 0)
            cca.no_answer_delay_time = form_result.get('no_answer_delay_time', 5)
            cca.record_calls = form_result.get('record_calls', 0)
            cca.status = 'Available'
            cca.state = 'Waiting'
            cca.user_id = endpoint.user_id
            cca.pbx_endpoint_id = endpoint.id

            db.add(cca)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s.' % error

        return "Successfully added agent."

    @authorize(logged_in)
    def agent_edit(self):
        schema = AgentEditForm()
        try:
            form_result = schema.to_python(request.params)
            cca = CallCenterAgent.query.filter_by(context=session['context'])\
                    .filter(CallCenterAgent.id==form_result.get('agent_id')).first()
            cca.extension = form_result.get('extension')
            endpoint = PbxEndpoint.query.filter_by(user_context=session['context'])\
                    .filter(PbxEndpoint.auth_id==cca.extension).first()
            cca.context = session['context']
            cca.domain = session['context']
            cca.type = 'callback'
            cca.record_calls = form_result.get('record_calls', 0)
            cca.timeout = form_result.get('timeout', 30)
            cca.max_no_answer = form_result.get('max_no_answer', 3)
            cca.wrap_up_time = form_result.get('wrap_up_time', 30)
            cca.reject_delay_time = form_result.get('reject_delay_time', 30)
            cca.busy_delay_time = form_result.get('busy_delay_time', 0)
            cca.no_answer_delay_time = form_result.get('no_answer_delay_time', 5)
            cca.user_id = endpoint.user_id
            cca.pbx_endpoint_id = endpoint.id

            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s.' % error

        return "Successfully edited agent."

    @restrict("GET")
    @authorize(logged_in)
    def del_agent(self, **kw):

        try:
            CallCenterAgent.query.filter_by(id=request.params.get('id', 0)).delete()
            db.commit()

        except:
            db.rollback()
            return "Error deleting agent."

        return  "Successfully deleted agent."

    @authorize(logged_in)
    @jsonify
    def cca_by_id(self, id, **kw):
        items=[]
        try:
            for cca in CallCenterAgent.query.filter_by(context=session['context']).filter_by(id=id).all():
                items.append({'id': cca.id, 'extension': cca.extension, 'type': cca.type, 'timeout': cca.timeout,
                              'max_no_answer': cca.max_no_answer, 'wrap_up_time': cca.wrap_up_time, 'reject_delay_time': cca.reject_delay_time,
                              'busy_delay_time': cca.busy_delay_time, 'no_answer_delay_time': cca.no_answer_delay_time, 'record_calls': cca.record_calls})

            return {'identifier': 'id', 'label': 'name', 'items': items}

        except Exception,e:
            return {'identifier': 'id', 'label': 'name', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    def update_agent_grid(self):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                log.debug(w['modified'])
                fsa = CallCenterAgent.query.filter(CallCenterAgent.name==str(i['extension'])+"@"+str(session['context'])).first()
                fsa.status = i['status']

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Successfully update agent."

    @authorize(logged_in)
    @jsonify
    def tiers(self):
        items=[]
        try:
            for tier in CallCenterTier.query.join(CallCenterQueue)\
                    .filter(CallCenterQueue.context==session['context']).all():
                agent = get_agent(tier.agent_id)
                queue = get_queue(tier.queue_id)
                items.append({'id': tier.id, 'agent': agent.extension,
                              'queue': queue.name, 'level': tier.level,
                              'position': tier.position, 'state': tier.state})

            return {'identifier': 'id', 'label': 'agent', 'items': items}

        except Exception, e:
            return {'identifier': 'id', 'label': 'agent', 'items': items, 'is_error': True, 'message': str(e)}

    @authorize(logged_in)
    def tier_add(self):
        schema = TierForm()
        try:
            form_result = schema.to_python(request.params)
            cca = CallCenterAgent.query.filter_by(extension=form_result.get('agent_extension', None))\
                    .filter_by(context=session['context']).first()
            cur_cct = CallCenterTier.query.filter_by(agent=cca.name).first()
            ccq = CallCenterQueue.query.filter_by(name=form_result.get('queue_name', None)).first()

            if cur_cct:
                return "Agent in tier already exists!"

            cct = CallCenterTier()
            cct.extension = cca.extension
            cct.queue_id = ccq.id
            cct.agent_id = cca.id
            cct.queue = str(ccq.name)+"@"+session['context']
            cct.agent = str(cca.extension)+"@"+session['context']
            cct.level = form_result.get('level', 1)
            cct.state = 'Ready'
            cct.position = form_result.get('position', 1)
            cct.context = session['context']
            cct.domain = session['context']

            db.add(cct)
            db.commit()

        except validators.Invalid, error:
            db.rollback()
            return 'Error: %s.' % error

        return "Successfully created tier agent."

    @authorize(logged_in)
    def update_tier_grid(self):

        try:
            w = loads(urllib.unquote_plus(request.params.get("data")))

            for i in w['modified']:
                log.debug(w['modified'])
                tier = CallCenterTier.query.filter_by(id=i['id']).first()

                tier.state = i['state']
                tier.level = i['level']
                tier.position = i['position']

                db.commit()

        except DataInputError, error:
            db.rollback()
            return 'Error: %s' % error

        return "Sucessfully updated agent tiers."

    @restrict("GET")
    @authorize(logged_in)
    def del_tier(self, **kw):

        try:
            CallCenterTier.query.filter_by(id=request.params.get('id', 0)).delete()
            db.commit()

        except:
            db.rollback()
            return "Error deleting tier agent."

        return  "Successfully deleted tier agent."

    #XXX: ???
    @authorize(logged_in)
    def cc_cdr_stats(self):
        pass

    @authorize(logged_in)
    @jsonify
    def get_queue_calls(self):

        try:
            user = User.query.filter_by(session_id=request.params.get("sid")).first()

            if user:
                context = user.get_context()
            else:
                return ""

            items = []
            sql = "SELECT * FROM call_center_callers WHERE queue like '%@{0}'".format(context)

            for call in db.execute(sql):
                items.append({'queue': call.queue.split("@")[0], 'cid_name': call.cid_name,
                              'cid_number': call.cid_number, 'agent': call.serving_agent.split("@")[0],
                              'state': call.state, 'uuid': call.uuid})

            if not len(items) == 0:
                return ""

            return items

        except Exception, e:
            {'is_error': True, 'message': str(e)}


    @restrict("POST")
    @authorize(logged_in)
    def delete_queue_recording(self, **params):

        try:
            path = request.params.get("data")
            queue = request.params.get("queue_name")
            file_name = path.split("/")[len(path.split("/"))-1]
            dir = fs_vm_dir+session['context']+"/queue-recordings/"+queue+"/"
            os.remove(os.path.join(dir, file_name))
        except:
            return "Error: Deleting queue recording."

        return "Deleted queue recording."

    @authorize(logged_in)
    @jsonify
    def get_queue_recordings(self):
        files = []
        try:
            queue = request.params.get("queue_name")

            dir = fs_vm_dir+session['context']+"/queue-recordings/"+queue
            for i in os.listdir(dir):
                path = dir+"/"+i
                id = i.split(".")[3].strip()
                row = PbxCdr.query.filter(PbxCdr.uuid==id).first()
                if row:
                    caller = row.caller_id_number[len(row.caller_id_number)-10:]
                    dest = row.destination_number
                    agent = PbxCdr.query.filter(PbxCdr.uuid==row.bleg_uuid).first()
                    agent_ext = agent.destination_number
                else:
                    agent_ext = "No CDR"
                    dest = "No CDR"
                    caller = "No CDR"

                tpath = "/vm/" +session['context']+"/queue-recordings/"+queue+"/"+i
                received = str(modification_date(path)).strip("\"")
                fsize = str(os.path.getsize(path))

                files.append({'name': caller, 'queue': queue, 'destination': dest,
                              'agent': agent_ext, 'path': tpath, 'received': received, 'size': fsize})

            return {'identifier': 'path', 'label': 'name', 'items': files}
        except Exception, e:
            return {'identifier': 'path', 'label': 'name', 'items': files}

    @authorize(logged_in)
    @jsonify
    def ad_audio(self):
        items = []
        dir = fs_vm_dir+session['context']+"/recordings/"
        try:
            for i in os.listdir(dir):
                fo = generateFileObject(i, "",  dir)
                items.append({'id': '1,'+fo["name"], 'name': 'Recording: '+fo["name"] ,
                              'data': fo["path"], 'type': 1, 'real_id': ""})

        except:
            pass

        return {'identifier': 'id', 'label': 'name', 'items': items}
    
    