import argparse
from pathlib import Path
from tabulate import tabulate
from termcolor import colored

import pandas as pd

class Localizer:
    
    def __init__(self, args):
        self.repl_log = []
        self.total_succeeds = 0 
        self.total_failures = 0
        self.key = args.key
        self.repl = args.repl
        self.args = args
        if args.file is None:
            self.files = list(Path(args.dir).rglob("*.ts")) + list(Path(args.dir).rglob("*.tsx"))
        else:
            self.files = [args.file]
        self.df = self.load_sheet()
        self.repl_dict = self.build_repl_dict()

    def build_repl_dict(self):
        '''
        Builds a disctionary for replacement. 
        Replace keys with values. 
        
        TODO: Check to make sure that there are no double quotes.
        '''
        
        src = self.df[self.key]
        repls = self.df[self.repl]
        
        if self.args.verbose:
            print("building repl dictionary...")
        
        repl_dict = {key: val for key, val in zip(src, repls)}
        
        if self.args.verbose:
            print("Built repl dictionary.")
        
        return repl_dict

    def load_sheet(self):
        '''
        Read sheet as csv and return.
        '''
        
        if self.args.verbose:
            print('loading repl sheet...')
            
        df = pd.read_csv(self.args.repl_file)
        
        if self.args.verbose:
            print('loaded repl sheet')
        
        return df

    def replace_emoji_in_string(self, line):
        '''
        replaces occurances of repl_dict.keys() with values in string and returns it.
        '''
        emoji_count = 0
        for key_emoji, replacement in self.repl_dict.items():
            emoji_count += line.count(key_emoji)
            line = line.replace(key_emoji, replacement)
            
        return line, emoji_count

    def replace_emoji_in_file(self, source_file):
        '''
        Performs replacements in source_file, and writes into target_file.
        Source and target are the same by default, but can be specified to be different.
        '''
        
        if self.args.very_verbose:
            print(f"Replacing text in file: {source_file}...")
        
        file_repl_count = 0
        
        try:
            with open(source_file, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                new_line, keycount = self.replace_emoji_in_string(line)
                new_lines.append(new_line)
                file_repl_count += keycount
            
            if self.args.very_verbose:
                print(f"  Replaced. Writing new text in file: {source_file}")
            
            with open(source_file, 'w') as f:
                f.writelines(new_lines)
            
            log_row = [source_file, file_repl_count]
            if file_repl_count > 0:
                self.total_succeeds += file_repl_count
                self.repl_log.append(log_row)
        
        # TODO: How do you want to handle this?
        except Exception as e:
            print(f"Error with file {source_file}. Skipping.")
            print("========================")
            print("Error Message:")
            print(e)
            print("========================")
            
            log_row = [source_file, "ERROR"]
            self.total_failures += 1
            self.repl_log.append(log_row)

    def replace_emoji_all(self):
        
        for file_path in self.files:
            self.replace_emoji_in_file(file_path)
    
    def show_report(self):
        print(f"\nEMOJI LOCALIZATION RESULT:\n")
        print(tabulate(self.repl_log, headers=["FILE NAME", "Replacement Count"]))
        
        collective_data = []
        collective_data.append(["TOTAL SUCCESSFUL REPLACEMENTS", self.total_succeeds])
        collective_data.append(["TOTAL FAILED FILES", self.total_failures])
        # print("\nAGGREGATION:")
        print()
        print(tabulate(collective_data, headers=["Aggregation", "Count"]))
        print()

def get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--key', type=str, required=True, 
                        help="columns to build keys to replace from")
    
    parser.add_argument('--repl', type=str, required=False, default=None, 
                        help="columns to build values to replace to")
    
    parser.add_argument('--repl_file', type=str, required=True, 
                        help="csv file with replacement information")
    
    parser.add_argument('--dir', type=str, required=False, default='.',
                        help='''This is the directory that the localizer with walk through to make
                        The translations.''')
    
    parser.add_argument('--file', type=str, required=False, default=None,
                        help='''This is the file that the localizer will work with. This overrides --dir.''')
    
    parser.add_argument('--verbose', '-v', default=False, action='store_true',
                        help="Set verbose to print checkopints.")
    
    parser.add_argument('--very_verbose', '-vv', default=False, action='store_true',
                        help="Set very verbose to print more checkpoints.")
    
    args = parser.parse_args()
    
    if args.very_verbose:
        args.verbose = True
        
    if args.verbose:
        print(args)
    
    return args

def check_repl():
    df = pd.read_csv("emoji_scorecard.csv")
    results = list(df["Result"])
    if "FAIL" in results:
        message_log = colored(f"\n[FAIL] Exiting localization_emoji without localization.\n".upper(), 'red') 
        print(message_log)
        exit(1)
    else:
        message_log = colored(f"\n[PASS] Running localization_emoji\n".upper(), 'green')
        print(message_log) 
    
if __name__ == "__main__":
    
    check_repl()
    
    args = get_args()
    if args.file is None:
        print(f"Replacing Emojis from all *.ts[x] files in the directory {args.dir} using {args.repl_file}.")
    
    else:
        print(f"Replacing Emojis from {args.file} using {args.repl_file}.")
    
    localizer = Localizer(args)
    localizer.replace_emoji_all()
    localizer.show_report()