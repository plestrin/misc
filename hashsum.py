import hashlib
import sys

def get_hashes(path):
	m5 = hashlib.md5()
	s1 = hashlib.sha1()
	s2 = hashlib.sha256()
	sz = 0
	with open(path, 'rb') as stream:
		while True:
			data = stream.read(0x80000)
			m5.update(data)
			s1.update(data)
			s2.update(data)
			sz += len(data)
			if len(data) < 0x80000:
				break
	return (sz, m5.hexdigest(), s1.hexdigest(), s2.hexdigest())

for arg in sys.argv[1:]:
	size, md5, sha1, sha256 = get_hashes(arg)
	print('Size    %u' % size)
	print('MD5     %s' % md5)
	print('SHA-1   %s' % sha1)
	print('SHA-256 %s' % sha256)
