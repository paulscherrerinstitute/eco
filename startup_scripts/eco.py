import argparse

parser = argparse.ArgumentParser(description='Experiment control startup script')
parser.add_argument('instrument', metavar='inst', type=str, nargs=1,
                   help='import instrument configuration upon startup')

args = parser.parse_args()
