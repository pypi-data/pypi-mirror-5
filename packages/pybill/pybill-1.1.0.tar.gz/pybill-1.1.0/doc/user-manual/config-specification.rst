.. -*- coding: utf-8 -*-

.. _config-specification:

==========================
Specifying a configuration
==========================

**PyBill** uses a configuration to customize the rendering of the PDF documents
generated from the XML accounting documents in PBD format. This configuration
can specify:

- the emitter data: name, logo, address,

- the emitter bank data: name, account number,

- the footer to be written below the PDF documents,

- the separators used in number rendering,

- the agreement text that will be written on the pro-forma documents,

- the localization of the terms used by PyBill in the PDF generation.

The following sections detail how to specify these items. For a more formal
view, you can read the XML Schema delivered with PyBill. For a more practical
view, you can have a look at the examples delivered with PyBill.

Root element
============

The root element of a PyBill configuration is a ``config`` element. This 
element must have the following attributes:

``format-version``
    Attribute containing the name of the version of the format used for the
    configuration specification. Currently, its only possible value is 
    ``PBD-1.0`` for `PyBill Document 1.0`.

``name``
    Attribute containing the name of the configuration. This name is not used in
    the PDF generation but is useful to discriminate one configuration from
    another.

The root element contains the following elements, that are all mandatory:

``company``
    Element containing data about the company that emits the accounting
    documents (logo, address, etc.). See :ref:`company-data` section.

``bank-data``
    Element containing data about the bank of the company that emits the 
    accounting documents (name, bank account, etc.). See :ref:`bank-data` 
    section.

``agreement-intro``
    Element containing the lines that are written on a pro-forma and that
    usually ask for a signature from the client as an agreement. See 
    :ref:`agreement-lines` section.

``footer``
    Element containing the lines that are written in the footer of all the
    PDFs generated from the accounting documents. See 
    :ref:`footer-lines` section.

``number-separators``
    Element containing the separators used to nicely write the numbers in the
    PDFs. See :ref:`number-separators` section.

``localisation``
    Element containing the localisation of the terms used by PyBill for the 
    PDF generation. See :ref:`localized-terms` section

.. _`company-data`:

Specifying the emitter data
===========================

The ``company`` element is used to specify the data relative to the company or
society that emits the accounting documents. It has the following child
elements:

``logo-file``
    Optional element containing the relative path to the image file containing
    the logo of the company. This element contains a string.

``orgname``
    Mandatory element containing the name of the organization (company or
    society) that emits the accounting documents.

``address``
    Optional element describing the address of the company. The structure of
    this element is inspired by the DocBook standard and is similar to the one
    described for the accounting documents (see 
    :ref:`sender-receiver-addresses` section). This element can have the
    following subelements:

    ``street``
        Optional element containing a string that describes one line of the
        street specification. Several elements of this type can be defined.

    ``pob``
        Optional element containing a string that describes the post box.

    ``postcode``
        Optional element containing a string that describes the post code (for
        post process).

    ``city``
        Optional element containing a string that describes the city.

    ``state``
        Optional element containing a string that describes the state (not
        useful in all countries).

    ``country``
        Optional element containing a string that describes the country.

    ``phone``
        Optional element containing a string that describes the phone number.

    ``fax``
        Optional element containing a string that describes the fax number.

    ``web``
        Optional element containing a string that describes the web site 
        address.

    ``email``
        Optional element containing a string that describes the email address.

The name of the emitter and its address will be displayed at the top of the 
accounting documents.

Here is an example of a specification of emitter data:

.. sourcecode:: xml

    <company>
        <logo-name>./my-logo.png</logo-name>
        <orgname>My Company</orgname>
        <address>
            <street>3rd floor</street>
            <street>Center Avenue, 124</street>
            <postcode>3456</postcode>
            <city>GLISBOW</city>
        </address>
    </company>

.. _`bank-data`:

Specifying the bank data
========================

The ``bank-data`` element is used to specify the data relative to the bank of
the company or society that emits the accounting documents. It has the 
following child elements:

