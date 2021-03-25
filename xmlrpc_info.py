import xmlrpclib

database = "tongweiqing"
username = "admin"
password = "admin"
url1="http://192.168.109.5:8069/xmlrpc/common"
url2="http://192.168.109.5:8069/xmlrpc/object"
sock_common = xmlrpclib.ServerProxy(url1)
user_id = sock_common.login( database, username, password )
print user_id
sock = xmlrpclib.ServerProxy(url2)
ids = sock.execute(database, user_id, password, 'notebook.notebook','search',[('title','=','tongweiqing01')], [])
print ids
data  = {
        "title":"rpc tongweiqing",
        "content":"rpc tongweiqing"
    }
ret = sock.execute(database, user_id, password, 'notebook.notebook','write',[2],data)
print ret
data2  = {
        "title":"rpc test",
        "content":"rpc test"
    }
ret = sock.execute(database, user_id, password, 'notebook.notebook','create',data2)
print ret