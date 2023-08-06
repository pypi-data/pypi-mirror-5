project_path=$1

mkdir bin
mkdir docs

cd tracgenericclass
python setup.py bdist_egg
cp dist/*.egg ../bin

cd ../tracgenericworkflow
python setup.py bdist_egg
cp dist/*.egg ../bin

cd ../sqlexecutor
python setup.py bdist_egg
cp dist/*.egg ../bin

cd ../testman4trac

python setup.py extract_messages
python setup.py extract_messages_js
python ./setup.py update_catalog -l it
python ./setup.py update_catalog_js -l it
python ./setup.py compile_catalog -f -l it
python ./setup.py compile_catalog_js -f -l it
python ./setup.py update_catalog -l es
python ./setup.py update_catalog_js -l es
python ./setup.py compile_catalog -f -l es
python ./setup.py compile_catalog_js -f -l es
python ./setup.py update_catalog -l de
python ./setup.py update_catalog_js -l de
python ./setup.py compile_catalog -f -l de
python ./setup.py compile_catalog_js -f -l de
python ./setup.py update_catalog -l fr
python ./setup.py update_catalog_js -l fr
python ./setup.py compile_catalog -f -l fr
python ./setup.py compile_catalog_js -f -l fr

python setup.py bdist_egg
cp dist/*.egg ../bin

cd ..

cp *.txt docs

cp rpc_example.py bin

if [ $# -eq 1 ]
then
  cp bin/*.egg $project_path/plugins
fi
