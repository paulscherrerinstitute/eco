
def main():
    import argparse
    parser = argparse.ArgumentParser(description='eco startup utility')

    parser.add_argument(
            '-s', '--scope', type=str, default=None,
            help='scope name, usually instrument or beamline')
    parser.add_argument(
            '--shell', type=bool, default=True,
            help='open eco in ipython shell')

    arguments = parser.parse_args()

    scope = arguments.scope
    #scope = 'bernina'

    if scope:
        #import importlib
        #eco = importlib.import_module('eco')
        #mdl = importlib.import_module(scope,package=eco)
        #mdl = importlib.import_module('eco.bernina')
        exec(f'from eco.{scope} import *')
        # is there an __all__?  if so respect it
        #if "__all__" in mdl.__dict__:
        #    names = mdl.__dict__["__all__"]
        #else:
            # otherwise we import all names that don't begin with _
        #    names = [x for x in mdl.__dict__ if not x.startswith("_")]
        # now drag them in
        #globals().update({k: getattr(mdl, k) for k in names})

    if arguments.shell:
        from IPython import embed
        embed()

if __name__ == "__main__":
    main()
