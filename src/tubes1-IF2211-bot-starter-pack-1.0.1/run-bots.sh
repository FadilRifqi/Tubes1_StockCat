#!/bin/bash

python main.py --logic StockCat --email=stockcat@email.com --name=stockcat --password=123456 --team etimo &
python main.py --logic Random --email=test1@email.com --name=stima1 --password=123456 --team etimo &
python main.py --logic Random --email=test2@email.com --name=stima2 --password=123456 --team etimo &
python main.py --logic Random --email=test3@email.com --name=stima3 --password=123456 --team etimo &
