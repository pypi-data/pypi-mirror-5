# Install GMP library.
wget ftp://ftp.gmplib.org/pub/gmp/gmp-5.1.3.tar.bz2
tar -xvf gmp-5.1.3.tar.bz2
cd gmp-5.1.3
./configure
make
sudo make install
cd ..
rm gmp-5.1.3.tar.bz2
rm -rf gmp-5.1.3


# Fixes: /usr/bin/ld: cannot find -ltcmalloc: 
sudo apt-get install libgoogle-perftools-dev

# Fixes: Libtool library used but 'LIBTOOL' is undefined
# sudo apt-get install libtool
# libtoolize


# PBC Dependencies:
#sudo apt-get instal flex
#sudo apt-geit instal bison

# Install pbc.
wget http://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xvf pbc-0.5.14.tar.gz
cd libpbc_0.5.14
./configure
make
sudo make install
cd ..
rm -rf pbc-0.5.14
rm pbc-0.5.14.tar.gz


# Downloads pypbc
wget -O pypbc.tar.gz https://www.gitorious.org/pypbc/pypbc/archive/16f5c2cf8775b8257fd531ce60f44d39a1999641.tar.gz
tar -xvf pypbc.tar.gz
cd pypbc
sudo python3 setup.py install
