# Copyright (c) 2015 OpenStack Foundation.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import datetime

from neutron_lib.db import api as db_api
from oslo_db import exception as db_exc
from oslo_utils import timeutils

from neutron.common import utils
from neutron.objects import quota as quota_obj


RESERVATION_EXPIRATION_TIMEOUT = 120  # seconds
UNLIMITED_QUOTA = -1


# Wrapper for utcnow - needed for mocking it in unit tests
def utcnow():
    return timeutils.utcnow()


class QuotaUsageInfo(collections.namedtuple(
        'QuotaUsageInfo', ['resource', 'project_id', 'used', 'dirty'])):
    """Information about resource quota usage."""


class ReservationInfo(collections.namedtuple(
        'ReservationInfo', ['reservation_id', 'project_id',
                            'expiration', 'deltas'])):
    """Information about a resource reservation."""


@db_api.retry_if_session_inactive()
@db_api.CONTEXT_READER
def get_quota_usage_by_resource_and_project(context, resource, project_id):
    """Return usage info for a given resource and project.

    :param context: Request context
    :param resource: Name of the resource
    :param project_id: Project identifier
    :returns: a QuotaUsageInfo instance
    """

    result = quota_obj.QuotaUsage.get_object_dirty_protected(
        context, resource=resource, project_id=project_id)
    if not result:
        return
    return QuotaUsageInfo(result.resource, result.project_id, result.in_use,
                          result.dirty)


@db_api.retry_if_session_inactive()
def get_quota_usage_by_resource(context, resource):
    objs = quota_obj.QuotaUsage.get_objects(context, resource=resource)
    return [QuotaUsageInfo(item.resource,
                           item.project_id,
                           item.in_use,
                           item.dirty) for item in objs]


@db_api.retry_if_session_inactive()
def get_quota_usage_by_project_id(context, project_id):
    objs = quota_obj.QuotaUsage.get_objects(context, project_id=project_id)
    return [QuotaUsageInfo(item.resource,
                           project_id,
                           item.in_use,
                           item.dirty) for item in objs]


@db_api.retry_if_session_inactive()
def set_quota_usage(context, resource, project_id, in_use=None, delta=False):
    """Set resource quota usage.

    :param context: instance of neutron context with db session
    :param resource: name of the resource for which usage is being set
    :param project_id: identifier of the project for which quota usage is
                       being set
    :param in_use: integer specifying the new quantity of used resources,
                   or a delta to apply to current used resource
    :param delta: Specifies whether in_use is an absolute number
                  or a delta (default to False)
    """
    with db_api.CONTEXT_WRITER.using(context):
        usage_data = quota_obj.QuotaUsage.get_object(
            context, resource=resource, project_id=project_id)
        if not usage_data:
            # Must create entry
            usage_data = quota_obj.QuotaUsage(
                context, resource=resource, project_id=project_id)
            usage_data.create()
        # Perform explicit comparison with None as 0 is a valid value
        if in_use is not None:
            if delta:
                in_use = usage_data.in_use + in_use
            usage_data.in_use = in_use
        # After an explicit update the dirty bit should always be reset
        usage_data.dirty = False
        usage_data.update()
    return QuotaUsageInfo(usage_data.resource, usage_data.project_id,
                          usage_data.in_use, usage_data.dirty)


@db_api.retry_if_session_inactive()
@db_api.CONTEXT_WRITER
def set_resources_quota_usage_dirty(context, resources, project_id,
                                    dirty=True):
    """Set quota usage dirty bit for a given project and one/multiple resources

    :param resources: (list of strings, string) list of resources or one single
                      resource, for which the dirty bit is going to be set
    :param project_id: project identifier
    :param dirty: the desired value for the dirty bit (defaults to True)
    :returns: the number of records for which the bit was actually set.
    """
    filters = {}
    if resources:
        filters['resource'] = resources
    objs = quota_obj.QuotaUsage.get_objects(context, project_id=project_id,
                                            **filters)
    for obj in objs:
        obj.dirty = dirty
        obj.update()
    return len(objs)


@db_api.retry_if_session_inactive()
@db_api.CONTEXT_WRITER
def set_all_quota_usage_dirty(context, resource, dirty=True):
    """Set the dirty bit on quota usage for all projects.

    :param resource: the resource for which the dirty bit should be set
    :returns: the number of projects for which the dirty bit was
              actually updated
    """
    # TODO(manjeets) consider squashing this method with
    # set_resources_quota_usage_dirty
    objs = quota_obj.QuotaUsage.get_objects(context, resource=resource)
    for obj in objs:
        obj.dirty = dirty
        obj.update()
    return len(objs)


@db_api.retry_if_session_inactive()
def create_reservation(context, project_id, deltas, expiration=None):
    # This method is usually called from within another transaction.
    # Consider using begin_nested
    expiration = expiration or (
        utcnow() + datetime.timedelta(0, RESERVATION_EXPIRATION_TIMEOUT))
    delta_objs = []
    for (resource, delta) in deltas.items():
        delta_objs.append(quota_obj.ResourceDelta(
            context, resource=resource, amount=delta))
    reserv_obj = quota_obj.Reservation(
        context, project_id=project_id, expiration=expiration,
        resource_deltas=delta_objs)
    reserv_obj.create()
    return ReservationInfo(reserv_obj['id'],
                           reserv_obj['project_id'],
                           reserv_obj['expiration'],
                           {delta.resource: delta.amount
                            for delta in reserv_obj.resource_deltas})


@db_api.retry_if_session_inactive()
def get_reservation(context, reservation_id):
    reserv_obj = quota_obj.Reservation.get_object(context, id=reservation_id)
    if not reserv_obj:
        return
    return ReservationInfo(reserv_obj['id'],
                           reserv_obj['project_id'],
                           reserv_obj['expiration'],
                           {delta.resource: delta.amount
                            for delta in reserv_obj.resource_deltas})


@utils.transaction_guard
@utils.skip_exceptions(db_exc.DBError)
@db_api.CONTEXT_WRITER
def remove_reservation(context, reservation_id, set_dirty=False):
    reservation = quota_obj.Reservation.get_object(context, id=reservation_id)
    if not reservation:
        # TODO(salv-orlando): Raise here and then handle the exception?
        return
    tenant_id = reservation.project_id
    resources = [delta.resource for delta in reservation.resource_deltas]
    reservation.delete()
    if set_dirty:
        # quota_usage for all resource involved in this reservation must
        # be marked as dirty
        set_resources_quota_usage_dirty(context, resources, tenant_id)
    return 1


@db_api.retry_if_session_inactive()
@db_api.CONTEXT_READER
def get_reservations_for_resources(context, project_id, resources,
                                   expired=False):
    """Retrieve total amount of reservations for specified resources.

    :param context: Neutron context with db session
    :param project_id: Project identifier
    :param resources: Resources for which reserved amounts should be fetched
    :param expired: False to fetch active reservations, True to fetch expired
                    reservations (defaults to False)
    :returns: a dictionary mapping resources with corresponding deltas
    """
    # NOTE(manjeets) we are using utcnow() here because it
    # can be mocked easily where as datetime is built in type
    # mock.path does not allow mocking built in types.
    return quota_obj.Reservation.get_total_reservations_map(
        context, utcnow(), project_id, resources, expired)


@db_api.CONTEXT_WRITER
def remove_expired_reservations(context, project_id=None, timeout=None):
    expiring_time = utcnow()
    if timeout:
        expiring_time -= datetime.timedelta(seconds=timeout)
    return quota_obj.Reservation.delete_expired(context, expiring_time,
                                                project_id)
