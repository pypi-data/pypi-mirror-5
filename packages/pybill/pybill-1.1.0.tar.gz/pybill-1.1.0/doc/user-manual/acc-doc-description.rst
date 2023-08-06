.. -*- coding: utf-8 -*-

=================================
Describing an accounting document
=================================

**PyBill** uses accounting documents that are described in a specific XML
format, the PBD format. The accounting documents can be of five different types:
bills, claim forms, debits, downpayments, and pro-formas. The following sections
detail how to describe these documents. For a more formal view, you can read the
XML Schema delivered with PyBill. For a more practical view, you can have a look
at the examples delivered with PyBill.

Document structure
==================

This section describe the content of an accounting document in the correct order
(as expected in the XML Schema). However, PyBill works even if some elements 
are not exactly sorted as specified here.

Root element
------------

The root element of an accounting document is an ``accounting-document``
element. This element must have the following attributes:

``format-version``
    Attribute containing the name of the version of the format used in this
    description. Currently, its default value is ``PBD-1.0`` for 
    `PyBill Document 1.0`.

``type`` 
    Attribute giving the type of the accounting document. Must be one of
    ``bill``, ``claim-form``, ``debit``, ``downpayment``, ``pro-forma``.

Here is an example of accounting document root element:

.. sourcecode:: xml

    <accounting-document version="PBD-1.0" type="bill">
        <!-- ... -->
    </accounting-document>

High-level elements
-------------------

Depending on the type of the accounting document, some high-level elements can
or must be defined. These elements bring crucial pieces of information for the
accounting document.

When the accounting document type is ``downpayment``, it is possible to define
the following element:

``downpayment-percent``
    Element containing the percent rate used in a downpayment to compute the
    total that will be paid. This element contains a float between ``0`` and 
    ``100``. By default, a 30% rate is assumed.

Here is an example of the beginning of a downpayment description:

.. sourcecode:: xml

    <accounting-document version="PBD-1.0" type="downpayment">
        <downpayment-percent>40.0</downpayment-percent>
        <!-- ... -->
    </accounting-document>

When the accounting document type is ``pro-forma``, it is mandatory to define
the following element:

``validity-date``
    Element containing the validity date of the offer done with this pro-forma
    document. After this date, the offer is not valid anymore. This element
    contains a string; its content will be displayed in the rendered PDF.

Here is an example of the beginning of a pro-forma description:

.. sourcecode:: xml

    <accounting-document version="PBD-1.0" type="pro-forma">
        <validity-date>april, 10th 2010</validity-date>
        <!-- ... -->
    </accounting-document>

Metadata specification
----------------------

The ``metadata`` element is used to specify the metadata of the accounting
document. Some pieces of this metadata are standard, but it is always possible
to add new pieces of metadata. The following elements can be defined in the
``metadata`` element:

``id`` 
    Element containing the identifier of the accounting document. This element
    is mandatory in the accounting elements whose type is ``bill``,
    ``claim-form``, ``debit``, ``downpayment``. The identifier is actually used
    by the accounting process to uniquely identify each accounting document. No
    mechanism of identifier validation is implemented in PyBill, it is the user
    responsability to define identifiers compatible with his own accounting
    identifiers policy. This element contains a string.

``doc-ref``
    Optional element containing the reference of the accounting document. Please
    note that the document reference is different from the accounting identifier
    (defined in ``id``). One is used by the accounting system, the other is used
    by the document management system. This element contains a string.

``place``
    Optional element containing the place where the document is
    created. This element contains a string.

``date``
    Optional element containing the textual specification of the date when the 
    document is created. This text will be displayed in the generated PDF.
    This element contains a string.

    This element can also have a ``num`` attribute containing the specification
    of the date in ISO format (e.g. ``2010-03-27``). This specification is
    used in the generation of the accounting entries. The ``num`` attribute
    contains a date in the ISO format (``YYYY-MM-DD``).

``info``
    Optional element that can be used to define other pieces of metadata. This
    element has a ``name`` attribute containing the name of the piece of
    metadata and this element contains the value of the piece of metadata. Both
    the element and its ``name`` attribute contain strings.

An example of the ``metadata`` of an accounting document could be:

