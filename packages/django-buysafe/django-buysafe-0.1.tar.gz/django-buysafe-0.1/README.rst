=====
Buysafe
=====

Buysafe bundles SunTech BuySafe (TM) posting and receiving routines into Django forms and views, and provides an admin view for payment method management.

Dependency
-----------

If you want to use the default product info handler, you need to use Cartridge as your ecommerce backend. If you provide your own info handler, all you need is Django.

Quick start
-----------

1. Add :code:`buysafe` to your :code:`INSTALLED_APPS` setting:

::

    INSTALLED_APPS = (
        ...
        'buysafe',
        ...
    )

2. If you don't use Cartridge, add :code:`BUYSAFE_FORM_VALUES_GENERATOR` in your settings to specify a custom handler. The handler should accept :code:`**kwargs`, which contains values in the :code:`request.POST` dictionary.

3. Run :code:`python manage.py migrate buysafe`.

4. Go to your admin and add some payment methods.

5. To pay for an order, use POST to submit a form to view:code:`buysafe_start` with the values to pass to the product info handler. The default handler needs an :code:`order_id` field. This brings up a view to initiate the payment process.

6. Profit!
