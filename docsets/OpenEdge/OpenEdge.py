#!/usr/bin/python

import os, re, sqlite3
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
       cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Guide', path))
       print 'adding file path: %s, name: %s' % (path, name)

   db.commit()


from findtools.find_files import (find_files, Match)

sh_files_pattern = Match(filetype='f', name='*.html')
found_files = find_files(path=docpath, match=sh_files_pattern)

for found_file in found_files:
    print 'editing file: %s' % (found_file)
    
    # Remove the onload attribute from the body tag
    # <body id="pYxQs0eniL26fH5dRGlU43A" class="ww_skin_page_body" onload="Page.OnLoad('../index.html#page/dvref/xml-data-type-attribute.html');">

    soup = BeautifulSoup(open(found_file))

    any = re.compile('.*')
    
    for tag in soup.find_all('body'):
        
        tag = soup.body

        del tag['onload']
        tag

    html = str(soup)
    with open((found_file),"wb") as file:
        file.write(html)

# Special Types

# Annotation Attribute Binding Builtin Callback Category Class Command Component Constant Constructor Define Delegate Diagram Directive Element Entry Enum Environment Error Event Exception Extension Field File Filter Framework Function Global Guide Hook Instance Instruction Interface Keyword Library Literal Macro Method Mixin Modifier Module Namespace Notation Object Operator Option Package Parameter Plugin Procedure Property Protocol Provider Provisioner Query Record Resource Sample Section Service Setting Shortcut Statement Struct Style Subroutine Tag Test Trait Type Union Value Variable Word

cur.execute('UPDATE searchIndex SET type = "Command" WHERE type = "Guide" and (name like "%command" or name like "%commands")')
cur.execute('UPDATE searchIndex SET type = "Command" WHERE type = "Guide" and (name like "%utility" or name like "%qualifier")')
cur.execute('UPDATE searchIndex SET type = "Parameter" WHERE type = "Guide" and (name like "%parameter" or name like "%parameters")')
cur.execute('UPDATE searchIndex SET type = "Parameter" WHERE type = "Guide" and (name like "% (-%)")')
cur.execute('UPDATE searchIndex SET type = "Attribute" WHERE type = "Guide" and (name like "%attribute" or name like "%attributes")')
cur.execute('UPDATE searchIndex SET type = "Class" WHERE type = "Guide" and (name like "%class" or name like "%classes")')
cur.execute('UPDATE searchIndex SET type = "Event" WHERE type = "Guide" and (name like "%event" or name like "%events")')
cur.execute('UPDATE searchIndex SET type = "Function" WHERE type = "Guide" and (name like "%function" or name like "%functions")')
cur.execute('UPDATE searchIndex SET type = "Instance" WHERE type = "Guide" and (name like "%instance")')
cur.execute('UPDATE searchIndex SET type = "Interface" WHERE type = "Guide" and (name like "%interface")')
cur.execute('UPDATE searchIndex SET type = "Method" WHERE type = "Guide" and (name like "%method" or name like "%methods")')
cur.execute('UPDATE searchIndex SET type = "Object" WHERE type = "Guide" and (name like "%object" or name like "%object")')
cur.execute('UPDATE searchIndex SET type = "Procedure" WHERE type = "Guide" and (name like "%procedure" or name like "%procedures")')
cur.execute('UPDATE searchIndex SET type = "Protocol" WHERE type = "Guide" and (name like "%protocol" or name like "%protocols")')
cur.execute('UPDATE searchIndex SET type = "Query" WHERE type = "Guide" and (name like "%query" or name like "%queries")')
cur.execute('UPDATE searchIndex SET type = "Statement" WHERE type = "Guide" and (name like "%statement" or name like "%statements")')
cur.execute('UPDATE searchIndex SET type = "Type" WHERE type = "Guide" and (name like "%type" or name like "%types")')
cur.execute('UPDATE searchIndex SET type = "Operator" WHERE type = "Guide" and (name like "%operator" or name like "%preprocessor directive" or name like "%preprocessor directives" or name like "%punctuation" or name like "%special character" or name like "%expression precedence" or name like "%array reference" or name like "%character-string literal" or name like "%preprocessor name reference")')