.. sourcecode:: xml

    <metadata>
        <id>2010-059</id>
        <doc-ref>EX-2010-04-02-ACC-AA-01</doc-ref>
	<place>Paris</place>
	<date num="2010-03-27">March, 27th 2010</date>
        <info name="Purchase number">PURCH-4024</info>
        <info name="Supplier ref">4623579320003</info>
    </metadata>

.. _`sender-receiver-addresses`:

Sender and receiver addresses
-----------------------------

The sender and receiver addresses are specified with an ``address`` element
whose structure is inspired by the DocBook standard. Nevertheless, the sender
address doesn't use as much pieces of information as the receiver address.

Indeed, the sender address is used to identify the person that sends the
document (name, email, phone, etc.) The name of the company or the society
that sends the accounting document is given in the configuration, and the sender
is supposed to be affiliated to this organization. The receiver
address specifies the company or society that is sent the accounting
document and, eventually, the person that should receive the document (this
person being affiliated to the organization).

Each address is described with an ``address`` element. This element has a
``role`` attribute whose value can be ``from`` for a sender address or ``to``
for a receiver address. 

The ``address`` element contains a serie of optional elements to describe the
person name:

``honorific``
    Optional element containing the prefix used before the person name (Mr,
    Miss, Dr, etc.) This element contains a string.

``firstname``
    Optional element containing the first name of the person. This element 
    contains a string.

``othername``
    Optional element containing other pieces of information about the name (when
    specifying the entire name in a single element, it should be in this one). 
    This element contains a string.

``surname``
    Optional element containing the surname of the person. This element 
    contains a string.

``lineage``
    Optional element containing the postfix used after the person name to
    specify its lineage (Jr, Sr, etc.) This element contains a string.

The ``address`` element also contains a serie of optional elements to describe
the postal address:

``street``
    Optional element containing the street field of the postal address (name of
    the street and number in the street). Several elements of this type can
    be used to describe several street lines. This element contains a string.

``pob``
    Optional element containing the post box (only used for post process).
    This element contains a string.

``postcode``
    Optional element containing the post code of the postal address. The post
    code can contain letters and digits. This element contains a string.

``city``
    Optional element containing the city of the postal address. This element 
    contains a string.

``state``
    Optional element containing the state (not useful in all countries). This 
    element contains a string.

``country``
    Optional element containing the country (actually only used for
    international postal sendings). This element contains a string.

The ``address`` element can also specify information on various communication
means with the following optional elements:

``phone``
    Optional element containing a phone number. This element contains a string.

``fax``
    Optional element containing a fax number. This element contains a string.

``web``
    Optional element containing the web address of a site. This element 
    contains a string.

``email``
    Optional element containing an email address. This element contains a 
    string.

Finally, the ``address`` element, when it decribes the address of a person, can
also describes the organization he is affiliated to. For this, a specific
``affiliation`` element is used. This element contains the following elements:

``orgname``
    Optional element containing the name of the organization (company or
    society) the person is affiliated to. This element contains a string.

``orgdiv``
    Optional element containing the name of the division of the organization,
    the person is affiliated to. Several elements of this type can be inserted 
    to specify the sub-division and so on. This element contains a string.

``jobtitle``
    Optional element containing the job title of the person affiliated to the
    organization. Several elements of this type can be inserted. This element 
    contains a string.

``address``
    Optional element containing the address of the organization. This element is
    the same as the ``address`` element described before but it should not
    contain the specification of a person name and an affiliation.

The ``address`` elements can be quite complex, especially when using the
affiliation. In PyBill, we suggest using them in the same way as the following
examples:

.. sourcecode:: xml

    <address role="from">
        <honorific>Mr</honorific>
        <firstname>Jean</firstname>
        <surname>Valjean</surname>
        <email>madeleine@mairie-montreuil-sur-mer.fr</email>
        <phone>+33 2 34 56 78 90</phone>
    </address>
    
    <address role="to">
        <honorific>Mr</honorific>
        <surname>Holmes</surname>
        <email>sherlock@holmes-inquiries.uk</email>
        <affiliation>
            <orgname>Holmes Inquiries</orgname>
            <jobtitle>Chief Detective</jobtitle>
            <address>
                <street>Baker street, 42ndB</street>
                <postcode>65624</postcode>
                <city>LONDON</city>
                <country>UNITED KINGDOM</country>
            </address>
        </affiliation>
    </address>

