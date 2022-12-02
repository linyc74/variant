import argparse
from typing import List, Dict
from src import filtering, picking


__VERSION__ = '1.0.0-beta'


PROG = 'python variant'
DESCRIPTION = f'CLI tools for variant calling pipeline (version {__VERSION__}) by Yu-Cheng Lin (ylin@nycu.edu.tw)'


# mode
FILTERING = 'filtering'
PICKING = 'picking'


# args
HELP_ARG = {
    'keys': ['-h', '--help'],
    'properties': {
        'action': 'help',
        'help': 'show this help message',
    }
}
VERSION_ARG = {
    'keys': ['-v', '--version'],
    'properties': {
        'action': 'version',
        'version': __VERSION__,
        'help': 'show version',
    }
}
WORKDIR_ARG = {
    'keys': ['-w', '--workdir'],
    'properties': {
        'type': str,
        'required': False,
        'default': './temp',
        'help': 'path to the temporary working directory (default: %(default)s)',
    }
}
MODE_TO_GROUP_TO_ARGS = {
    FILTERING:
        {
            'Required':
                [
                    {
                        'keys': ['-i', '--input-vcf'],
                        'properties': {
                            'type': str,
                            'required': True,
                            'help': 'path to the input vcf(.gz) file',
                        }
                    },
                    {
                        'keys': ['-o', '--output-vcf'],
                        'properties': {
                            'type': str,
                            'required': True,
                            'help': 'path to the output vcf(.gz) file',
                        }
                    },
                ],
            'Optional':
                [
                    {
                        'keys': ['--variant-flagging-criteria'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'comma-separated flagging criteria, e.g. "low_depth: DP<20, mid_qual: 20<=MQ<=40, high_af: AF>0.02" (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--variant-removal-flags'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'comma-separated flags for variant removal, e.g. "panel_of_normals,map_qual" (default: %(default)s)',
                        }
                    },
                    WORKDIR_ARG,
                    HELP_ARG,
                    VERSION_ARG,
                ],
        },
    PICKING:
        {
            'Required':
                [
                    {
                        'keys': ['-r', '--ref-fa'],
                        'properties': {
                            'type': str,
                            'required': True,
                            'help': 'path to the reference genome fasta file',
                        }
                    },
                    {
                        'keys': ['-o', '--output-vcf'],
                        'properties': {
                            'type': str,
                            'required': True,
                            'help': 'path to the output vcf(.gz) file',
                        }
                    },
                ],
            'Optional':
                [
                    {
                        'keys': ['--mutect2'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the mutect2 vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--haplotype-caller'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the haplotype-caller vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--muse'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the muse vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--varscan'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the varscan vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--lofreq'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the lofreq vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--vardict'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the vardict vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--somatic-sniper'],
                        'properties': {
                            'type': str,
                            'required': False,
                            'default': 'None',
                            'help': 'path to the somatic-sniper vcf(.gz) file (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--min-snv-callers'],
                        'properties': {
                            'type': int,
                            'required': False,
                            'default': 1,
                            'help': 'min number of variant callers for an SNV to be picked (default: %(default)s)',
                        }
                    },
                    {
                        'keys': ['--min-indel-callers'],
                        'properties': {
                            'type': int,
                            'required': False,
                            'default': 1,
                            'help': 'min number of variant callers for an indel to be picked (default: %(default)s)',
                        }
                    },
                    WORKDIR_ARG,
                    HELP_ARG,
                    VERSION_ARG,
                ],
        },
}


class EntryPoint:

    root_parser: argparse.ArgumentParser
    filtering_parser: argparse.ArgumentParser
    picking_parser: argparse.ArgumentParser

    def main(self):
        self.set_parsers()
        self.add_root_parser_args()
        self.add_filtering_parser_args()
        self.add_picking_parser_args()
        self.run()

    def set_parsers(self):
        self.root_parser = argparse.ArgumentParser(
            prog=PROG,
            description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False)

        subparsers = self.root_parser.add_subparsers(
            title='commands',
            dest='mode'
        )

        self.filtering_parser = subparsers.add_parser(
            prog=f'{PROG} {FILTERING}',
            name=FILTERING,
            description=f'{DESCRIPTION} - {FILTERING} mode',
            add_help=False)

        self.picking_parser = subparsers.add_parser(
            prog=f'{PROG} {PICKING}',
            name=PICKING,
            description=f'{DESCRIPTION} - {PICKING} mode',
            add_help=False)

    def add_root_parser_args(self):
        for arg in [HELP_ARG, VERSION_ARG]:
            self.root_parser.add_argument(*arg['keys'], **arg['properties'])

    def add_filtering_parser_args(self):
        self.__add_arguments(
            parser=self.filtering_parser,
            required_args=MODE_TO_GROUP_TO_ARGS[FILTERING]['Required'],
            optional_args=MODE_TO_GROUP_TO_ARGS[FILTERING]['Optional']
        )

    def add_picking_parser_args(self):
        self.__add_arguments(
            parser=self.picking_parser,
            required_args=MODE_TO_GROUP_TO_ARGS[PICKING]['Required'],
            optional_args=MODE_TO_GROUP_TO_ARGS[PICKING]['Optional']
        )

    def __add_arguments(
            self,
            parser: argparse.ArgumentParser,
            required_args: List[Dict],
            optional_args: List[Dict]):

        group = parser.add_argument_group(f'Required')
        for arg in required_args:
            group.add_argument(*arg['keys'], **arg['properties'])

        group = parser.add_argument_group(f'Optional')
        for arg in optional_args:
            group.add_argument(*arg['keys'], **arg['properties'])

    def run(self):
        args = self.root_parser.parse_args()

        if args.mode is None:
            self.root_parser.print_help()

        elif args.mode == FILTERING:
            print(f'Start running variant {FILTERING} {__VERSION__}\n', flush=True)
            filtering(
                input_vcf=args.input_vcf,
                output_vcf=args.output_vcf,
                variant_flagging_criteria=args.variant_flagging_criteria,
                variant_removal_flags=args.variant_removal_flags,
                workdir=args.workdir)

        elif args.mode == PICKING:
            print(f'Start running variant {PICKING} {__VERSION__}\n', flush=True)
            picking(
                ref_fa=args.ref_fa,
                output_vcf=args.output_vcf,
                mutect2=args.mutect2,
                haplotype_caller=args.haplotype_caller,
                muse=args.muse,
                lofreq=args.lofreq,
                varscan=args.varscan,
                vardict=args.vardict,
                somatic_sniper=args.somatic_sniper,
                min_snv_callers=args.min_snv_callers,
                min_indel_callers=args.min_indel_callers,
                workdir=args.workdir)


if __name__ == '__main__':
    EntryPoint().main()