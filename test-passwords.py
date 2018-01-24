import paramiko
import logging
logging.getLogger("paramiko").setLevel(logging.ERROR)

WAIT_TIME=60

def test_passwords(host, passwords, gw_host=None, gw_passwd=None):
    """Test a list of passwords to connect to a host, using a gateway or not.

        Keyword arguments:
        host -- host string to connect (fomart: username@hostname[:port]), default port is 22
        passwords -- list of strings of passwords to try on
        gw_host -- gateway host string (format: username@hostname[:port]), default port is 22
        gw_passwd -- string of gateway host's password

        If no gw_host or gw_passwd is specified, don't try to use a gateway to connect to the host
    """
    username = host.split('@')[0]
    if len(host.split('@')[1].split(':')) == 2:
        dest = host.split('@')[1].split(':')[0]
        port = int(host.split('@')[1].split(':')[1])
    else:
        dest = host.split('@')[1]
        port = 22

    vm = None
    vmchannel = None
    if gw_host and gw_passwd:
        gw_username = gw_host.split('@')[0]
        if len(gw_host.split('@')[1].split(':')) == 2:
            gw_dest = gw_host.split('@')[1].split(':')[0]
            gw_port = int(gw_host.split('@')[1].split(':')[1])
        else:
            gw_dest = gw_host.split('@')[1]
            gw_port = 22

        vm = paramiko.SSHClient()
        vm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        vm.connect(gw_dest, port=gw_port, username=gw_username, password=gw_passwd, auth_timeout=WAIT_TIME)
        vmtransport = vm.get_transport()
        vmchannel = vmtransport.open_channel("direct-tcpip", (dest, port), (gw_dest, gw_port))

    line = f'{host} ---> ??????'
    for password in passwords:
        try:
            jhost = paramiko.SSHClient()
            jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            jhost.connect(dest, port=port, username=username, password=password, sock=vmchannel, auth_timeout=WAIT_TIME)
            jhost.close()
            line = f'{host} ---> {password}'
            break
        except Exception:
            continue
    print (line)
    if vm:
        vm.close()
