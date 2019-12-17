# comic-dl
    A command line based comic book downloader

### requirements
    - Google Chrome
    - >=python3.5

### installation
    pip3 install comicdl

### commands

- `comic-dl add -q="<query>" | -l="<link>"`

    The add command is used to add comics to a watchlist where comics are specially identified by an alias
    - You can add comics by searching for them with`-q` or
    - Adding their link directly with `-l`

- `comic-dl watched`

    Displays a list of all comics on watchlist, their aliases and last downloaded issues

- `comic-dl download <alias> -i=<n> | -a=<n> | -r=<n>-<m> | --all`

    Downloads comic issues specified for a comic series specified by an alias
    - the `-i` flag can be used to specify a particular issue, a number is expected.
    - the `-a` flag can be used to specify a particular annual, a number is expected.
    - the `-r` flag can be used to specify a range of issues, a string of form n-m
    is expected with no whitespaces in between the hyphen and numbers.
    - the `--all` flag can be used to specify all issues available.

- `comic-dl issues <alias>`

    Lists available issues for a particular comic series specified by alias

- `comic-dl updates`

    Lists all available issues that have not been download for all comics