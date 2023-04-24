import re
from tabulate import tabulate
from collections import defaultdict
from termcolor import colored

import pandas as pd
import numpy as np

REPL_TEXT_FILE = "repl/repl_text.csv"
REPL_EMOJI_FILE = "repl/repl_emoji.csv"
REPL_VALUES_FILE = "repl/repl_values.csv"

class ReplChecker:
    
    def __init__(self, file_name):
        '''
        
        '''
        self.scorecard = []
        self.file_name = file_name
        if "text" in file_name:
            self.type = "text"
        elif "emoji" in file_name:
            self.type = "emoji"
        elif "values" in file_name:
            self.type = "values"
            
        self.df = pd.read_csv(self.file_name)
        
    def populate_checks(self, test_name, test_result, test_note):
        '''
        
        '''
        self.scorecard.append([test_name, test_result, test_note])
    
    def show(self):
        '''
        
        '''
        print(f"\n{self.type.upper()} RESULTS:\n")
        print(tabulate(self.scorecard, headers=["Test", "Result", "Notes"]))
        print()
    
    def check_all(self):
        self.check_translation_completion()
        self.check_formatted_strings()
        self.check_double_quotes()
    
    def check_double_quotes(self):
        test_name = "Double Quotes"
        double_quotes_count = 0
        
        for i in range(self.df.index.size):
            translation = self.df["translation"][i]
            if type(translation) != str and np.isnan(translation):
                continue
            if '"' in translation:
                double_quotes_count += translation.count('"')
        
        test_note = f"{double_quotes_count} Double Quotes Found."
        
        if double_quotes_count == 0:
            test_result = "PASS"
        
        else:
            test_result = "FAIL"
        
        self.populate_checks(test_name=test_name, test_result=test_result, test_note=test_note)
    
    def check_translation_completion(self):
        '''
        
        '''
        test_name = "Translation Completion"
        nan_count = self.df["translation"].isnull().sum()
        test_note = f"{nan_count} incomplete translations"
        if nan_count > 0:
            test_result = "FAIL"
        
        else:
            test_result = "PASS"
        
        self.populate_checks(test_name=test_name, test_result=test_result, test_note=test_note)
    

    def check_formatted_strings(self):
        '''
        
        '''
        test_name = "Formatted Strings like ${.*}"
        regex_pattern = r"(\${.*?})"
        
        matched_formats = 0
        unmatched_formats = 0
        
        for i in range(self.df.index.size):
                
            english = self.df["english"][i]
            translation = self.df["translation"][i]
            
            english_formats = re.search(regex_pattern, english)
            english_format_counts = defaultdict(lambda: 0)
            
            if english_formats is not None:
                for j in range(len(english_formats.groups())):
                    match = english_formats.group(j)
                    english_format_counts[match] += 1
                
                if type(translation) != str and np.isnan(translation):
                    unmatched_formats += len(english_formats.groups())
                
                else:    
                    translation_formats = re.search(regex_pattern, translation)
                    if translation_formats is None:
                        unmatched_formats += len(english_formats.groups())
                    
                    else:
                        for j in range(len(translation_formats.groups())):
                            match = translation_formats.group(j)
                            if english_format_counts[match] > 0:
                                matched_formats += 1
                                english_format_counts[match] -= 1
                            
                            else:
                                unmatched_formats += 1
        
        test_note = f"{matched_formats} MATCHED string formats and {unmatched_formats} UNMATHCED string formats"
        
        if unmatched_formats == 0:
            test_result = "PASS"
        
        else:
            test_result = "FAIL"
        
        self.populate_checks(test_name=test_name, test_result=test_result, test_note=test_note)
    
    def save_check_results(self):
        '''
        
        '''
        save_df = pd.DataFrame(data = self.scorecard, columns=["Test", "Result", "Notes"])
        save_df.to_csv(f"{self.type}_scorecard.csv", index=False)
        
        result = list(save_df["Result"])
        
        if "FAIL" in result:
            text = colored(f"[FAIL] {self.file_name} failed one more more of the above tests. The localization script will not be run for {self.type}. \nPlease fix the repl sheet and try again.", 'red', attrs=['reverse'])
            print(text)

if __name__ == "__main__":
    
    text_checker = ReplChecker(REPL_TEXT_FILE)
    emoji_checker = ReplChecker(REPL_EMOJI_FILE)
    values_checker = ReplChecker(REPL_VALUES_FILE)
    
    text_checker.check_all()
    text_checker.show()
    text_checker.save_check_results()
    
    emoji_checker.check_all()
    emoji_checker.show()
    emoji_checker.save_check_results()
    
    values_checker.check_all()
    values_checker.show()
    values_checker.save_check_results()
    
    
    
    
            