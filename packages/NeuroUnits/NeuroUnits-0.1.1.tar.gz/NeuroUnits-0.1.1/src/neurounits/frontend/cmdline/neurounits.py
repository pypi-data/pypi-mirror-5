
#! /usr/bin/python



import os

#print os.environ



import argparse
from neurounits import NeuroUnitParser, NutsIO
from itertools import chain


def build_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--validate', dest='validate', action='store_true')

    parser.add_argument('--extract', dest='extract', action='store_true')
    parser.add_argument('--extract-level', dest='extract_level', action='store', nargs=1)
    parser.add_argument('--extract-to', dest='extract_to', action='store', nargs=1)
    parser.add_argument('files', nargs='+')
    return parser





def validate_eqn(filename):
    print 'Validating:', filename
    f = NeuroUnitParser.File(open(filename).read())
    print '  ', f.summary()

def validate_nuts(filename):
    NutsIO.validate(filename)
    print 'Validating:', filename

import StringIO

def extract(filenames, level,output_file):

    lines = list( chain(* [NutsIO.load(fname) for fname in filenames]))

    # Extract the relevant lines: 
    if level:
        level = level[0]
        lines = [l for l in lines if l.options.type.startswith(level)]
    
    # Open the output file:
    if output_file:
        output_file = output_file[0]
        f = open(output_file,'w')
    else:
        f = StringIO.StringIO()

    # Write the output
    for line in lines:
        op = line.line + '\n'
        print op
        f.write(op)

    print 'Level', level
    print lines
    print 'Extracting:'



def main():
    parser = build_parser()
    args= parser.parse_args()

    print args.files
    print 'validate', args.validate
    print 'extract', args.extract

    # Validation:
    if args.validate:
        for f in args.files:
            if f.endswith('.eqn'):
                validate_eqn(f)

            if f.endswith('nuts'):
                validate_nuts(f)

    # Extraction:
    if args.extract:
        tgts = [f for f in args.files if f.endswith('nuts') ]
        extract(tgts, args.extract_level, args.extract_to)




if __name__=='__main__':
    main()
