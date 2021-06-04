# LSSY量化交易系统

支持市场：A股和可转债

该项目是本人3年来研究量化慢慢积累开发的一套系统，属于早期作品慢慢修改而来，仅供学习研究。

如需要更专业的量化交易系统，请使用蝴蝶量化：https://hdlh.org

# 环境安装

  * Python 3.7.x or 3.8.x or 3.9.x

  * Redis
  
    Windows
    
    https://github.com/microsoftarchive/redis/releases

    Linux

    ```
    sudo apt install redis
    ```

# 执行安装脚本

  * Windows

  ```
  install.bat
  ```

  * Linux

  ```
  ./install.sh
  ```

# 启动LSSY量化交易系统

  * Windows

    进入实盘交易

    ```
    win_realtime.bat
    ```

    进入回测

    ```
    win_backtest.bat
    ```

  * Linux

    进入实盘交易

    ```
    ./runWork.py
    ```

    进入回测

    ```
    ./runWork.py b
    ```

# 访问前端

推荐分辨率>=2k

```
http://127.0.0.1:8000/
```

# 初次启动注意事项

首次部署LSSY量化交易系统，会下载大量财务历史等数据，根据网络情况可能会很慢，建议晚上睡觉前启动系统，一般到第二天就全部下载完成了，仅首次运行，后续每天只需要更新k线即可，速度会快很多。

微信: qiji_hello

QQ交流群：174647513
