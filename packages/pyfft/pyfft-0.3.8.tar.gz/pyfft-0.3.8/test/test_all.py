import optparse
import sys

from test_performance import run as run_perf
from test_errors import run as run_err
from test_functionality import run as run_func
from helpers import DEFAULT_BUFFER_SIZE, isCudaAvailable, isCLAvailable


# Parser settings

parser = optparse.OptionParser(usage = "test_all.py <mode> [options]\n" +
	"Modes: func, err, perf")

parser.add_option("-c", "--cuda", action="store_true",
	dest="test_cuda", help="run Cuda tests", default=False)
parser.add_option("-o", "--opencl", action="store_true",
	dest="test_opencl", help="run OpenCL tests", default=False)

parser.add_option("-a", "--accurate-math", action="store_false",
	dest="fast_math", help="Use slow, but more accurate math", default=True)
parser.add_option("-s", "--buffer-size", action="store", type="int", default=DEFAULT_BUFFER_SIZE,
	dest="buffer_size", help="Maximum test buffer size, Mb")
parser.add_option("-d", "--double-precision", action="store_true",
	dest="double", help="Run tests in double precision", default=False)

# Parse options and run tests
modes = ['func', 'err', 'perf']

if len(sys.argv) == 1:
	to_run = modes
	args = []
else:
	# FIXME: find a way to do it using OptionParser
	mode = sys.argv[1]
	args = sys.argv[2:]

	if mode.startswith("-"):
		args = [mode] + args
		to_run = modes
	elif mode not in modes:
		parser.print_help()
		sys.exit(1)
	else:
		to_run = [mode]

opts, args = parser.parse_args(args)

if not opts.test_cuda and not opts.test_opencl:
	opts.test_cuda = isCudaAvailable()
	opts.test_opencl = isCLAvailable()

if 'func' in to_run:
	run_func(opts.test_cuda, opts.test_opencl)
if 'err' in to_run:
	run_err(opts.test_cuda, opts.test_opencl, opts.buffer_size, opts.fast_math, opts.double)
if 'perf' in to_run:
	run_perf(opts.test_cuda, opts.test_opencl, opts.buffer_size, opts.fast_math, opts.double)