As you can see, we don't specify any postal address for the sender as the
address will be read in the configuration; we only specify the name and phone or
email that will be displayed somewhere at the top of the document. For the
receiver, we don't directly specify his address but his name and phone or email
(that will be displayed somewhere at the top of the document), and then we
precisely describe his affiliation with the organization name and address (that
is the main information used for the accounting document). 

For the receivers that are not affiliated to an organization, we can of course
direclty describe their address without the ``affiliation`` element, such as in
the following example:

.. sourcecode:: xml

    <address role="to">
        <honorific>Mr</honorific>
        <surname>Holmes</surname>
        <street>Baker street, 42ndB</street>
        <postcode>65624</postcode>
        <city>LONDON</city>
        <country>UNITED KINGDOM</country>
        <email>sherlock@holmes-inquiries.uk</email>
    </address>

Optional text
-------------

Some ``remark`` elements can be inserted to define some paragraphs that will be
displayed at the beginning of the accounting document. These are simple
paragraphs that only contain text (without subelements or specific
rendering). As one would expect, the ``remark`` elements contain strings.

Here is an example:

.. sourcecode:: xml

    <remark>As we agreed, would you please pay this bill before the end of the 
    month.</remark>

Items specification
-------------------

The ``items-list`` element contain several ``item`` subelements that describe
the items concerned by the accounting document. The `Describing the items`_
section will detail how to specify the items and what options are availables.

Other information
-----------------

Finally, depending on the type of the accounting document, some elements can
or must be defined. These elements bring pieces of information that can be
important for the accounting document:

``charged-downpayment``
    Optional element in the documents whose type is ``bill``. This element
    describes a downpayment that was previously charged and whose total will
    be substracted from the total of the current bill. Several elements of this
    kind can be defined if necessary. This element has the following 
    attributes:

    ``id``
        Required attribute containing the identifier of the previously charged
        downpayment. This attribute contains a string.

    ``date``
        Required attribute containing the textual specification of the date of 
        the previously charged downpayment. This attribute contains a string.

    ``total``
        Required attribute containing the total of the previously charged 
        downpayment. This attribute contains a number.

    ``vat``
        Optional attribute containing the VAT amount of the previously charged 
        downpayment. It is only used for the generation of the accounting
        entries. This attribute contains a number.

``issued-debit``
    Optional element in the documents whose type is ``bill``. This element
    describes a debit that was previously emitted and whose total will
    be discarded from the total of the current bill. Several elements of this
    kind can be defined if necessary. This element has the following 
    attributes:

    ``id``
        Required attribute containing the identifier of the previously issued
        debit. This attribute contains a string.

    ``date``
        Required attribute containing the textual specification of the date of 
        the previously issued debit. This attribute contains a string.

    ``total``
        Required attribute containing the total of the previously issued
        debit. This attribute contains a number.

    ``vat``
        Optional attribute containing the VAT amount of the previously issued
        debit. It is only used for the generation of the accounting
        entries. This attribute contains a number.

``payment-terms``
    Required element in the documents whose type is ``bill``, ``downpayment``,
    ``claim-form``. Optional element in the documents whose type is ``debit``.
    Contains the specification of the payment terms (when and how the 
    accounting document must be paid). This information will be added to the
    bank data specified in the configuration. This element contains a string.

Describing the items
====================

Inside the accounting document, the concerned items are described into the
``items-list`` element. This element contains a serie of ``item`` elements, each
one describing an item. When the items are in a bill, they represent the items
that were sold and that are currently billed, when they are in a debit, they
represent the items that were returned and that are now reimbursed, and so on.

The following sections describe how to detail each item.

Description
-----------

The ``desccription`` element is the second child of the ``item`` element and is
mandatory. It contains the description of the item. The description is done in
two subelements:

``title``
    A mandatoty subelement of ``description`` that contains the main description
    of the item. As expected, this element contains a string.

``detail``
    An optional subelement of ``description`` that contains supplementary
    details on the item. Each ``detail`` consist of a single paragraph, but
    several ``detail`` elements can be defined. This element contains a string
    with no formatting marks (only pure text).

Quantity
--------

The ``quantity`` element is the first child of the ``item`` element and is
mandatory. It contains a real number representing the number of the item. The
``quantity`` element can have a ``digits`` attribute containing a positive
integer. This is the number of digits of the quantity that will be displayed in
the final PDF and that will be taken into account in the computations (the
quantity is rounded in order to only have the expected number of digits). By
default, a value of ``0`` is assumed for the number of digits.

