===============================
Yo Payments
===============================

.. image:: https://badge.fury.io/py/yo_payments.png
    :target: http://badge.fury.io/py/yo_payments

.. image:: https://pypip.in/d/yo_payments/badge.png
	:target: https://crate.io/packages/yo_payments?version=latest


Api Wrapper for the Yo Payments service

* Free software: BSD license
* Documentation: http://yo_payments.rtfd.org.

Usage
_____

        from yo_payments.yo_payments import Yo

        api_request = Yo("username","password","method","api_url")
        result = api_request.make_request()

Features
--------

* Easy Access to the Yo Payments API
