# LSSY量化交易系统

开源的目的是希望能有更多的人来参与社区维护，共同打造最完美的量化交易系统。

支持A股和可转债市场。

目前市场上集量化回测、实盘交易的系统并不多，要么收费高昂，LSSY量化交易系统为了让研究量化交易的朋友人人都能用，所以在此开源，并且完全免费，希望更多的人来参与完善系统，贡献自己的一份力量。

LSSY量化交易系统致力于量化交易，不再主观交易，只做确定性，让量化交易不再是机构专属，大家都可以参与完善，**为了更好的利于社区发展，目前采用邀请制，使用邀请码才能完整的使用LSSY量化交易系统**，提交代码或者邀请朋友都可以免费获得邀请码（在社区讨论QQ群发放）。我们是希望大家互相告知让更多的宽客去实现自己的策略梦想，并不是为了收费，现在不会，将来也不会。

# 安装

需要在 python3.8 下运行

Linux 可以下载源码编译：https://www.python.org/ftp/python/3.8.7/Python-3.8.7.tgz

Windows用户需要安装linux子系统，选择ubuntu子系统里面默认的就是python3.8。

安装redis数据库
```
apt install redis
```
python 包
```
pip3 install tornado
pip3 install redis
pip3 install pytdx
pip3 install baostock
pip3 install pycryptodome
pip3 install akshare
```

# 启动LSSY量化交易系统
进入实盘交易
```
./runWork.py
```
进入回测
```
./runWork.py b
```

# 访问前端
```
http://127.0.0.1:8000/
```

# 初次启动注意事项
首次部署LSSY量化交易系统，会下载大量财务历史等数据，根据网络情况可能会很慢，建议晚上睡觉前启动系统，一般到第二天就全部下载完成了，仅首次运行，后续每天只需要更新k线即可，速度会快很多。


社区讨论QQ群：174647513
