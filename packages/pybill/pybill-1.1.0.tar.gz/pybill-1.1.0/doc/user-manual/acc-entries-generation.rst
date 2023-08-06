.. -*- coding: utf-8 -*-

.. _acc-entries-generation:

=================================
Generating the accounting entries
=================================

**PyBill** has the ability to generate accounting entries for the accounting
documents it processes. These entries are in the XML format used by
`pycompta`_ tool, and will be saved in an XML file specified when running
PyBill (by default, ``entries.xml``). The following sections describe how to
correctly generate the accounting entries, including how to specify the account
numbers impacted by each document.

.. _`pycompta`: http://www.logilab.org/Project/pycompta

General view
============

In order to generate accounting entries with PyBill, two main things must be
done:

#. specify the impacted accounts in each accounting document,

#. call PyBill with the correct options to generate the entries.

Specifying the impacted accounts
================================

In each XML file defining an accounting document, it is possible to insert a
dedicated processing instruction to specify the accounts that are impacted by
the document. These accounts are the client account that will be, for example,
debited when sending a bill; the product account that will be, for example,
credited when sending a bill; the VAT account that will be, for example,
credited when sending a bill. A supplementary client account for the holdbacks
can be specified; it will only be used if there are some holdbacks in the
document.

For each accounting document, PyBill produces an accounting entry that transfers
money from some accounts to other accounts. The way these transferts are done
depends on the document type and is dictated by the rules of accountings.

The :ref:`accounting-info-in-accdocs` section details how to specify the number
of the impacted accounts in one accounting document.

Generating accounting entries with PyBill
=========================================

Two command-line options are used to control the generation of the accounting
entries. Each call of PyBill generates the accounting entries for all the
accounting documents that are processed during this call. The accounting entries
are saved in a single XML file.

By default, PyBill generates the accounting entries. However the ``-n`` or
``--no-entries`` command-line option can be used to disable this generation. By
default, PyBill generates the entries in the ``entries.xml`` file stored in
current directory. This can be changed thanks to the ``-e`` or
``--entries-file`` command-line option that specifies the name of the file
containing the accounting entries.

Example
=======

Suppose, we have the following simple bill:

.. sourcecode:: xml

    <?xml version="1.0" encoding="UTF-8"?>

    <?pybill config="my-company"?>
    <?accounts client="411001" client-holdback="411001" 
               product="70501" vat="44571"?>

    <accounting-document version="PBD-1.0" type="bill">
        <metadata>
            <id>2010-059</id>
            <place>Paris</place>
            <date num="2010-04-14">April, 14th 2010</date>
        </metadata>

        <address role="to">
            <affiliation>
                <orgname>A Company</orgname>
                <address>
                    <street>Main street, 15th</street>
                    <postcode>12345</postcode>
                    <city>GLISBOW</city>
                </address>
            </affiliation>
        </address>

        <items-list>
            <item>
                <quantity>3</quantity>
                <description>
                    <title>Something valuable</title>
                </description>
                <unit-price>10.00</unit-price>
                <vat-rate>19.60</vat-rate>
            </item>
            <item>
                <quantity>1</quantity>
                <description>
                    <title>Another thing very valuable</title>
                </description>
                <unit-price>100.00</unit-price>
                <vat-rate>19.60</vat-rate>
            </item>
        </items-list>

        <payment-terms>End of the month</payment-terms>

    </accounting-document>

The bill has a tax-free total of ``130.00`` and an including-taxes total of 
155.48. The generated file containing the accounting entries will be:

.. sourcecode:: xml

    <ecritures>
        <ecriture date='2010-04-14'>
            <libelle>Bill #2010-059</libelle>
            <debit compte='4110O1' montant='155.48'/>
            <credit compte='70501' montant='130.00'/>
            <credit compte='44571' montant='25.28'/>
        </ecriture>
    </ecritures>

This file contains only one accounting entry as there was only one accounting
document processed by PyBill.
