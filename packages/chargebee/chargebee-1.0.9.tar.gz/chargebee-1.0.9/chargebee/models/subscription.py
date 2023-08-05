import json
from chargebee.model import Model
from chargebee import request
from chargebee import APIError

class Subscription(Model):
    class Addon(Model):
      fields = ["id", "quantity"]
      pass
    class Coupon(Model):
      fields = ["coupon_id", "apply_till", "applied_count"]
      pass

    fields = ["id", "plan_id", "plan_quantity", "status", "trial_start", "trial_end", "current_term_start", \
    "current_term_end", "remaining_billing_cycles", "created_at", "activated_at", "cancelled_at", \
    "cancel_reason", "due_invoices_count", "due_since", "total_dues", "addons", "coupon", "coupons" ]


    @staticmethod
    def create(params, env=None):
        return request.send('post', '/subscriptions', params, env)

    @staticmethod
    def list(params=None, env=None):
        return request.send('get', '/subscriptions', params, env)

    @staticmethod
    def retrieve(id, env=None):
        return request.send('get', '/subscriptions/%s' % id, None, env)

    @staticmethod
    def update(id, params=None, env=None):
        return request.send('post', '/subscriptions/%s' % id, params, env)

    @staticmethod
    def cancel(id, params=None, env=None):
        return request.send('post', '/subscriptions/%s/cancel' % id, params, env)

    @staticmethod
    def reactivate(id, params=None, env=None):
        return request.send('post', '/subscriptions/%s/reactivate' % id, params, env)
