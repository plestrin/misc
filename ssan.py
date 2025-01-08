#!/usr/bin/python

import sys
import os
import re
import hashlib
import enchant

DICT = enchant.Dict('en_US')
OWN_DICT = frozenset(('addr', 'aes', 'arg', 'cmd', 'ciphertext', 'del', 'desc', 'dev', 'dst', 'eax', 'ebx', 'ecx', 'edx', 'endianness', 'fpga', 'gettime', 'grep', 'hmac', 'init', 'ip', 'len', 'linux', 'malloc', 'mem', 'msg', 'nb', 'pci', 'pe', 'pid', 'plaintext', 'prev', 'proc', 'ptr', 'ptrace', 'rb', 'realloc', 'ret', 'shl', 'shr', 'sizeof', 'snprintf', 'spi', 'src', 'str', 'struct', 'sudo', 'tmp', 'tsearch', 'wunused', 'xor', 'xtea'))

EXCLUDE = ('.git',)

RE_TOKENIZE_WORD = re.compile(r'(?<!%)[a-zA-Z][a-z]*')

CONFIG_TAB_SIZE = 4
CONFIG_VERBOSE = False
CONFIG_MAX_REPORT = 10

CHECK_ALIGN_MUL_MACRO 	= 1
CHECK_DOUBLE_SPACE 		= 2
CHECK_EMPTY_FILE 		= 3
CHECK_EMPTYL_BEG 		= 4
CHECK_EMPTYL_END 		= 5
CHECK_EXPLICIT_NZCOND 	= 6
CHECK_EXPLICIT_ZCOND 	= 7
CHECK_INDENT_SPACE 		= 8
CHECK_MALLOC_CAST 		= 9
CHECK_NEW_LINE_EOF 		= 10
CHECK_MISSING_VOID_PROT = 11
CHECK_RECURSIVE_INCLUDE = 12
CHECK_SPACE_BRACE 		= 13
CHECK_SPACE_PARENTHESIS = 14
CHECK_SPACE_COMMA 		= 15
CHECK_SPACE_COND 		= 16
CHECK_SPACE_EOL 		= 17
CHECK_SPACE_OPERATOR 	= 18
CHECK_SEVERAL_SEMICOL 	= 19
CHECK_SPELLING 			= 20
CHECK_WINDOWS_CARRIAGE 	= 21

HASH_SET = set()

def hash_file(file_name):
	sha256 = hashlib.sha256()

	with open(file_name, 'rb') as f:
		while True:
			data = f.read(65536)
			sha256.update(data)
			if len(data) != 65536:
				break

	return sha256.digest()

def is_elf_file(file_name):
	with open(file_name, 'rb') as f:
		elf_hdr = f.read(16)
	if len(elf_hdr) != 16:
		return False
	if not elf_hdr[ : 4] == '\x7fELF': # magic
		return False
	if elf_hdr[4] not in ('\x00', '\x01', '\x02'): # class
		return False
	if elf_hdr[5] not in ('\x00', '\x01', '\x02'): # encoding
		return False
	return elf_hdr[9 : ] == '\x00\x00\x00\x00\x00\x00\x00'

