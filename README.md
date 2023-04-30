# GameQA-Localization

This project contains the localization script for [GameQA](https://www.gameqa.app) and will provide you with the codebases for the GameQA API and mobile app localized in your language of choice. If you haven't already, please refer to the [localization tutorial](https://gameqa.app/#/) for full instructions on how to deploy the localized app and API.

## Usage

In the ```GameQA``` directory, you will find a subdirectory ```repl``` that contains three ```.csv``` files:

1. ```repl_text.csv```
2. ```repl_emoji.csv```
3. ```repl_values.csv```

These files contain itemized lists of code components for GameQA that need to be translated into your language of choice. They have a handful of columns including:
- ```english```: The English translation of the code components
- ```context```: Text providing a description of context for the components to help with translations
- ```type```: The type of the components such as buttons, errors, texts, titles, etc.
- **```translation```:** **You fill this column with the appropriate translation**

### Translating text, emojis, and other values

The first step to translate all text in the GameQA repo is to translate every single row. We recommend doing this on copies of the following google sheets:
1. [repl_text]()
2. [repl_emoji]()
3. [repl_values]()

Once finished, you can download each of your copies as separate ```.csv``` files and replacing the ones present in ```GameQA/repl/``` correspondingly.

**Note:** Make sure you name the files the same as the the originals!

### Running the localization script

From the ```GameQA``` directory, run:
```
$ sh localize.sh
```

This script will first test your *repl* files for completion and correctness. Only if your files pass the test will the corresponding translation be run.

### After successful translation

Upon successful completion (no failure messages) you should see a new directory ```GameQA/Localized_App``` containing the localized code for both ```app``` and ```api```.

You are now ready to deploy the API and the app. **We recommend that you start with [Setting Up the API](https://www.gameqa.app/#/api-setup/introduction.md) since the App depends on it!**