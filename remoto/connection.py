import socket
import sys
import execnet
import logging
# compatibility for older clients that rely on the previous ``Connection`` class
from remoto.backends import BaseConnection as Connection
