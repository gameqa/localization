import json
import re
import pymongo
import os
import utils
import argparse

CONFIG_JSON = "./localizeconfig.json"
MODEL_DIR = "models"

config = None
client = None
db = None


def init():
    
    global client
    global db
    global config 
    
    
    with open(CONFIG_JSON, 'r') as f:
        config = json.load(f)
    
    assert "apiEnvVars" in config, "'apiEnvVars' object missing from config file"
    assert "MONGODB_URI" in config['apiEnvVars'], "'MONGODB_URI' object missing from apiEnvVars in config"
    
    
    mongo_uri = config['apiEnvVars']['MONGODB_URI']
    
    client = pymongo.MongoClient(mongo_uri)
    db = client['test']


def pipeline_step(positive_msg, negative_msg):
    def f(g):
        def wrapper(*args, **kwargs):
            try:
                g(*args, **kwargs)
                print(f"✅ {positive_msg}")
            except Exception as e:
                print(f"❌ {negative_msg}. Error received: '{e}'")
                raise Exception("Go to next one")
        return wrapper
    return f

def display_name_to_scraper_name(display_name):
    return display_name.lower().capitalize() + "Scraper"


class UserPrompt:

    @staticmethod
    def __format(prompt):
        return f"\t - {prompt}"

    @staticmethod
    def print(prompt):
        print(UserPrompt.__format(prompt))

    @staticmethod
    def yes_no(prompt):
        inp = input(UserPrompt.__format(f"{prompt}[y/n] "))
        cleaned = inp.lower().strip()
        YES = 'y'
        return cleaned == YES


class Verifier:

    @pipeline_step("Verified the format", "Incorrect format")
    @staticmethod
    def source_format(source):
        assert 'displayName' in source, "Source is missing key called 'displayName'"
        assert 'identifier' in source, "Source is missing key called ''identifier"
        assert 'logo' in source, "Source is missing key called ''logo"
        assert 'hostname' in source, "Source is missing key called ''hostname"
        assert 'domains' in source, "Source should have domains 'domains'"
        assert type(source['domains']
                    ) is list, "Domains should be a list/array"
        for domain in source['domains']:
            assert 'domain' in domain, "domain has a missing 'domain' key"
            assert 'regex' in domain, "domain has a missing 'regex' key"
            assert 'exampleUrl' in domain, "domain should have 'exampleUrl' key"

    @pipeline_step("All regex patterns are valid for the source", "There is a regex pattern that is not valid")
    @staticmethod
    def regex_and_domains(source):
        for domain in source['domains']:
            pattern = re.compile(domain['regex'])
            example_url = domain['exampleUrl']
            match = pattern.search(example_url)
            assert match is not None, f"No match found for regerx '{domain['regex']} in URL {domain['exampleUrl']}'"

            matched_substring = example_url[match.start():match.end()]
            wants_to_continue = UserPrompt.yes_no(
                f"We matched '{matched_substring}' in the string based on the regex. Is this correct?"
            )
            assert wants_to_continue, "We won't continue with this source since the regex match was incorrect"

    @pipeline_step("Name checks passed", "Name check not passed")
    @staticmethod
    def name(source):
        pattern = r'^[a-zA-Z_$][a-zA-Z0-9_$]*$'
        assert bool(re.match(
            pattern, source['displayName'])), "Display name for source MUST be a valid variable name in Javascript"


class Upserter:

    @pipeline_step("Article source record is up to date in database", "Article source record is NOT up to date in database")
    @staticmethod
    def database_record(source):
        id = source['identifier']
        filter_query = {"identifier": id}
        doc = db.articlesources.find_one(filter_query)

        keys = ["identifier", "displayName", "hostname", "logo"]
        if not doc:
            UserPrompt.print(
                f"Source with identifier '{id}' does not exist. Writing it to database")
            db.articlesources.insert_one({
                key: source[key] for key in keys
            })
        else:
            diffs = [key for key in keys if doc[key] != source[key]]

            if len(diffs) == 0:
                return

            UserPrompt.print(
                "There are changes in the config json for this source")
            for diff_key in diffs:
                UserPrompt.print(
                    f"The key '{diff_key}' for the source has been changed from '{doc[diff_key]}' to '{source[diff_key]}'")

            wants_to_continue = UserPrompt.yes_no(
                f"Do you want to update?"
            )

            assert wants_to_continue, "You decided not to update the information for this article source"

            update_query = {
                '$set': {
                    key: source[key] for key in diffs
                }
            }

            # Update the document
            result = db.articlesources.update_one(filter_query, update_query)

            # Check if the update was successful
            if result.modified_count != 1:
                raise Exception("Document not found or no updates were made")

    @pipeline_step("Scraper created", "Scraper not created")
    @staticmethod
    def scraper_code(source):
        scaper_name = display_name_to_scraper_name(source['displayName'])

        scraper_dir = os.path.join(
            MODEL_DIR, f"Articles/ScrapingService/{scaper_name}")
        scraper_file = os.path.join(scraper_dir, "index.ts")
        
        print(scraper_dir)
        print(scraper_file)

        if not os.path.exists(scraper_dir):
            UserPrompt.print(
                f"Directory for {scaper_name} does not exist, creating {scraper_dir}")
            os.system(f"mkdir {scraper_dir}")
            
        if not os.path.exists(scraper_dir):
            print("Foo")


        if not os.path.exists(scraper_file):
            UserPrompt.print(
                f"Index file for for {scaper_name} does not exist, creating {scraper_file}")
            f = open(scraper_file, "w")
            f.write(utils.get_new_scraper_code_boilerplate(scaper_name))
            f.close()
            
        


