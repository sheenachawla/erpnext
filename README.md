# ERPNext - Open Source ERP for small, medium sized businesses

[https://erpnext.com](https://erpnext.com)

ERPNext is a web based ERP that includes Accounting, Inventory, CRM, Sales, Purchase, Projects, HRMS. 

Database supported is MySQL. Server-side application written in Python and based on
[wnframework](https://github.com/webnotes/wnframework).

ERPNext is under active development so if you are using it and updating regularly,
you might have to hit our forms.

Easiest way to use ERPNext is to use our [hosted service](https://erpnext.com), it 
also pays for the development, or download a [virtual image](https://erpnext.com/download-erpnext.html). If you want to set it up yourself,
please read the instructions carefully.

## Platform

ERPNext is built on  (Version 2.0)

## User Guide

[See wiki](https://github.com/webnotes/erpnext/wiki/User-Guide)

## Download and Install

First install all the pre-requisites, then

    $ git clone git://github.com/webnotes/erpnext.git
    $ cd erpnext
    $ python erpnext_install.py
    
[See installation notes](https://github.com/webnotes/erpnext/wiki/How-to-Install-ERPNext)

## Patch and update

To patch and update from the latest git repository the erpnext folder and run.
You will have to set your origin in git remote

    $ lib/wnf.py --update origin master

## Forums

Please join our forums for more questions:

- [Developer Forum](http://groups.google.com/group/erpnext-developer-forum)
- [User Forum](http://groups.google.com/group/erpnext-user-forum)

## License

GNU/General Public License (see licence.txt)

**Note:** The name "ERPNext" must be retained in all derivatives.