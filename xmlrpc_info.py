import xmlrpclib

database = "tongweiqing"
username = "admin"
password = "admin"
socket = xmlrpclib.ServerProxy( "http://192.168.109.5:8069/xmlrpc/common" )
user_id = socket.login( database, username, password )
print user_id
ids = socket.execute( database, user_id, password, 'notebook.notebook','search', [] )
print ids