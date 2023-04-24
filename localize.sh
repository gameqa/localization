rm -rf localized-app
mkdir -p localized-app

pip3 install -r requirements.txt

cd localized-app

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

# pre-localization check.
echo ""
echo "[CHECKING REPL SHEETS FOR CORRECTNESS...]"
python3 scripts/check_repl_sheet.py

echo ""
echo "[TRANSLATING THE APP AND API...]"
python3 scripts/localization_text.py --key key --repl translation --repl_file repl/repl_text.csv --dir localized-app -v
python3 scripts/localization_emoji.py --key key --repl translation --repl_file repl/repl_emoji.csv --dir localized-app -v
python3 scripts/localization_values.py --key english --repl translation --repl_file repl/repl_values.csv --dir localized-app -v

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

#TODO:  Post-localization script.
