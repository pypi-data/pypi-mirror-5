import sys
import glob
from assembler import assemble, ascii_binary_to_real_binary


def main():

    if len(sys.argv) == 1:
        print "USAGE: galapagos-as [-d] source.gas [source2.gas ...]"
        return

    debug = '-d' in sys.argv

    paths = filter(lambda x: x[0] != '-',
                   [item for sublist in map(glob.glob, sys.argv[1:])
                    for item in sublist])

    for path in paths:
        with open(path, 'r') as f:
            assembly = [line for line in f]
        assembled = assemble(assembly)

        if not assembled:
            return

        address = 0
        ascii_binary = []
        for line in assembled:
            ascii_binary.append(line.toBinary())
            if debug:
                print 'Address: %s' % address
                print 'text: ' + str(line)
                print line.toBinary(debug=debug)
                print
            address += 1

        ascii_binary = ''.join(ascii_binary)

        with open(path + '.out', 'w') as f:
            f.write(ascii_binary_to_real_binary(ascii_binary))


if __name__ == '__main__':
    main()
