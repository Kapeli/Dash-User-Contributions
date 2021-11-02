import os, re, sqlite3, glob

# Script to generate index for Dash docset. Notice that this code isn't really what you call 'production ready' but should get the job done.

db = sqlite3.connect('OpenCL.docset/Contents/Resources/docSet.dsidx')
cur = db.cursor()

try: cur.execute('DROP TABLE searchIndex;')
except: pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

# It's expected that files from http://www.khronos.org/registry/cl/sdk/<version>/docs/man/xhtml has been downloaded into the Documents directory and also the specs pdf
# which can be found here http://www.khronos.org/registry/cl/specs/opencl-<version>.pdf

docpath = 'OpenCL.docset/Contents/Resources/Documents'

# will replace the file path to the opencl spec

def patch_pdf_link(file):
	f = open(file, 'r')
	filedata = f.read()
	f.close()

	newdata = filedata.replace("http://www.khronos.org/registry/cl/specs/","")

	f = open(file, 'w')
	f.write(newdata)
	f.close()

# This will parse the enum file and insert all the enums as constants

def parse_enum_file(file_path):
	prog = re.compile('CL\w+')
	f = open(os.path.join(file_path, 'enums.html'), "r")
	lines = f.readlines()
	f.close()

	for line in lines:
		enum = prog.search(line)
		if enum != None:
			cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (enum.group(0), 'Constant', 'enums.html'))

	return


# This is somewhat a manual thing to do but should hopefully be fine
# List of files that doesn't contain functions

file_skip_list = ["abstractDataTypes", "accessQualifiers", "asyncCopyFunctions", 
				  "atomicFunctions", "attribute", "classDiagram", "commonFunctions", "constant", "convert_T", "enums",
				  "cl_",
				  "d3d10_sharing",
				  "EXTENSION",
				  "explicitMemoryFenceFunctions",
				  "FP_CONTRACT", "functionQualifiers", "geometricFunctions",
				  "math",
				  "macroLimits",
				  "oclRefPages-Title",
				  "operators",
				  "otherDataTypes",
				  "preprocessorDirectives",
				  "sampler_t",
				  "miscVectorFunctions",
				  "imageFunctions",
				  "integer",
				  "relationalFunctions",
				  "reserverdDataTypes",
				  "scalarDataTypes",
				  "supportedImageFormats",
				  "vectorData",
				  "commonMax",
				  "commonMin",
				  "workItemFunctions"]

# Check if file represents a function and should be added to the function list

def is_file_function(name):
	for skip_file in file_skip_list:
		if name.find(skip_file) != -1:
			return False;
	return True;

# Handle all thefunctions

for file in glob.glob(os.path.join(docpath, "*.html")):
	patch_pdf_link(file)

	path = os.path.basename(file)
	name = os.path.splitext(path)[0]

	if is_file_function(name):
		cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Function', path))
		print 'name: %s, path: %s' % (name, path)


# Manually insert some functions

cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', ('min', 'Function', 'commonMin.html'))
cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', ('max', 'Function', 'commonMax.html'))

# Types

for ab_type in ['cl_platform_id', 'cl_device_id', 'cl_context', 'cl_command_queue', 'cl_mem', 'cl_kernel', 'cl_event', 'cl_sampler']: 
	cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (ab_type, 'Type', 'abstractDataTypes.html'))

for ab_type in ['__read_only', 'read_only', '__write_only', 'write_only']: 
	cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (ab_type, 'Attribute', 'accessQualifiers.html'))

cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', ('__attribtue__', 'Attribute', 'attribute.html'))

for ab_type in ['constant', '__constant']: 
	cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (ab_type, 'Attribute', 'constant.html'))

parse_enum_file(docpath)

db.commit()
db.close()