# Rename all topic titles to include the section at the end            
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Application Server: Administration" WHERE path like "asadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Application Server: Developing AppServer Applications" WHERE path like "asaps/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Application Server: Developing WebSpeed Applications" WHERE path like "aswsp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Application Developers Guide" WHERE path like "bpm-appdev/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: BP Server Developers Guide" WHERE path like "bpm-bpserver/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge BPM BusinessManager: Clustering Guide" WHERE path like "bpm-cluster/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Customization Guide" WHERE path like "bpm-custom/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: BPM Events Users Guide" WHERE path like "bpm-events/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: First Steps Guide" WHERE path like "bpm-first/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Managed Adapters Guide" WHERE path like "bpm-manadapter/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge: Migrating to OpenEdge Business Process Management 11.5" WHERE path like "bpm-migrate/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Modeler: Users Guide" WHERE path like "bpm-modeler-user/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Business Process Portal Administrators Guide" WHERE path like "bpm-portal-admin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Business Process Portal Managers Guide" WHERE path like "bpm-portal-manage/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Business Process Portal Users Guide" WHERE path like "bpm-portal-user/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Server Administrators Guide" WHERE path like "bpm-serveradmin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Developing BPM Applications with Developer Studio" WHERE path like "bpm-studio-ug/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Terminology Guide" WHERE path like "bpm-term/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Troubleshooting Guide" WHERE path like "bpm-trouble/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress OpenEdge Business Process Server: Web Services Developers Guide" WHERE path like "bpm-web/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress Developer Studio for OpenEdge: OpenEdge Business Rules" WHERE path like "busrules/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Copyright" WHERE path like "copyright/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Data Management: Database Administration" WHERE path like "dmadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Data Management: DataServer for ODBC" WHERE path like "dmodb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Data Management: DataServer for Oracle" WHERE path like "dmora/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Data Management: SQL Development" WHERE path like "dmsdv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Data Management: DataServer for Microsoft SQL Server" WHERE path like "dmsql/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Data Management: SQL Reference" WHERE path like "dmsrf/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Deployment: Managing ABL Applications" WHERE path like "dpabl/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Deployment: Startup Command and Parameter Reference" WHERE path like "dpspr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Deployment: WebClient Applications" WHERE path like "dpweb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: ADM Reference" WHERE path like "dvadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: AppBuilder" WHERE path like "dvapb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Debugging and Troubleshooting" WHERE path like "dvdbg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Basic Database Tools" WHERE path like "dvdbt/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Basic Development Tools" WHERE path like "dvdvt/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Error Handling" WHERE path like "dverr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Messaging and ESB" WHERE path like "dvesb/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Internationalizing Applications" WHERE path like "dvint/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Java Open Clients" WHERE path like "dvjav/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Working with JSON" WHERE path like "dvjsn/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Mobile Applications" WHERE path like "dvmad/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: .NET Open Clients" WHERE path like "dvnet/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: GUI for .NET Mapping Reference" WHERE path like "dvngm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: GUI for .NET Programming" WHERE path like "dvngp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: ADM and SmartObjects" WHERE path like "dvobj/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Open Client Introduction and Programming" WHERE path like "dvoci/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Object-oriented Programming" WHERE path like "dvoop/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: ProDataSets" WHERE path like "dvpds/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Programming Interfaces" WHERE path like "dvpin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: ABL Reference" WHERE path like "dvref/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Translation Manager" WHERE path like "dvtmg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Visual Translator" WHERE path like "dvvis/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Web Services" WHERE path like "dvwsv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Development: Working with XML" WHERE path like "dvxml/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Replication: User Guide" WHERE path like "ffr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: ABL Essentials" WHERE path like "gsabl/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Application and Integration Services" WHERE path like "gsais/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Core Business Services - Security and Auditing" WHERE path like "gscsv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Database Essentials" WHERE path like "gsdbe/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Guide for New Developers" WHERE path like "gsdev/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: GUI for .NET Primer" WHERE path like "gsgnp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Identity Management" WHERE path like "gsidm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Installation and Configuration" WHERE path like "gsins/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Multi-tenancy Overview" WHERE path like "gsmto/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: New and Revised Features" WHERE path like "gspub/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Progress OpenEdge Studio" WHERE path like "gsstu/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Table Partitioning" WHERE path like "gstab/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: Introducing the Progress Developer Studio for OpenEdge Visual Designer" WHERE path like "gsvis/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Getting Started: WebSpeed Essentials" WHERE path like "gswsp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management and OpenEdge Explorer: Configuration" WHERE path like "oemcf/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management and OpenEdge Explorer: Getting Started" WHERE path like "oemgs/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management and OpenEdge Explorer: Configuring Multi-tenancy" WHERE path like "oemtc/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management and OpenEdge Explorer: Managing Table Partitioning in Databases" WHERE path like "oemtp/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Alerts Guide and Reference" WHERE path like "omalr/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Database Management" WHERE path like "omdbg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management and OpenEdge Explorer: Getting Started with Multi-tenancy" WHERE path like "ommtg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Pacific Application Server for OpenEdge Configuration" WHERE path like "ompas/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Resource Monitoring" WHERE path like "omrmg/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Reporting" WHERE path like "omrpt/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Servers, DataServers, Messengers, and Adapters" WHERE path like "omsrv/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Management: Trend Database Guide and Reference" WHERE path like "omtrd/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Pacific Application Server for OpenEdge: Administration Guide" WHERE path like "pasoe-admin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Pacific Application Server for OpenEdge: Introducing PAS for OpenEdge" WHERE path like "pasoe-intro/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Pacific Application Server for OpenEdge: Application Migration and Development Guide" WHERE path like "pasoe-migrate-develop/%"')
cur.execute('UPDATE searchIndex SET name = name || " : Progress Developer Studio for OpenEdge Online Help" WHERE path like "pdsoe/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Reporting: Query/Results Administration and Development" WHERE path like "rpadm/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Reporting: Report Builder Deployment" WHERE path like "rpbld/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Reporting: Deploying Crystal Reports" WHERE path like "rpcry/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Reporting: Query/Results for UNIX" WHERE path like "rpunx/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Reporting: Query/Results for Windows" WHERE path like "rpwin/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Web Paper: ABL Data Types Addenda" WHERE path like "wp-abl-datatypes/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Web Paper: ABL Database Triggers and Indexes" WHERE path like "wp-abl-triggers/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Web Paper: Application Development Environment (ADE) Addenda" WHERE path like "wp-adeaddenda/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Web Paper: Batch-mode Event Support" WHERE path like "wp-batchmode/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Web Paper: Coding for Portability" WHERE path like "wp-codeport/%"')
cur.execute('UPDATE searchIndex SET name = name || " : OpenEdge Web Paper: Dynamic Call Object" WHERE path like "wp-dyncall/%"')


db.commit()

db.close()