def report(check_id, file_name, line, auto, arg=None):
	string = "??"

	if check_id == CHECK_ALIGN_MUL_MACRO:
		string = 'alignment in multi-line macro'
	elif check_id == CHECK_DOUBLE_SPACE:
		string = 'double space'
	elif check_id == CHECK_EMPTY_FILE:
		string = 'empty file'
	elif check_id == CHECK_EMPTYL_BEG:
		string = 'empty line at the beginning of file'
	elif check_id == CHECK_EMPTYL_END:
		string = 'empty line at the end of file'
	elif check_id == CHECK_EXPLICIT_NZCOND:
		string = 'explicit non-zero condition'
	elif check_id == CHECK_EXPLICIT_ZCOND:
		string = 'explicit zero condition'
	elif check_id == CHECK_INDENT_SPACE:
		string = 'indented with space'
	elif check_id == CHECK_MALLOC_CAST:
		string = 'explicit cast result of calloc/malloc/realloc'
	elif check_id == CHECK_MISSING_VOID_PROT:
		string = 'missing void in prototype'
	elif check_id == CHECK_NEW_LINE_EOF:
		string = 'no new line at EOF'
	elif check_id == CHECK_RECURSIVE_INCLUDE:
		string = 'non standard / missing protection to prevent recursive include'
	elif check_id == CHECK_SPACE_BRACE:
		string = 'no space before / after brace'
	elif check_id == CHECK_SPACE_PARENTHESIS:
		string = 'unintended space after opening parenthesis or before closing parenthesis'
	elif check_id == CHECK_SPACE_COMMA:
		string = 'no space after comma'
	elif check_id == CHECK_SPACE_COND:
		string = 'no space before condition'
	elif check_id == CHECK_SPACE_EOL:
		string = 'space(s) / tab(s) at EOL'
	elif check_id == CHECK_SPACE_OPERATOR:
		string = 'no space around operator'
	elif check_id == CHECK_SEVERAL_SEMICOL:
		string = 'several semi-column'
	elif check_id == CHECK_SPELLING:
		string = 'spell check'
	elif check_id == CHECK_WINDOWS_CARRIAGE:
		string = 'Windows carriage return'

	try:
		check_id_loc = report.check_id
	except AttributeError:
		report.check_id = check_id
	try:
		file_name_loc = report.file_name
	except AttributeError:
		report.file_name = file_name
	try:
		counter_loc = report.counter
	except AttributeError:
		report.counter = 0

	if report.check_id != check_id or report.file_name != file_name:
		report.file_name = file_name
		report.check_id = check_id
		report.counter = 0

	if CONFIG_VERBOSE or report.counter < CONFIG_MAX_REPORT:
		sys.stdout.write(file_name + ':' + str(line) + ' - ' + string)
		if arg is not None:
			sys.stdout.write(' ' + arg)
		if not auto:
			sys.stdout.write(' [no auto-correct]\n')
		else:
			sys.stdout.write('\n')
	elif report.counter == CONFIG_MAX_REPORT:
		sys.stdout.write('\x1b[33m[-]\x1b[0m stop reporting: \'' + string + '\' for file ' + file_name + '\n')
	report.counter += 1

def generic_spelling(strings, file_name, line, file_typo):
	for string in strings:
		words = RE_TOKENIZE_WORD.findall(string)
		for word in words:
			lword = word.lower()
			if len(word) < 32 and not DICT.check(word) and lword not in OWN_DICT and lword not in file_typo:
				report(CHECK_SPELLING, file_name, line, False, '\x1b[31m' + word + '\x1b[0m in ' + string)
				file_typo.add(lword)

def sscan_space_parenthesis(lines, file_name, auto=False):
	rewrite = False

	for i, line in enumerate(lines):
		line_rewrite = False

		# Space after opening parenthesis
		idx = line.find('( ')
		while idx != -1:
			if not auto:
				line_rewrite = True
				break

			sz = 2
			while idx + sz < len(line) and line[idx + sz] == ' ':
				sz += 1
			line = line[:idx + 1] + line[idx + sz:]
			line_rewrite = True
			idx = line.find('( ')

		# Space before closing parenthesis
		for j, b in enumerate(line):
			if b != ' ' or b != '\t':
				idx = line.find(' )', j + 1)
				while idx != -1:
					if not auto:
						line_rewrite = True
						break

					sz = 0
					while idx - sz > j + 1 and line[idx - sz - 1] == ' ':
						sz += 1
					line = line[:idx - sz] + line[idx + 1:]
					line_rewrite = True
					idx = line.find(' )', j + 1)
				break

		if line_rewrite:
			report(CHECK_SPACE_PARENTHESIS, file_name, i + 1, auto)
			lines[i] = line
			rewrite = auto

	return rewrite, lines