class Pipeline:
    
    def __init__(self, steps):
        self.steps = steps

    def run(self, *args, **kwargs):
        for fn in self.steps:
            fn(*args, **kwargs)


class CodeGen:

    @staticmethod
    def replace_var(file_name, var_name, start_of, end_of, replacement):
        # Read the file content
        with open(file_name, 'r') as file:
            content = file.read()

        # Find the start and end positions of the mapHostToArticleSourceIdentifier object
        start = content.find(start_of, content.index(var_name)) + len(start_of)
        end   = content.find(end_of, start)

        with open(file_name, "w") as file:
            file.write(content[:start] + replacement + content[end:])
        UserPrompt.print(f"UPDATED {var_name}")
            

    @staticmethod
    def handle_map_host_to_article_source_identifier(codegen_recipes):
        file_name = os.path.join(MODEL_DIR, "ArticleSources/utils.ts")
        replacement = "\n" + "".join([f'\t"{_["domain"]}": "{_["identifier"]}",\n' for _ in codegen_recipes])
        CodeGen.replace_var(
            file_name,
            "mapHostToArticleSourceIdentifier",
            "= {",
            "};",
            replacement
        )

    @staticmethod
    def handle_map_article_source_identifier_to_regex(codegen_recipes):
        file_name = os.path.join(MODEL_DIR, "ArticleSources/utils.ts")
        
        identifier_to_regex = {_['identifier']: _['regex'] for _ in codegen_recipes}
        
        replacement = "\n" + "".join([f'\t"{key}": /{val}/g,\n' for key, val in identifier_to_regex.items()])
        CodeGen.replace_var(
            file_name,
            "mapArticleSourceIdentifierToArticleKeyRegex",
            "= {",
            "};",
            replacement
        )


    @staticmethod
    def handle_article_source_identifier(codegen_recipes):
        identifiers = set([_['identifier'] for _ in codegen_recipes])
        replacement = "\n" + "\n".join(["\t| " + f"\"{_}\"" for _ in  identifiers])
        file_name = os.path.join(MODEL_DIR, "ArticleSources/interface.ts")
        CodeGen.replace_var(
            file_name,
            "ArticleSourceIdentifier",
            "=",
            ";",
            replacement
        )

    @staticmethod
    def handle_article_hostnames(codegen_recipes):
        replacement = "\n" + "\n".join(["\t| " + f"\"{_['domain']}\"" for _ in  codegen_recipes])
        file_name = os.path.join(MODEL_DIR, "ArticleSources/interface.ts")
        CodeGen.replace_var(
            file_name,
            "ArticleHostnames",
            "=",
            ";",
            replacement
        )
        
    @staticmethod
    def handle_scaper_factory(codegen_recipes):
        tuples = set(
            (_['identifier'], _['display_name'])
            for _ in codegen_recipes
        )

        file_name = os.path.join(MODEL_DIR, "Articles/ScrapingService/ScrapingFactory/index.ts")

        # replace cases
        cases = []
        for id, name in tuples:
            class_name = display_name_to_scraper_name(name)
            txt = "\n" + f"\t\t\tcase \"{id}\":\n\t\t\t\tthis.instance = new {class_name}(sourceArticleKey);\n\t\t\t\tbreak;";
            cases.append(txt);
        
        replacement = "\n".join(cases);
        
        CodeGen.replace_var(
            file_name,
            "ScraperFactory",
            "switch (source) {",
            "default:",
            replacement
        )
        
        # replace imports
        imports = []
        for id, name in tuples:
            class_name = display_name_to_scraper_name(name)
            imports.append(f"import {class_name} from \"../{class_name}\";")
        
        replacement = "\n" + "\n".join(imports) + "\n\n"

        CodeGen.replace_var(
            file_name,
            "import",
            "\"./interface\";",
            "export class",
            replacement
        )
                


if __name__ == "__main__":

    init()

    f = open(CONFIG_JSON, "r")
    config = json.load(f)

    assert "sources" in config, "config must include key 'sources'"
    assert type(config['sources']) == list, "'sources' in config must be an array"

    sources = config['sources']
    codegen_recipes = []
    
    verification_pipeline = Pipeline([
        Verifier.source_format,
        Verifier.regex_and_domains,
        Verifier.name,
        Upserter.database_record,
        Upserter.scraper_code
    ])
    
    code_gen_pipeline = Pipeline([
        CodeGen.handle_map_host_to_article_source_identifier,
        CodeGen.handle_map_article_source_identifier_to_regex,
        CodeGen.handle_article_hostnames,
        CodeGen.handle_article_source_identifier,
        CodeGen.handle_scaper_factory
    ])
    
    for i, source in enumerate(sources):
        print(f"[{i + 1}/{len(sources)}] Reviewing source")
        try:
            verification_pipeline.run(source)
            # if source passes all checks then we perform codegen tasks
            for domain_obj in source['domains']:
                codegen_recipes.append({
                    'display_name': source['displayName'],
                    'domain': domain_obj['domain'],
                    'identifier': source['identifier'],
                    'regex': domain_obj['regex']
                })
        except:
            pass

    print(f"\nVerification done for {len(sources)} sources. {len(codegen_recipes)} passed all checks.\n")

    print("\nRunning codegen script to add variables, types, and mappings for sources that passed all checks.\n")
    code_gen_pipeline.run(codegen_recipes)
    
    print("\n✅ Adding sources completed!")
    print("\n❗  NOTE: You must update the 'include' and 'exclude' lists in the Programmable Search Engine UI.")
    
