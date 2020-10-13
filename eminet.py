
## QV 2020-10-12 runs Eminet to derive B10 and B11 emissivity for L8/TIRS based on L8/OLI spectrum or image
##
## last modification 2020-10-13 (QV) added processing flags

def run_eminet():
    ## import sys to parse arguments
    import sys
    ## for evaluation of bool strings
    import distutils.core
    import eminet as em

    ## ignore numpy errors
    import numpy as np
    olderr = np.seterr(all='ignore')

    import argparse
    parser = argparse.ArgumentParser(description='EMINET')
    parser.add_argument('--input', help='Input spectrum or L2 satellite image')
    parser.add_argument('--output', help='Output directory', default=None)
    parser.add_argument('--use_water_defaults', help='Use default emissivity for liquid water (default=True)', default=True)
    parser.add_argument('--netname', help='Net to use (default=Net2)', default='Net2')

    parser.add_argument('--em_water_b10', help='Water emissivity for B10 (default=0.9926)', default=0.9926)
    parser.add_argument('--em_water_b11', help='Water emissivity for B11 (default=0.9877)', default=0.9877)
    parser.add_argument('--water_threshold', help='Threshold on 1.6 micron TOA reflectance to separate water/non-water (default=0.02)', default=0.02)

    args, unknown = parser.parse_known_args()

    if args.input is None:
        print('No input file given.')
        return(1)

    if type(args.use_water_defaults) == str: args.use_water_defaults = bool(distutils.util.strtobool(args.use_water_defaults))
    if type(args.em_water_b10) == str: args.em_water_b10 = float(args.em_water_b10)
    if type(args.em_water_b11) == str: args.em_water_b11 = float(args.em_water_b11)
    if type(args.water_threshold) == str: args.water_threshold = float(args.water_threshold)

    ## run the processing
    em.eminet_models(args.input,
                    output=args.output,
                    netname=args.netname,
                    use_water_defaults=args.use_water_defaults,
                    ew_b10=args.em_water_b10, ew_b11=args.em_water_b11, water_threshold = args.water_threshold)

if __name__ == '__main__':
    run_eminet()
