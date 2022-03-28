function downloadGolang() {
  echo -e "\033[36m ⌛ detecting system..."
  arch=$(uname -m)
  if [ "$arch" == "x86_64" ]; then
    echo -e "\033[32m OK ✓"
    echo -e "\033[36m ⌛ downloading golang..."
    cd /tmp
    wget https://go.dev/dl/go1.18.linux-amd64.tar.gz
    echo -e "\033[32m golang downloaded ✓"
    echo -e "\033[36m ⌛ extracting golang..."
    sudo tar -C /usr/local/ -xzf go1.18.linux-amd64.tar.gz
    mkdir /usr/lib/go
    export GOROOT=/usr/local/go
    export GOPATH=$HOME/go
    export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
    source ~/.bashrc
    echo -e "\033[32m golang installed ✓"
    echo -e "\033[33m reboot required "
    return 0
  else
    echo -e "\033[31m [ERROR]: detecting system failed ✕\n install golang manually"
  fi
}

function checkGolang() {
    PKG=$(go version | grep go)
    echo -e "\033[36m Checking..."
    if [ -n "$PKG" ]; then
        echo -e "\033[32m installed ✓"
    else
        downloadGolang
    fi
}

python3.8 -V || apt install python3.8
checkGolang

echo "Package installing..."
echo -n "HTTProuter " & go get github.com/julienschmidt/httprouter && echo "success!" || echo "FAIL!"
echo -n "Pudge " & go get github.com/recoilme/pudge && echo "success!" || echo "FAIL!"
echo -n "Colorizer " & go get github.com/JennieSex/colorizer && echo "success!" || echo "FAIL!"
echo -n "Mutagen " & python3.8 -m pip install mutagen && echo "success!" || echo "FAIL!"
echo -n "Telethon " & python3.8 -m pip install telethon && echo "success!" || echo "FAIL!"
echo -n "Requests " & python3.8 -m pip install requests && echo "success!" || echo "FAIL!"
echo -n "AIOhttp " & python3.8 -m pip install aiohttp && echo "success!" || echo "FAIL!"

chmod +x compile.sh

echo "Compiling binaries..."
./compile.sh

chmod +x start.sh
echo "Done!"