def sscan_text(lines, file_name):
	rewrite = False

	# Check empty file
	if not lines:
		report(CHECK_EMPTY_FILE, file_name, 0, False)
	else:
		# Check Windows newline
		for i, line in enumerate(lines):
			if line.find('\r') != -1:
				report(CHECK_WINDOWS_CARRIAGE, file_name, i + 1, True)
				lines[i] = line.replace('\r', '')
				rewrite = True

		# Check empty lines
		if lines[-1][-1] != '\n':
			report(CHECK_NEW_LINE_EOF, file_name, len(lines), True)
			lines[-1] = lines[-1] + '\n'
			rewrite = True
		elif lines[-1] == '\n':
			report(CHECK_EMPTYL_END, file_name, len(lines), True)
			while lines and lines[-1] == '\n':
				lines = lines[:-1]
			rewrite = True
		if not lines:
			report(CHECK_EMPTY_FILE, file_name, 0, False)
		else:
			if lines[0] == '\n':
				report(CHECK_EMPTYL_BEG, file_name, 1, True)
				while lines[0] == '\n':
					lines = lines[1:]
				rewrite = True

			# Space or tab at end of line
			regex = re.compile(r'[ \t]+$')
			for i, line in enumerate(lines):
				if regex.findall(line):
					report(CHECK_SPACE_EOL, file_name, i + 1, True)
					lines[i] = regex.sub('', line)
					rewrite = True

	return rewrite, lines

def sscan_ccode(lines, file_name):
	rewrite = False

	# Double space
	regex = re.compile(r'( {2}|\t )')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_INDENT_SPACE, file_name, i + 1, False)

	# Space before condition
	regex = re.compile(r'(^|[\t }])(if|for|while|switch)\(')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_SPACE_COND, file_name, i + 1, True)
			lines[i] = regex.sub(r'\1\2 (', line)
			rewrite = True

	# Explicit non-zero condition
	regex = re.compile(r'(!= *0[ )&|]|[ (&|]0 *!=)')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_EXPLICIT_NZCOND, file_name, i + 1, False)

	# Explicit zero condition
	regex = re.compile(r'(== *0[ )&|]|[ (&|]0 *==)')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_EXPLICIT_ZCOND, file_name, i + 1, False)

	# Remove unnecessary cast
	regex = re.compile(r'\([^()]+\*\)(calloc|malloc|realloc)\(')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_MALLOC_CAST, file_name, i + 1, True)
			lines[i] = regex.sub(r'\1(', line)
			rewrite = True

	# Spell check strings
	regex1 = re.compile(r'(?<!include )"[^"]*"')
	regex2 = re.compile(r'%[0-9]*(c|d|p|s|u|x|lld|llu|llx)')
	file_typo = set()
	for i, line in enumerate(lines):
		strings = regex1.findall(line)
		strings = [regex2.sub('', string) for string in strings]
		generic_spelling(strings, file_name, i + 1, file_typo)

	# Non-void prototype
	regex = re.compile(r'([a-zA-Z0-9_]+)[ ]*\(\)[ ]*\{')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_MISSING_VOID_PROT, file_name, i + 1, True)
			lines[i] = regex.sub(r'\1(void){', line)
			rewrite = True

	# Space before brace for struct/enum/union definition
	regex = re.compile(r'((struct|enum|union) [a-zA-Z0-9_]+){')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_SPACE_BRACE, file_name, i + 1, True)
			lines[i] = regex.sub(r'\1 {', line)
			rewrite = True

	# Space before brace for else/do statement
	regex = re.compile(r'((else|do)){')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_SPACE_BRACE, file_name, i + 1, True)
			lines[i] = regex.sub(r'\1 {', line)
			rewrite = True

	# Space after closing brace for do ... while statement
	regex = re.compile(r'}while')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_SPACE_BRACE, file_name, i + 1, True)
			lines[i] = regex.sub(r'} while', line)
			rewrite = True

	# No space or new line after comma
	for i, line in enumerate(lines):
		idx = line.find(',')
		while idx != -1:
			if idx + 1 < len(line) and line[idx + 1] not in (' ', '\n'):
				report(CHECK_SPACE_COMMA, file_name, i + 1, False)
			idx = line.find(',', idx + 1)

	# No space around boolean operator
	regex1 = re.compile(r'(==|<=|>=|!=|&&|\|\|)(?![ \t])')
	regex2 = re.compile(r'(?<![ \t])(==|<=|>=|!=|&&|\|\|)')
	for i, line in enumerate(lines):
		if regex1.findall(line):
			report(CHECK_SPACE_OPERATOR, file_name, i + 1, True)
			line = regex1.sub(r'\1 ', line)
			lines[i] = line
			rewrite = True
		if regex2.findall(line):
			report(CHECK_SPACE_OPERATOR, file_name, i + 1, True)
			lines[i] = regex2.sub(r' \1', line)
			rewrite = True

	# More than one semi column
	regex = re.compile(r';;+')
	for i, line in enumerate(lines):
		if regex.findall(line):
			report(CHECK_SEVERAL_SEMICOL, file_name, i + 1, False)
			# no auto correct because it is a rare mistake and correction will mess up with the for (;;){ syntax

	# Multi-line macro
	prev_size = 0
	for i, line in enumerate(lines):
		if line[-2:] == '\\\n':
			size = 0
			for c in line[:-2]:
				if c == '\t':
					size += CONFIG_TAB_SIZE - (size % CONFIG_TAB_SIZE)
				else:
					size += 1
			if prev_size:
				if size > prev_size:
					report(CHECK_ALIGN_MUL_MACRO, file_name, i + 1, False)
				if size < prev_size:
					while size < prev_size:
						lines[i] = lines[i][:-2] + '\t\\\n'
						size += CONFIG_TAB_SIZE - (size % CONFIG_TAB_SIZE)
						rewrite = True
					report(CHECK_ALIGN_MUL_MACRO, file_name, i + 1, True)
			elif size % CONFIG_TAB_SIZE:
				lines[i] = lines[i][:-2] + '\t\\\n'
				prev_size = size + CONFIG_TAB_SIZE - (size % CONFIG_TAB_SIZE)
				report(CHECK_ALIGN_MUL_MACRO, file_name, i + 1, True)
				rewrite = True
			else:
				prev_size = size
		else:
			prev_size = 0

	return rewrite, lines

