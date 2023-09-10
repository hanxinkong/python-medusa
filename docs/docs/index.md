# python-medusa

python-medusa是一个闻名的爆破工具medusa的python库,可以帮助使用medusa进行端口爆破，希望能为使用者带来益处。如果您也想贡献好的代码片段，请将代码以及描述，通过邮箱（ [xinkonghan@gmail.com](mailto:hanxinkong<xinkonghan@gmail.com>)
）发送给我。代码格式是遵循自我主观，如存在不足敬请指出！

----
**文档地址：
** <a href="https://python-medusa.xink.top/" target="_blank">https://python-medusa.xink.top/ </a>

**PyPi地址：
** <a href="https://pypi.org/project/python-medusa" target="_blank">https://pypi.org/project/python-medusa </a>

**GitHub地址：
** [https://github.com/hanxinkong/python-medusa](https://github.com/hanxinkong/python-medusa)

----

## 安装

<div class="termy">

```console
pip install python-medusa
```

</div>

## 支持的协议

* AFP
* CVS
* FTP
* HTTP
* IMAP
* MS-SQL
* MySQL
* NCP (NetWare)
* NNTP
* PcAnywhere
* POP3
* PostgreSQL
* rexec
* rlogin
* rsh
* SMB
* SMTP (AUTH/VRFY)
* SNMP
* SSH
* SSHv2
* Telnet
* VmAuthd
* VNC

## 简单使用

✨在使用之前,请确保已安装`medusa`应用程序

```python
from medusa import PortBlaster

mds = PortBlaster()
print("medusa version:", mds.medusa_version)
mds.brute(
    hosts='192.168.2.185',
    ports='22',
    user='root',
    password='root',
    arguments='-M ssh',
    isfile_hosts=False,
    isfile_user=False,
    isfile_password=False
)
print("medusa command line:", mds.command_line)
print(mds.get_medusa_last_output)
# print('medusa bruteinfo: ', mds.bruteinfo)
# print('medusa brutestats: ', mds.brutestats)

for host in mds.all_hosts:
    print("Host: %s (%s)" % (host, mds[host]))
```

参数说明

| 字段名             | 类型      | 必须 | 描述                    |
|-----------------|---------|----|-----------------------|
| hosts           | string  | 是  | 主机,可多个（用,号分隔）         |
| ports           | string  | 否  | 端口,可多个（23,80,666-777） |
| user            | string  | 否  | 用户（默认：root）           |
| password        | string  | 否  | 密码（默认：root）           |
| arguments       | string  | 否  | 附加参数（详见附加参数说明）        |
| isfile_hosts    | boolean | 否  | 主机从文件导入,可多个（每行为一个）    |
| isfile_user     | boolean | 否  | 用户从文件导入,可多个（每行为一个）    |
| isfile_password | boolean | 否  | 密码从文件导入,可多个（每行为一个）    |

附加参数说明

```shell
-O [FILE]      指定成功后文件日志信息路径
-e [n/s/ns]    N意为空密码，S意为密码与用户名相同
-M [TEXT]      模块执行名称
-m [TEXT]      传递参数到模块
-d             显示所有的模块名称
-n [NUM]       使用非默认端口
-s             启用SSL
-r [NUM]       重试间隔时间，默认为3秒
-t [NUM]       设定线程数量
-L             并行化，每个用户使用一个线程
-f             在任何主机上找到第一个账号/密码后，停止破解
-q             显示模块的使用信息
-v [NUM]       详细级别（0-6）
-w [NUM]       错误调试级别（0-10）
-V             显示版本
-Z [TEXT]      继续扫描上一次
```

## 依赖

内置依赖

- `re` Type Hints for Python.
- `os` Type Hints for Python.
- `shlex` Type Hints for Python.
- `subprocess` Type Hints for Python.
- `sys` Type Hints for Python.
- `json` Type Hints for Python.

_注：依赖顺序排名不分先后_

## 链接

Github：https://github.com/hanxinkong/python-medusa

在线文档：https://python-medusa.xink.top

## 贡献者

## 许可证

该项目根据 **MIT** 许可条款获得许可.

## 免责声明

1. 若使用者滥用本项目,本人 **无需承担** 任何法律责任.
2. 本程序仅供娱乐,源码全部开源,**禁止滥用** 和二次 **贩卖盈利**.  **禁止用于商业用途**.