Unit price
----------

The ``unit-price`` element is the third child of the ``item`` element and is
mandatory. It contains a real number representing the unit price of the
item. The ``unit-price`` element can have a ``digits`` attribute containing a
positive integer. This is the number of digits of the unit price that will be
dsisplayed in the final PDF and that will be taken into account in the
computations (the unit price is rounded in order to only have the expected
number of digits). By default, a value of ``2`` is assumed for the number of
digits.

VAT rate
--------

The ``vat-rate`` element is the fourth child of the ``item`` element and is
optional. It contains a real number representing the VAT rate that will be
applied to the item. No attribute allows to control the number of digits of the
VAT rate; the rate is always kept with two digits. Please note that we specify
here the rate i.e. ``10`` corresponds to ``10.00%``.

If no VAT is applied to the item (international selling, specific item not
submitted to VAT), then we just don't define a ``vat-rate`` element.

Holdback
--------

Sometimes, the items are submitted to a holdback (the item is entirely billed
but only a part will be paid at the moment, the other part being paid later
after the item has been installed or tested). For these situations, it is
possible to define a holdback rate on each item.

The ``holdback-rate`` attribute can be defined on the ``item`` element. It
contains a real number representing the holdback rate that is applied to the
item. There is no control on the number of digits of this rate; the rate is
always kept with two digits. Please note that we specify here the rate
i.e. ``10`` corresponds to ``10.00%``.

The ``holdback-on-vat`` can also be defined on the ``item`` element. It can have
the ``yes`` or the ``no`` value. When set to ``yes``, the holdback applies to
the Tax Free price and the VAT amount; that's to say the client will firstly not
pay all of the TF price and the VAT amount and will pay the rest later. When set
to ``no``, the holdback only applies to the Tax Free price; that's to say the
client will firstly pay all the VAT amount but not all of the TF price and will
pay the rest of the TF price later. By default, a ``no`` value is assumed for
this attribute.

Let's consider a little example. The client has bought one item whose unit
price in 100.00. This item is submitted to a 20.0% rate. It is also submitted to
a 10% holdback rate. The bill has a Tax Free total of 100.00 and an Including
Taxes  total of 120.00. As we have a holdback on the item, the client will hold
back 10% of the TF price of the item and pay it later. So, he will hold back
10.00 and will firstly pay 110.00 (90.00~+ 20.00 of VAT) and later the 10.00 of
the holdback.

In this example, if the holdback is also on VAT, the bill will still have a Tax
Free total of 100.00 and an Including Taxes total of 120.00. But now, the client
will hold back 10% of the IT price of the item and pay it later. So, he will
holdback 12.00 and will firstly pay 108.00 (90.00~+ 18.00 of VAT) and later
the 12.00 of the holdback (10.00~+ 2.00 of VAT).

Some examples
-------------

Here is an example of a unique item with a 19.60 VAT rate:

.. sourcecode:: xml

    <items-list>
        <item>
            <quantity>1</quantity>
            <description>
                <title>Python book</title>
                <detail>Hard cover</detail>
            </description>
            <unit-price>15.60</unit-price>
            <vat-rate>19.60</vat-rate>
        </item>
    </items-list>

The following example is a bit more complex and has controls of the number of
digits used for the computations and for the PDF display:

.. sourcecode:: xml

    <items-list>
        <item>
            <quantity digits="3">1.234</quantity>
            <description>
                <title>Potatoes</title>
                <detail>weight expressed in kilograms</detail>
            </description>
            <unit-price digits="4">0.9987</unit-price>
            <vat-rate>19.60</vat-rate>
        </item>
    </items-list>

Please note that the specified number of digits can be inferior to the actual
number of digits of the number written in the XML. In this case, the number will
be rounded to have the specified number of digits.

Finally, this example shows the definition of two items, one with a holdback on
TF price only and the other with a holdback on the IT price:

