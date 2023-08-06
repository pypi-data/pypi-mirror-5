rm -rf bin

cd tracgenericclass
rm -rf build dist *.egg-info

cd ../tracgenericworkflow
rm -rf build dist *.egg-info

cd ../sqlexecutor
rm -rf build dist *.egg-info

cd ../testman4trac
rm -rf build dist *.egg-info
rm -f testmanager/locale/de/LC_MESSAGES/*.mo
rm -f testmanager/locale/es/LC_MESSAGES/*.mo
rm -f testmanager/locale/fr/LC_MESSAGES/*.mo
rm -f testmanager/locale/it/LC_MESSAGES/*.mo
rm -f testmanager/htdocs/js/de.js
rm -f testmanager/htdocs/js/es.js
rm -f testmanager/htdocs/js/fr.js
rm -f testmanager/htdocs/js/it.js

cd ..