def sscan_cheader(lines, file_name):
	# Recursive include protection
	if len(lines) < 3:
		report(CHECK_RECURSIVE_INCLUDE, file_name, 0, False)
	else:
		if lines[0] != '#ifndef ' + os.path.basename(file_name)[:-2].upper() + '_H\n':
			report(CHECK_RECURSIVE_INCLUDE, file_name, 1, False)
		elif lines[1] != '#define ' + os.path.basename(file_name)[:-2].upper() + '_H\n':
			report(CHECK_RECURSIVE_INCLUDE, file_name, 2, False)
		elif lines[-1] != '#endif\n':
			report(CHECK_RECURSIVE_INCLUDE, file_name, len(lines), False)

	return False, lines

def sscan_pcode(lines, file_name):
	# Double space in the middle of a line
	for i, line in enumerate(lines):
		for j, b in enumerate(line):
			if b != ' ' or b != '\t':
				if line[j:].find('  ') != -1:
					report(CHECK_DOUBLE_SPACE, file_name, i + 1, False)
				break

	return False, lines

def dispatcher(root_name, file_name):
	# Rename file
	base_name = os.path.basename(file_name)
	full_name = os.path.join(root_name, file_name)

	new_file_name = file_name
	if new_file_name.endswith('.yar'):
		new_file_name = new_file_name + 'a'
	if new_file_name.find(' ') != -1:
		new_file_name = new_file_name.replace(' ', '_')
	if new_file_name.lower() == 'readme.md' and new_file_name != 'README.md':
		new_file_name = 'README.md'
	if new_file_name.lower() == 'makefile' and new_file_name != 'Makefile':
		new_file_name = 'Makefile'

	if file_name != new_file_name:
		new_full_name = os.path.join(root_name, new_file_name)
		if os.path.exists(new_full_name):
			sys.stdout.write('\x1b[33m[-]\x1b[0m cannot move %s to %s : file exists already\n' % (full_name, new_full_name))
		else:
			os.rename(full_name, new_full_name)
			sys.stdout.write('\x1b[32m[+]\x1b[0m file %s move to %s\n' % (full_name, new_full_name))
			full_name = new_full_name
			file_name = new_file_name
			base_name = os.path.basename(new_file_name)

	# Check duplicate
	sha256 = hash_file(full_name)
	if sha256 in HASH_SET:
		sys.stdout.write('\x1b[33m[-]\x1b[0m file %s is a duplicate\n' % full_name)
	else:
		HASH_SET.add(sha256)

	sscan_list = []

	if base_name.endswith('.a'):
		return
	elif base_name.endswith('.asm'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.bin'):
		return
	elif base_name.endswith('.c'):
		sscan_list = [sscan_text, sscan_ccode, sscan_space_parenthesis]
	elif base_name.endswith('.cpp'):
		sscan_list = [sscan_text, sscan_ccode, sscan_space_parenthesis]
	elif base_name.endswith('.dll'):
		return
	elif base_name.endswith('.exe'):
		return
	elif base_name == '.gitignore':
		sscan_list = [sscan_text]
	elif base_name.endswith('.gz'):
		return
	elif base_name.endswith('.h'):
		sscan_list = [sscan_text, sscan_ccode, sscan_cheader, sscan_space_parenthesis]
	elif base_name.endswith('.html'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.i64'):
		return
	elif base_name.endswith('.idb'):
		return
	elif base_name.endswith('.js'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.go'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.ko'):
		return
	elif base_name.endswith('.log'):
		return
	elif base_name.endswith('.md'):
		sscan_list = []
	elif base_name.endswith('.o'):
		return
	elif base_name.endswith('.obj'):
		return
	elif base_name.endswith('.patch'):
		return
	elif base_name.endswith('.pcap'):
		return
	elif base_name.endswith('.pdf'):
		return
	elif base_name.endswith('.pem'):
		return
	elif base_name.endswith('.png'):
		return
	elif base_name.endswith('.py'):
		sscan_list = [sscan_text, sscan_pcode, sscan_space_parenthesis]
	elif base_name.endswith('.pyc'):
		return
	elif base_name.endswith('.rb'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.sh'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.so'):
		return
	elif base_name.endswith('.symvers'):
		return
	elif base_name.endswith('.sys'):
		return
	elif base_name.endswith('.tgz'):
		return
	elif base_name.endswith('.txt'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.yara'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.xml'):
		sscan_list = [sscan_text]
	elif base_name.endswith('.zip'):
		return
	elif base_name in ('Makefile', 'Dockerfile'):
		sscan_list = [sscan_text]
	else:
		if not is_elf_file(full_name):
			sys.stdout.write('\x1b[33m[-]\x1b[0m file %s has no known type -> skip\n' % full_name)
		return

	with open(full_name, 'r') as f:
		lines = f.readlines()

	rewrite = False

	for sscan in sscan_list:
		local_rewrite, lines = sscan(lines, full_name)
		rewrite |= local_rewrite

	if rewrite:
		with open(full_name, 'w') as f:
			for line in lines:
				f.write(line)
		sys.stdout.write('\x1b[32m[+]\x1b[0m fixed problem(s) in %s\n' % full_name)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.stderr.write('\x1b[31m[!]\x1b[0m Usage: %s [-v] path\n' % sys.argv[0])
		sys.exit(1)

	path_args = []
	for arg in sys.argv[1:]:
		if arg == '-v':
			CONFIG_VERBOSE = True
		else:
			path_args.append(arg)

	for arg in path_args:
		if os.path.isdir(arg):
			for root, subdirs, files in os.walk(arg, topdown=True):
				subdirs[:] = [subdir for subdir in subdirs if subdir not in EXCLUDE]
				for f in files:
					dispatcher(root, f)
		elif arg not in EXCLUDE:
			dispatcher('', arg)
