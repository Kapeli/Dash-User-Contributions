#!/usr/bin/python -S
# -*- coding: utf-8 -*-

import sys

sys.setdefaultencoding("utf-8")

import site

import os, re, sqlite3, urllib, codecs
from bs4 import BeautifulSoup, NavigableString, Tag 

db = sqlite3.connect('OpenEdge.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

docpath = 'OpenEdge.docset/Contents/Resources/Documents'

files = []
for name in os.listdir(docpath):
    if os.path.isfile(os.path.join(docpath,name)):
        files.append(name)
        
for file in files:

   soup = BeautifulSoup(open(os.path.join(docpath,file)))

   any = re.compile('.*')
    
   for tag in soup.find_all('a', {'href':any}):
       name = tag.text.strip()
       path = tag.attrs['href'].strip()
    
       if len(name) == 0:
           name = path
        
       if path.split('#')[0] not in ('index.html'):
           path = urllib.unquote(path)
           path = path.encode('ascii', 'ignore')
           cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Guide', path))
           print 'adding file path: %s, name: %s' % (path, name)

   db.commit()

from findtools.find_files import (find_files, Match)

sh_files_pattern = Match(filetype='f', name='*.html')
found_files = find_files(path=docpath, match=sh_files_pattern)

for found_file in found_files:

    if path.split('#')[0] not in ('index.html'):

        print 'editing file: %s' % (found_file)
    
        # Remove the onload attribute from the body tag
        # <body id="pYxQs0eniL26fH5dRGlU43A" class="ww_skin_page_body" onload="Page.OnLoad('../index.html#page/dvref/xml.html');">

        soup = BeautifulSoup(open(found_file))

        any = re.compile('.*')
    
        for tag in soup.find_all('body'):
        
            tag = soup.body

            del tag['onload']
            tag

        html = str(soup)
        
        new_file = found_file.encode('ascii', 'ignore')
        
        with open((found_file),"wb") as file:
            file.write(html)
            
        if new_file <> found_file:
            with open((new_file),"wb") as file:
                file.write(html)


# Special Types

# Annotation Attribute Binding Builtin Callback Category Class Command Component Constant Constructor Define Delegate Diagram Directive Element Entry Enum Environment Error Event Exception Extension Field File Filter Framework Function Global Guide Hook Instance Instruction Interface Keyword Library Literal Macro Method Mixin Modifier Module Namespace Notation Object Operator Option Package Parameter Plugin Procedure Property Protocol Provider Provisioner Query Record Resource Sample Section Service Setting Shortcut Statement Struct Style Subroutine Tag Test Trait Type Union Value Variable Word

# Command
cur.execute('UPDATE searchIndex SET type = "Command" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%command" or name like "%commands")')
cur.execute('UPDATE searchIndex SET type = "Command" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%utility" or name like "%qualifier")')

# Parameter
cur.execute('UPDATE searchIndex SET type = "Parameter" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%parameter" or name like "%parameters")')
cur.execute('UPDATE searchIndex SET type = "Parameter" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "% (-%)")')

# Attribute
cur.execute('UPDATE searchIndex SET type = "Attribute" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%attribute" or name like "%attributes")')

# Class
cur.execute('UPDATE searchIndex SET type = "Class" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%class" or name like "%classes")')

# Event
cur.execute('UPDATE searchIndex SET type = "Event" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%event" or name like "%events")')

# Function
cur.execute('UPDATE searchIndex SET type = "Function" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%function" or name like "%functions")')

# Interface
cur.execute('UPDATE searchIndex SET type = "Interface" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%interface")')

# Method
cur.execute('UPDATE searchIndex SET type = "Method" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%method" or name like "%methods")')

# Object
cur.execute('UPDATE searchIndex SET type = "Object" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%object" or name like "%object")')

# Procedure
cur.execute('UPDATE searchIndex SET type = "Procedure" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%procedure" or name like "%procedures")')

# Query
cur.execute('UPDATE searchIndex SET type = "Query" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%query" or name like "%queries")')

# Statement
cur.execute('UPDATE searchIndex SET type = "Statement" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%statement" or name like "%statements")')

# Type
cur.execute('UPDATE searchIndex SET type = "Type" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%type" or name like "%types")')

# Operator
cur.execute('UPDATE searchIndex SET type = "Operator" WHERE type = "Guide" and (path like "dpspr/%" or path like "dvref/%") and (name like "%operator" or name like "%preprocessor directive" or name like "%preprocessor directives" or name like "%punctuation" or name like "%special character" or name like "%expression precedence" or name like "%array reference" or name like "%character-string literal" or name like "%preprocessor name reference")')

# Rename all topic titles to include the section at the end            

# OpenEdge Application Server
cur.execute('UPDATE searchIndex SET name = name || " : Administration : OpenEdge Application Server" WHERE path like "asadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Developing AppServer Applications : OpenEdge Application Server" WHERE path like "asaps/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Developing WebSpeed Applications : OpenEdge Application Server" WHERE path like "aswsp/%"')

# Business Process Server/Manager
cur.execute('UPDATE searchIndex SET name = name || " : Application Developers Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-appdev/%"')
cur.execute('UPDATE searchIndex SET name = name || " : BP Server Developers Guide: Progress OpenEdge Business Process Server" WHERE path like "bpm-bpserver/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Clustering Guide : Progress OpenEdge BPM BusinessManager" WHERE path like "bpm-cluster/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Customization Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-custom/%"')
cur.execute('UPDATE searchIndex SET name = name || " : BPM Events Users Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-events/%"')
cur.execute('UPDATE searchIndex SET name = name || " : First Steps Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-first/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Managed Adapters Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-manadapter/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Migrating to OpenEdge Business Process Management 11.5 : OpenEdge" WHERE path like "bpm-migrate/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Users Guide : Progress OpenEdge Business Process Modeler" WHERE path like "bpm-modeler-user/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Business Process Portal Administrators Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-portal-admin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Business Process Portal Managers Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-portal-manage/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Business Process Portal Users Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-portal-user/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Server Administrators Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-serveradmin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Developing BPM Applications with Developer Studio : OpenEdge Getting Started" WHERE path like "bpm-studio-ug/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Terminology Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-term/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Troubleshooting Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-trouble/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Web Services Developers Guide : Progress OpenEdge Business Process Server" WHERE path like "bpm-web/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Business Rules : Progress Developer Studio for OpenEdge" WHERE path like "busrules/%"')

# Copyright
cur.execute('UPDATE searchIndex SET name = name || " : Copyright" WHERE path like "copyright/%"')

# OpenEdge Data Management
cur.execute('UPDATE searchIndex SET name = name || " : Database Administration : OpenEdge Data Management" WHERE path like "dmadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : DataServer for ODBC : OpenEdge Data Management" WHERE path like "dmodb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : DataServer for Oracle : OpenEdge Data Management" WHERE path like "dmora/%"')
cur.execute('UPDATE searchIndex SET name = name || " : SQL Development : OpenEdge Data Management" WHERE path like "dmsdv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : DataServer for Microsoft SQL Server : OpenEdge Data Management" WHERE path like "dmsql/%"')
cur.execute('UPDATE searchIndex SET name = name || " : SQL Reference : OpenEdge Data Management" WHERE path like "dmsrf/%"')

# OpenEdge Deployment
cur.execute('UPDATE searchIndex SET name = name || " : Managing ABL Applications : OpenEdge Deployment" WHERE path like "dpabl/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Startup Command and Parameter Reference : OpenEdge Deployment" WHERE path like "dpspr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : WebClient Applications : OpenEdge Deployment" WHERE path like "dpweb/%"')

# OpenEdge Development
cur.execute('UPDATE searchIndex SET name = name || " : ADM Reference : OpenEdge Development" WHERE path like "dvadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : AppBuilder : OpenEdge Development" WHERE path like "dvapb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Debugging and Troubleshooting : OpenEdge Development" WHERE path like "dvdbg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Basic Database Tools : OpenEdge Development" WHERE path like "dvdbt/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Basic Development Tools : OpenEdge Development" WHERE path like "dvdvt/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Error Handling : OpenEdge Development" WHERE path like "dverr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Messaging and ESB : OpenEdge Development" WHERE path like "dvesb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Internationalizing Applications : OpenEdge Development" WHERE path like "dvint/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Java Open Clients : OpenEdge Development" WHERE path like "dvjav/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Working with JSON : OpenEdge Development" WHERE path like "dvjsn/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Mobile Applications : OpenEdge Development" WHERE path like "dvmad/%"')
cur.execute('UPDATE searchIndex SET name = name || " : .NET Open Clients : OpenEdge Development" WHERE path like "dvnet/%"')
cur.execute('UPDATE searchIndex SET name = name || " : GUI for .NET Mapping Reference : OpenEdge Development" WHERE path like "dvngm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : GUI for .NET Programming : OpenEdge Development" WHERE path like "dvngp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : ADM and SmartObjects : OpenEdge Development" WHERE path like "dvobj/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Open Client Introduction and Programming : OpenEdge Development" WHERE path like "dvoci/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Object-oriented Programming : OpenEdge Development" WHERE path like "dvoop/%"')
cur.execute('UPDATE searchIndex SET name = name || " : ProDataSets : OpenEdge Development" WHERE path like "dvpds/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Programming Interfaces : OpenEdge Development" WHERE path like "dvpin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : ABL Reference : OpenEdge Development" WHERE path like "dvref/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Translation Manager : OpenEdge Development" WHERE path like "dvtmg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Visual Translator : OpenEdge Development" WHERE path like "dvvis/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Web Services : OpenEdge Development" WHERE path like "dvwsv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Working with XML : OpenEdge Development" WHERE path like "dvxml/%"')

# OpenEdge Replication
cur.execute('UPDATE searchIndex SET name = name || " : User Guide : OpenEdge Replication" WHERE path like "ffr/%"')

# OpenEdge Getting Started
cur.execute('UPDATE searchIndex SET name = name || " : ABL Essentials : OpenEdge Getting Started" WHERE path like "gsabl/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Application and Integration Services : OpenEdge Getting Started" WHERE path like "gsais/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Core Business Services - Security and Auditing : OpenEdge Getting Started" WHERE path like "gscsv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Database Essentials : OpenEdge Getting Started" WHERE path like "gsdbe/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Guide for New Developers : OpenEdge Getting Started" WHERE path like "gsdev/%"')
cur.execute('UPDATE searchIndex SET name = name || " : GUI for .NET Primer : OpenEdge Getting Started" WHERE path like "gsgnp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Identity Management : OpenEdge Getting Started" WHERE path like "gsidm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Installation and Configuration : OpenEdge Getting Started" WHERE path like "gsins/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Multi-tenancy Overview : OpenEdge Getting Started" WHERE path like "gsmto/%"')
cur.execute('UPDATE searchIndex SET name = name || " : New and Revised Features : OpenEdge Getting Started" WHERE path like "gspub/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Studio : OpenEdge Getting Started" WHERE path like "gsstu/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Table Partitioning : OpenEdge Getting Started" WHERE path like "gstab/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Introducing the Progress Developer Studio for OpenEdge Visual Designer : OpenEdge Getting Started" WHERE path like "gsvis/%"')
cur.execute('UPDATE searchIndex SET name = name || " : WebSpeed Essentials : OpenEdge Getting Started" WHERE path like "gswsp/%"')

# OpenEdge Management
cur.execute('UPDATE searchIndex SET name = name || " : Configuration : OpenEdge Management" WHERE path like "oemcf/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Getting Started : OpenEdge Management" WHERE path like "oemgs/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Configuring Multi-tenancy : OpenEdge Management" WHERE path like "oemtc/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Managing Table Partitioning in Databases : OpenEdge Management" WHERE path like "oemtp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Alerts Guide and Reference : OpenEdge Management" WHERE path like "omalr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Database Management : OpenEdge Management" WHERE path like "omdbg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Getting Started with Multi-tenancy : OpenEdge Management" WHERE path like "ommtg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Pacific Application Server for OpenEdge Configuration : OpenEdge Management" WHERE path like "ompas/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Resource Monitoring : OpenEdge Management" WHERE path like "omrmg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Reporting : OpenEdge Management" WHERE path like "omrpt/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Servers, DataServers, Messengers, and Adapters : OpenEdge Management" WHERE path like "omsrv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Trend Database Guide and Reference : OpenEdge Management" WHERE path like "omtrd/%"')

cur.execute('UPDATE searchIndex SET name = name || " : Administration Guide : Pacific Application Server" WHERE path like "pasoe-admin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Introducing PAS for OpenEdge : Pacific Application Server" WHERE path like "pasoe-intro/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Application Migration and Development Guide : Pacific Application Server" WHERE path like "pasoe-migrate-develop/%"')

# PDSOE
cur.execute('UPDATE searchIndex SET name = name || " : Progress Developer Studio" WHERE path like "pdsoe/%"')

# OpenEdge Reporting
cur.execute('UPDATE searchIndex SET name = name || " : Query/Results Administration and Development : OpenEdge Reporting" WHERE path like "rpadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Report Builder Deployment : OpenEdge Reporting" WHERE path like "rpbld/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Deploying Crystal Reports : OpenEdge Reporting" WHERE path like "rpcry/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Query/Results for UNIX : OpenEdge Reporting" WHERE path like "rpunx/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Query/Results for Windows : OpenEdge Reporting" WHERE path like "rpwin/%"')

# OpenEdge White Papers
cur.execute('UPDATE searchIndex SET name = name || " : ABL Data Types Addenda : OpenEdge Web Paper" WHERE path like "wp-abl-datatypes/%"')
cur.execute('UPDATE searchIndex SET name = name || " : ABL Database Triggers and Indexes : OpenEdge Web Paper" WHERE path like "wp-abl-triggers/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Application Development Environment (ADE) Addenda : OpenEdge Web Paper" WHERE path like "wp-adeaddenda/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Batch-mode Event Support : OpenEdge Web Paper" WHERE path like "wp-batchmode/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Coding for Portability : OpenEdge Web Paper" WHERE path like "wp-codeport/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Dynamic Call Object : OpenEdge Web Paper" WHERE path like "wp-dyncall/%"')

db.commit()

db.close()
