import sys

__version__ = "1.06.01"

def require(version):
	currentVersion = __version__
	require_lib(version, currentVersion, "PythonTools")

def require_lib(version, currentVersion, libName):
	if __compare_versions(version, currentVersion) > 0:
		print >> sys.stderr, "This program requires %s version: %s" % (libName, version)
		exit(-1)

def __compare_versions(ver1, ver2):
	parts1 = [int(x) for x in ver1.split(".")]
	parts2 = [int(x) for x in ver2.split(".")]
	l1 = len(parts1)
	l2 = len(parts2)
	sizeDiff = abs(l1 - l2)
	maxSize = max(l1, l2)
	if l1 < l2:
		parts1.extend([0] * sizeDiff)
	elif l2 < l1:
		parts2.extend([0] * sizeDiff)
	for i in xrange(maxSize):
		if int(parts1[i]) > int(parts2[i]):
			return 1
		elif int(parts1[i]) < int(parts2[i]):
			return -1
	return 0
