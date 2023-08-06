'''
    This Source Code Form is subject to the terms of the Mozilla Public
    License, v. 2.0. If a copy of the MPL was not distributed with this
    file, You can obtain one at http://mozilla.org/MPL/2.0/.

    Software distributed under the License is distributed on an 'AS IS'
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
'''

import datetime
from datetime import datetime
from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.types import Integer, DateTime, Boolean, Unicode, UnicodeText, Float, Numeric
from sqlalchemy.orm import relation, synonym, relationship, backref
from freepybx.model.meta import db, Base, metadata


customer_services = Table('customer_services', metadata,
    Column('customer_id', Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE')),
    Column('billing_service_id', Integer, ForeignKey('billing_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
)


class BillingService(Base):
    __tablename__='billing_services'

    id = Column(Integer, autoincrement=True, primary_key=True)
    billing_service_type_id = Column(Integer, ForeignKey('billing_service_types.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    service_id = Column(Integer, default=0)
    name = Column(Unicode(64))
    description = Column(Unicode(1024))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class BillingServiceType(Base):
    __tablename__='billing_service_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(1024))

    billing_service = relationship('BillingService', backref='billing_service_types')

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<BillingServiceType({0},{1},{2},{3})>'.format(
            self.id,self.billing_service_type_id, self.name, self.description)


class VoipService(Base):
    __tablename__='voip_services'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    voip_service_plan_id = Column(Integer, ForeignKey('voip_service_plans.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(Unicode(64))
    description = Column(Unicode(1024))
    created = Column(DateTime,default=datetime.now())
    start_date = Column(DateTime,default=datetime.now())
    end_date = Column(DateTime)
    interval = Column(Integer, default=1)

    voip_service_plan = relationship('VoipServicePlan', backref='voip_services')


class VoipServicePlan(Base):
    __tablename__='voip_service_plans'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(1024))
    voip_service_type_id = Column(Integer, ForeignKey('voip_service_types.id',
        onupdate='CASCADE', ondelete='CASCADE'))

    service_profile_id = Column(Integer)

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class VoipServiceType(Base):
    __tablename__='voip_service_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(1024))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class VoipExtensionServiceProfile(Base):
    __tablename__='voip_extension_service_profiles'

    id = Column(Integer, autoincrement=True, primary_key=True)
    voip_service_id = Column(Integer, ForeignKey('voip_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    voip_service_policy_id = Column(Integer, default=0)
    included_minutes_enforced = Column(Boolean, default=False)
    included_minutes = Column(Integer, default=0)
    overage_fee = Column(Numeric)
    billable_seconds_increment = Column(Integer, default=0)
    per_call = Column(Boolean, default=True)


class VoipTrunkServiceProfile(Base):
    __tablename__='voip_trunk_service_profiles'

    id = Column(Integer, autoincrement=True, primary_key=True)
    voip_service_id = Column(Integer, ForeignKey('voip_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    voip_service_policy_id = Column(Integer, default=0)
    max_trunks = Column(Integer, default=0)
    included_minutes = Column(Integer, default=0)
    overage_fee = Column(Numeric)
    billable_seconds_increment = Column(Integer, default=0)
    per_call = Column(Boolean, default=True)


class VoipPbxServiceProfile(Base):
    __tablename__='pbx_voip_service_profiles'

    id = Column(Integer, autoincrement=True, primary_key=True)
    voip_service_id = Column(Integer, ForeignKey('voip_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    voip_service_policy_id = Column(Integer, default=0)
    name = Column(Unicode(64))
    description = Column(UnicodeText)
    amount = Column(Numeric)
    max_extensions_enforced = Column(Boolean, default=False)
    max_extensions = Column(Integer, default=0)
    included_extension_minutes_enforced = Column(Boolean, default=False)
    included_extension_minutes = Column(Integer, default=0)
    included_pbx_minutes = Column(Integer, default=0)
    included_pbx_minutes_enforced = Column(Boolean, default=False)
    can_create_extensions = Column(Boolean, default=True)
    can_delete_metered_extensions = Column(Boolean, default=True)
    overage_fee = Column(Numeric)
    billable_seconds_increment = Column(Integer, default=0)
    max_virtual_extensions = Column(Integer, default=0)
    enforce_max_virtual_extensions = Column(Boolean, default=False)


class VoipServicePolicy(Base):
    __tablename__='voip_service_policies'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(UnicodeText)
    disconnect = Column(Boolean, default=False)
    play_recording = Column(Boolean, default=False)
    reroute_call = Column(Boolean, default=False)
    pbx_route_id = Column(Integer, default=411)
    auto_pool_deduct = Column(Boolean, default=False)
    auto_fill_pool = Column(Boolean, default=False)
    default_pool_fill_amount = Column(Numeric, default=0)
    ignore = Column(Boolean, default=True)


class BillingServiceFee(Base):
    __tablename__='billing_service_fees'

    id = Column(Integer, autoincrement=True, primary_key=True)
    billing_service_fee_type_id = Column(Integer, ForeignKey('billing_service_fee_types.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    billing_service_id = Column(Integer, ForeignKey('billing_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(Unicode(64))
    description = Column(Unicode(128))
    flat_fee_amount = Column(Numeric, default=0)
    flat_fee_description = Column(UnicodeText)
    taxable = Column(Boolean, default=False)
    percentage = Column(Boolean, default=False)
    percentage_amount = Column(Numeric, default=0)


class BillingServiceFeeType(Base):
    __tablename__='billing_service_fee_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))

    billing_service_fee = relationship('BillingServiceFee',
        backref='billing_service_fee_types')

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class BillingCycleType(Base):
    __tablename__='billing_cycle_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(128))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description

class ProviderBillingProfile(Base):
    __tablename__='provider_billing_profiles'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    provider_billing_gateway_id = Column(Integer, ForeignKey('provider_billing_gateways.id',
        onupdate='CASCADE', ondelete='CASCADE'))


class BillingProduct(Base):
    __tablename__='billing_products'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(Unicode(64))
    description = Column(Unicode(1024))
    amount = Column(Numeric, default=0)

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class BillingProductType(Base):
    __tablename__='billing_product_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(1024))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class BillingProductFee(Base):
    __tablename__='billing_product_fees'

    id = Column(Integer, autoincrement=True, primary_key=True)
    flat_fee = Column(Boolean, default=False)
    flat_fee_amount = Column(Numeric, default=0)
    flat_fee_description = Column(UnicodeText)
    taxable = Column(Boolean, default=False)
    percentage = Column(Boolean, default=False)
    percentage_amount = Column(Numeric, default=0)


class ProviderBillingGateway(Base):
    __tablename__='provider_billing_gateways'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(Unicode(64))
    description = Column(Unicode(128))
    billing_api_type_id = Column(Integer, default=1)


class ProviderBillingApiType(Base):
    __tablename__='provider_billing_api_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(128))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class AuthorizeNetAccount(Base):
    __tablename__='authorize_net_accounts'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    api_username = Column(Unicode(128))
    transaction_id = Column(Unicode(128))


class Invoice(Base):
    __tablename__='invoices'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    created = Column(DateTime,default=datetime.now())
    billing_service_id = Column(Integer, ForeignKey('billing_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    payment_id = Column(Integer, default=0)


class InvoiceItem(Base):
    __tablename__='invoice_items'

    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    invoice_id = Column(Integer, ForeignKey('invoices.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    billing_service_id = Column(Integer, ForeignKey('billing_services.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    created = Column(DateTime,default=datetime.now())
    line_description = Column(Unicode(1024))
    amount = Column(Numeric, default=0)


class Payment(Base):
    __tablename__='payments'

    id = Column(Integer, autoincrement=True, primary_key=True)
    invoice_id = Column(Integer, default=0)
    customer_id = Column(Integer, ForeignKey('customers.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    payment_type_id = Column(Integer, ForeignKey('payment_types.id',
        onupdate='CASCADE', ondelete='CASCADE'))
    created = Column(DateTime,default=datetime.now())
    amount = Column(Numeric, default=0)


class PaymentType(Base):
    __tablename__='payment_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(64))
    description = Column(Unicode(128))

    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description