``line``
    Element containing a string that describes one line of the bank
    data. Hence, the bank data is divided in several lines (e.g. paragraphs)
    that will be written at the end of the accounting documents the client must
    pay (bills, claim forms, downpayments). There can be zero or several
    ``line`` elements in the ``bank-data`` element.

Here is an example of a specification of the bank data:

.. sourcecode:: xml

    <bank-data>
        <line>Golden Squirrel Bank</line>
        <line>IBAN: FR01 2345 6789 0123 4567 8901 234</line>
    </bank-data>

.. _`agreement-lines`:

Specifying the agreement introduction
=====================================

The ``agreement-intro`` element is used to specify the text that will be
inserted on the pro-formas and that usually asks the client to sign the
document. It has the following child elements:

``line``
    Element containing a string that describes one line of the agreement
    introducion. Hence, this text is divided in several lines (e.g. paragraphs)
    that will be written at the end of the pro-formas documents. There can be 
    zero or several ``line`` elements in the ``agreement-intro`` element.

Here is an example of a definition of the agreement introduction text:

.. sourcecode:: xml

    <agreement-intro>
        <line>Please sign here to confirm the command</line>
    </agreement-intro>

.. _`footer-lines`:

Specifying the footer
=====================

The ``footer`` element is used to specify the text that will be written in the
footer of all the accounting documents. It has the following child elements:

``line``
    Element containing a string that describes one line of the footer. There 
    can be zero or several ``line`` elements in the ``footer`` element. Please 
    be aware that writting too much lines in the footer will give ugly results.
    The ``line`` element contains only text without any formatting marks. It
    cannot contain images or tables.

Here is an example of a definition of the footer:

.. sourcecode:: xml

    <footer>
        <line>My Company - GLISBOW</line>
    </footer>

.. _`number-separators`:

Specifying the number separators
================================

The ``number-separators`` element specifies the various separators used to
nicely write the numbers in the PDFs generated from the accounting documents. It
has three child elements corresponding to the various separators:

``sign`` 
    Element containing the separator inserted between the sign and the
    number. It contains a string (usually a single character) and is
    optional. If not specified, the default value for this separator is used
    (empty value).

``thousands`` 
    Element containing the separator inserted between the thousands digit and 
    the hundreds digit, the millions digit and the hundreds of thousand digit,
    and so on. It contains a string (usually a single character) and is
    optional. If not specified, the default value for this separator is used
    (empty value).

``digits`` 
    Element containing the separator inserted between the integer and the
    digits. It contains a string (usually a single character) and is
    optional. If not specified, the default value for this separator is used
    (``.``).

Here is an example of the definition of the number separators for the
traditional English rendering:

.. sourcecode:: xml

    <number-separators>
        <sign>&#xA0;</sign> <!-- non blank space -->
        <thousands>,</thousands>
        <digits>.</digits>
    </number-separators>

.. _`localized-terms`:

Localizing the terms
====================

The ``localisation`` element defines the localisation of the terms that are used
by PyBill to write text in the PDFs generated from the accounting
documents. Each child element is one of these terms. In order to have a correct
generation of the PDFs, all the terms must be defined (that's why all the
following elements are mandatory).

``colon``
    Colon that will be inserted after a keyword and before its value. In
    English, it is just ``:`` but in some langages it can be preceded by a
    non-blank space.

``phone-kw``
    Name of the keyword preceding the phone numbers, for example `Phone`.

``fax-kw``
    Name of the keyword preceding the fax numbers, for example `Fax`.

``web-kw``
    Name of the keyword preceding the web site addresses, for example `Web`.

``email-kw``
    Name of the keyword preceding the email addresses, for example `Email`.

``doc-ref-kw``
    Name of the keyword preceding the document reference, for example 
    `Our ref` or `Ref`.

``receiver-kw``
    Name of the keyword preceding the name of the person the document is
    specifically sent to, for example `c/o`

