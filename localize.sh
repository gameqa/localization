rm -rf Localized_App
mkdir -p Localized_App

pip3 install -r requirements.txt

cd Localized_App

git clone https://github.com/cadia-lvl/qa-crowdsourcing-app.git
git clone https://github.com/cadia-lvl/qa-crowdsourcing-api.git

cd qa-crowdsourcing-app 
git checkout localize
rm -r -f .git && cd ..

cd qa-crowdsourcing-api 
git checkout localization
rm -r -f .git && cd ..

mv qa-crowdsourcing-app app
mv qa-crowdsourcing-api api

cd ..

# TODO:
# pre-localization check.
echo ""
echo "[CHECKING REPL SHEETS FOR CORRECTNESS...]"
python3 scripts/check_repl_sheet.py

echo ""
echo "[TRANSLATING THE APP AND API...]"
python3 scripts/localization_text.py --key key --repl translation --repl_file repl/repl_text.csv --dir Localized_App -v
python3 scripts/localization_emoji.py --key key --repl translation --repl_file repl/repl_emoji.csv --dir Localized_App -v
python3 scripts/localization_values.py --key english --repl translation --repl_file repl/repl_values.csv --dir Localized_App -v

echo ""
echo "[TRANSLATING THE SENDGRID TEMPLATES...]"
python3 scripts/localization_text.py --key key --repl translation --repl_file repl/repl_text.csv --dir sendgrid_templates -v
python3 scripts/localization_emoji.py --key key --repl translation --repl_file repl/repl_emoji.csv --dir sendgrid_templates -v
python3 scripts/localization_values.py --key english --repl translation --repl_file repl/repl_values.csv --dir sendgrid_templates -v

echo ""
echo "[REMOVING SCORECARDS...]"
rm text_scorecard.csv
rm emoji_scorecard.csv
rm values_scorecard.csv

# python3 localization_text.py --key key --repl translation --repl_file repl_text.csv --dir . -v # TODO: Modify to take jsut one fine as well


#TODO:  Post-localization script.
