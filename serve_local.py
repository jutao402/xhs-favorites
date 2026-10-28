from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import argparse

parser=argparse.ArgumentParser(description="Serve the favorites dashboard on loopback only")
parser.add_argument("--port",type=int,default=8000)
args=parser.parse_args()
folder=Path(__file__).resolve().parent/"dashboard"/"dist"
server=ThreadingHTTPServer(("127.0.0.1",args.port),partial(SimpleHTTPRequestHandler,directory=str(folder)))
print(f"Open http://127.0.0.1:{args.port}/")
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