``sender-kw``
    Name of the keyword preceding the name of the person that sends the
    document, for example `from`.

``on-date``
    Introductory phrase preceding the date, for example `on`, as in
    `Paris, on April 14th`.

``bill``
    Name designating a bill, typically `Bill`.

``claim-form``
    Name designating a claim form, typically `Claim Form`.

``downpayment``
    Name designating a downpayment, typically `Downpayment`.

``debit``
    Name designating a debit, typically `Debit`.

``pro-forma``
    Name designating a pro-forma, typically `Pro-Forma`.

``number``
    Introductory phrase or symbol preceding the identifier or number of an
    accounting document, for example `#`.

``dated``
    Introductory phrase written before the date of a document, for example 
    `dated on`.

``valid-until``
    Introductory phrase written before the expiration date of a pro-forma, for
    example `valid until`.

``intro-detail``
    Text that is written at the beginning of all the accounting document, for
    example `All the amounts are written in Euros`.

``quantity``
    Name of the keyword designating the quantity of an item, for example `Qty`.

``description``
    Name of the keyword designating the description of an item, for example 
    `Desc`.

``vat-rate``
    Name of the keyword designating the VAT rate of an item, for example 
    `VAT rate`.

``unit-price``
    Name of the keyword designating the unit price of an item, for example 
    `Unit Price`.

``tf-unit-price``
    Name of the keyword designating the tax-free unit price of an item, for 
    example `TF Unit Price`.

``price``
    Name of the keyword designating the price, for example `Price`.

``tf-price``
    Name of the keyword designating the tax-free price, for example `TF Price`.

``it-price``
    Name of the keyword designating the including-taxes price, for example
    `IT Price`.

``holdback-on``
    Phrase representing the `holdback on` expression, typically `Holdback on`.

``ita-est``
    Phrase representing the `ita est` expression, for example `i.e.` or 
    `that is`.

``total``
    Name of the keyword designating the total, for example `Total`.

``tf-total``
    Name of the keyword designating the tax-free total, for example `TF Total`.

``vat-amount``
    Name of the keyword designating a VAT amount, for example `VAT Amount`.

``it-total``
    Name of the keyword designating the including-taxes total, for example 
    `IT Total`.

``including``
    Phrase representing the `including` expression, typically `including`.

``holdback``
    Name designating a holdback, typically `Holdback`.

``on-tf``
    Expression designating an holdback that concerns TF amounts, typically 
    `on TF amounts`.

``on-vat``
    Expression designating an holdback that concerns VAT amounts, typically 
    `on VAT amounts`.

``debit-total``
    Name of the keyword designating the total of a debit, for example 
    `Debit Total`.

``charged-downpayment``
    Name designating a previously charged downpayment, typically `Downpayment`.

``charged-on``
    Expression introducing the date when a previous downpayment was charged,
    for example `charged on`.

``issued-debit``
    Name designating a previously issued debit, typically `Debit`.

``issued-on``
    Expression introducing the date when a previous debit was issued,
    for example `issued on`.

``to-be-paid``
    Name of the keyword designating the total to be paid, for example 
    `To be paid`.

``payment-terms``
    Name of the keyword designating the payment terms (for the bills, the claim
    forms and the downpayments), typically `Payment Terms`.

``to-bring-forward``
    Name of the keyword designating the amount to be brought forward (when 
    having multiple pages), for example `To bring fwd`.

``carry-forward``
    Name of the keyword designating the carry forward (when having multiple 
    pages), for example `Carry fwd`.

The following terms are only used for compatibility with older formats (`PyBill
0.X`). Nevertheless, they should also be defined:

``your-ref-kw``
    Name of the keyword designating the reference given by the receiver to the
    current exchange, for example `Your ref.`.

``purch-ref-kw``
    Name of the keyword designating the reference of the purchase, for example 
    `Purch.`.

``supplier-ref-kw``
    Name of the keyword designating the reference given by the receiver to the
    sender as one of his suppliers, for example  `Suppl.`.