.. sourcecode:: xml

    <items-list>
        <item holdback-rate="15.0">
            <quantity>1</quantity>
            <description>
                <title>Refrigerator</title>
                <detail>An holdback will be held until the product is 
                installed</detail>
            </description>
            <unit-price>399.00</unit-price>
            <vat-rate>19.60</vat-rate>
        </item>
        <item holdback-rate="15.0" holdback-on-vat="yes">
            <quantity>1</quantity>
            <description>
                <title>Electrical oven</title>
                <detail>An holdback will be held until the product is 
                installed</detail>
            </description>
            <unit-price>549.00</unit-price>
            <vat-rate>19.60</vat-rate>
        </item>
    </items-list>


Choosing a configuration
========================

When PyBill transforms an accounting document into a PDF, various pieces of
information are necessary (address of the company emitting the document, path to
the logo of the company, data of the company bank, several localized terms,
etc.) These pieces of information are specified in a configuration file (see
:ref:`config-specification` section for more details).

The configuration file can be specified in two ways:

- either on the command-line with a dedicated option,

- or into a processing instruction in the XML accounting document.

on the command line
-------------------

When running PyBill on the command-line, the ``-c`` or ``--config`` option can
be used to give the path to the XML file that contains the configuration to be
used for transforming the accounting documents into PDF. This configuration will
override any configuration specified in the accounting documents. Please note
that the same configuration will be applied to all the documents processed
during the command line run.

The :ref:`command-line-run` section details the options of the command line.

in the accounting document
--------------------------

Thanks to a dedicated processing instruction, it is possible to specify, in each
accounting document, the configuration that must be used to transform this
document into PDF. Therefore, the accounting documents can be associated to
different configurations, and they will be easily transformed in PDF with a
simple run of PyBill (without specifying the configuration on the command line).

The ``pybill`` processing instruction can be defined at the beginning of an XML
accounting document (in PBD-1.0 format). This processing instruction contains 
the following fields:

``config``
    Name of the configuration associated with the accounting document.

From the `name` of the configuration, a file name is built by adding the `.xml`
extension. A file with this name is then searched in the user PyBill
configuration directory and then in the system configuration directory. If the
configuration file is not found, PyBill doesn't crash but uses its default
configuration. The user configuration directory is, on the Unix-like platforms,
the ``$HOME/.config/pybill`` directory. The system configuration directory is,
on the Unix-like platforms, the ``/etc/pybill/config`` directory.

The user can thus define his own configuration files and store them in his
configuration directory. He can also override an existing system configuration
by adding a configuration file with the same name in his directory.

Here is an example of the specification of a configuration in an accounting
document:

.. sourcecode:: xml

    <?xml version="1.0" encoding="UTF-8"?>

    <?pybill config="my-company"?>

    <accounting-document version="PBD-1.0" type="bill">
        <!-- ... --->        
    </accounting-document>

In this example, PyBill searches in ``~/.config/pybill/`` directory, a file
named ``my-company.xml``. If this file is not found, it searches it in
``/etc/pybill/config/`` directory. If it is not found, PyBill uses its default
configuration saved in ``/etc/pybill/config/default.xml``.

.. _accounting-info-in-accdocs:

Specifying accounting information
=================================

PyBill has the ability to generate the accounting entries corresponding to the
processed accounting documents. These entries are saved in the `pycompta`_
format into an XML file. The :ref:`acc-entries-generation`  section details
the entries generation.

.. _`pycompta`: http://www.logilab.org/Project/pycompta

In each accounting document, the user can specify the numbers of the accounts
that will be used in the entries generation. These accounts are a client
account, a client account for the holdback, a product account and a VAT
account. A dedicated processing instruction can be used for this specification.

The ``accounts`` processing instruction can be inserted at the beginning of an
accounting document in the PBD-1.0 XML format. It contains four fields:

``client`` 
    Number of the account used for the client

``client-holdback``
    Number of the account used for the client holdbacks. Can be the same as
    previous account.

``product``
    Number of the product account. Only one product account is used for all the
    items in the document.

``vat``
   Number of the VAT account.

Here is an example of a specification of the accounts with the processing
instruction:

.. sourcecode:: xml

    <?xml version="1.0" encoding="UTF-8"?>

    <?pybill config="my-company"?>
    <?accounts client="411001" client-holdback="411001" 
               product="70501" vat="44571"?>

    <accounting-document version="PBD-1.0" type="bill">
        <!-- ... --->        
    </accounting-document>

You can see in this example that we use both processing instructions, one for
the association to the configuration and the other one for the specification of
the accounts impacted by the document.
