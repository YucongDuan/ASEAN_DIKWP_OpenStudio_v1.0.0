#!/usr/bin/env python3
"""Start the local studio or provision a teacher. Requires Python 3.10+."""
import argparse, getpass, os
from app.server import Application, Store, APIError, ROOT

def main():
    parser=argparse.ArgumentParser(description='DIKWP OpenStudio')
    parser.add_argument('command',nargs='?',default='serve',choices=['serve','create-teacher'])
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--username')
    args=parser.parse_args()
    if args.command=='create-teacher':
        username=args.username or input('Teacher username: ')
        password=getpass.getpass('Password (at least 10 characters): ')
        confirm=getpass.getpass('Confirm password: ')
        if password!=confirm:parser.error('Passwords do not match')
        try:user=Store(os.environ.get('OPENSTUDIO_DB',str(ROOT/'instance/studio.sqlite3'))).create_user(username,password,'teacher')
        except APIError as ex:parser.error(ex.message)
        print('Teacher created:',user['username']);return
    from wsgiref.simple_server import make_server,WSGIServer
    from socketserver import ThreadingMixIn
    class Server(ThreadingMixIn,WSGIServer):daemon_threads=True
    origin=f'http://127.0.0.1:{args.port}'
    app=Application(public_origin=origin)
    print(f'\nDIKWP OpenStudio → {origin}\nCtrl+C stops the local service.\n',flush=True)
    with make_server('127.0.0.1',args.port,app,server_class=Server) as server:
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
