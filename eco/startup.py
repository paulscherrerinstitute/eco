
def main():
    import argparse
    parser = argparse.ArgumentParser(description='eco startup utility')

    parser.add_argument(
            '-s', '--scope', type=str, default=None,
            help='scope name, usually instrument or beamline')
    parser.add_argument(
            '--shell', type=bool, default=True,
            help='open eco in ipython shell')
    parser.add_argument(
            '--pylab', type=bool, default=True,
            help='open ipython shell in pylab mode')

    arguments = parser.parse_args()

    scope = arguments.scope
    #scope = 'bernina'

    print('                       ___ _______\n                      / -_) __/ _ \ \n Experiment Control   \__/\__/\___/ \n\n')
    if scope:
        #import importlib
        #eco = importlib.import_module('eco')
        #mdl = importlib.import_module(scope,package=eco)
        #mdl = importlib.import_module('eco.bernina')
        exec(f'from eco.{scope} import *')
        exec(f'import eco.{scope} as {scope}')
        # is there an __all__?  if so respect it
        #if "__all__" in mdl.__dict__:
        #    names = mdl.__dict__["__all__"]
        #else:
        # otherwise we import all names that don't begin with _
        #    names = [x for x in mdl.__dict__ if not x.startswith("_")]
        # now drag them in
        #globals().update({k: getattr(mdl, k) for k in names})

    if arguments.shell:
        if arguments.pylab:
            import matplotlib.pyplot as plt
            from IPython.terminal.embed import InteractiveShellEmbed
            shell = InteractiveShellEmbed()
            shell.enable_matplotlib()
            shell()
        else:
            from IPython import embed
            embed()

if __name__ == "__main__":
    main()
