VER=$1

. ./clean.sh

svn checkout --username=seccanj svn+ssh://seccanj@svn.code.sf.net/p/testman4trac/code/ testman4trac.$VER.SVN
cd testman4trac.$VER.SVN
cp -R ../testman4trac.$VER/* .
svn status
svn add
#svn commit

cd ..

hg clone https://seccanj@bitbucket.org/olemis/testman4trac testman4trac.$VER.BITBKT
cd testman4trac.$VER.BITBKT
cp -R ../testman4trac.$VER/* .
hg status
hg add
#hg commit
#hg push

cd ..
#rm -rf testman4trac.$VER testman4trac.$VER.SVN testman4trac.$VER.BITBKT
