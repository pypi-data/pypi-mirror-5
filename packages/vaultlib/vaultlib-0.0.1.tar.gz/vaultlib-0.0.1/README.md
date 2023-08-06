#vaultlib

#EXPERIMENTAL - USE AT YOUR OWN RISK -

Chef style Databag Storage

Supports plain text and encrypted databags.

A data bag is an object with two properties:

* _id
* data

The _\_id_ represent the databag name and _data_ contains the data we want to store in the databag.

##Installation

    ./run-tests
    python setup.py sdist
    pip install ./dist/vaultlib-0.0.1.tar.gz
    
    or 
    
    pip install vaultlib
  

##Features


__Vault__.__Storage__

* add_databag()
* get_databag()
* delete_databag()
* list_databags()

__Vault__.__Databag__

* encrypt()
* decrypt()

__Vault__.__Key__

* from_file()
* from_data()


##Library Usage

### Create encryption key

To encrypt a databag we need a key:

    openssl genrsa -out my_key.pem 4096

### Initialize the Vault

    couchdb_host = '127.0.0.1'
    couchdb_port = 6984
    couchdb_database = 'databags'

    vault = Vault('http', couchdb_host, couchdb_port, couchdb_database)

### Create a databag

    databag_data = {
        "foo": "bar",
        "and": {
            "foo": "bar"
        }
    }

    databag_name = "prefix.name.suffix"
    databag = Databag(databag_name, databag_data)

### Encrypt databag (optional)

    key_file = "mykey.pem"
    pk = Key(filename=key_file).private
    databag.encrypt(pk)

### Store databag in the Vault

    vault.add_databag(databag)

### Retrieve data bag from the vault

    databag_name = "prefix.name.suffix"
    databag = vault.get_databag(databag_name)

    data = databag.data
    id_ = databag.id

### Decrypt databag (optional)

    key_file = "mykey.pem"
    pk = Key(filename=key_file).private
    databag.decrypt(pk)

    data = databag.data
    id_ = databag.id

### List all databags

    for databag in vault.list_databags():
        databag.decrypt("mykey.pem")
        print databag.data
        print databag.id

##Cli Usage

Required environment variables:

    export VAULT_PROTOCOL=http
    export VAULT_HOST='127.0.0.1'
    export VAULT_PORT=5984
    export VAULT_DATABASE='vault'

__Help__

    vault-cli --help
    
    ---
    
    usage: vault-cli [-h] [--databag DATABAG] [--key KEY] [cmd [cmd ...]]

    Manage databags
    
    positional arguments:
      cmd                [add, list, show]
    
    optional arguments:
      -h, --help         show this help message and exit
      --databag DATABAG  specify .json databag
      --key KEY          specify encryption key

__Add databag__

    vault-cli add --databag databag.json
    
    vault-cli add --databag databag.json --key /my/path/key.pem

__List databag__

    vault-cli list

__Show databag__

    vault-cli show databag_name
    
    vault-cli show databag_name --key /my/path/key.pem

__Delete databag__
    
    vault-cli delete databag_name
 


