param ( [string] $file_path )

Remove-Item ./Shop/solidity/output -Recurse -ErrorAction Ignore
docker run -v ${PWD}/Shop/solidity:/sources ethereum/solc:0.8.18 -o /sources/output --abi --bin /sources/$file_path
