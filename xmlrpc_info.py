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
ids = sock.execute(database, user_id, password, 'notebook.notebook','search',1, [])
print ids