自动删种程序
======================
|PyPI| |GithubActionsCI| |ReadTheDocs| |Coverage| |Codacy| |Downloads| |MIT|

这个程序可以帮助你删除种子。现在你再也不用担心你的磁盘空间了——通过你设置的策略，程序会帮你检查每一个种子是否满足删除的条件；如果是，那就自动地删除它。

这个程序支持 qBittorrent、Transmission、μTorrent 或 Deluge。 如果你喜欢，可以点个星星 :star2: :)

文档：https://autoremove-torrents.readthedocs.io/zh_CN/latest/

.. |GithubActionsCI| image:: https://github.com/jerrymakesjelly/autoremove-torrents/actions/workflows/build.yml/badge.svg?branch=master
   :target: https://github.com/jerrymakesjelly/autoremove-torrents/actions
.. |ReadTheDocs| image:: https://readthedocs.org/projects/autoremove-torrents-cn/badge/?version=latest
   :target: https://autoremove-torrents.readthedocs.io/zh_CN/latest/?badge=latest
.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/ab6f14fa9d9845b8bc8edecaf8f705e4
   :target: https://www.codacy.com/gh/jerrymakesjelly/autoremove-torrents/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jerrymakesjelly/autoremove-torrents&amp;utm_campaign=Badge_Grade
.. |Coverage| image:: https://app.codacy.com/project/badge/Coverage/ab6f14fa9d9845b8bc8edecaf8f705e4
    :target: https://www.codacy.com/gh/jerrymakesjelly/autoremove-torrents/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jerrymakesjelly/autoremove-torrents&amp;utm_campaign=Badge_Coverage
.. |MIT| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/jerrymakesjelly/autoremove-torrents/blob/master/LICENSE
.. |PyPI| image:: https://badge.fury.io/py/autoremove-torrents.svg
    :target: https://badge.fury.io/py/autoremove-torrents
.. |Downloads| image:: https://img.shields.io/pypi/dm/autoremove-torrents.svg
    :target: https://pypi.org/project/autoremove-torrents/

环境要求
-------------

* Python 3

需要 Python 3.6 或更高版本。（自 1.6.1 起不再支持 Python 2。）


快速开始
-------------
安装
+++++++++++++++++++
从 pip 安装
^^^^^^^^^^^^^^^^^
::

    pip install autoremove-torrents

或者

从 GitHub 安装
^^^^^^^^^^^^^^^^^^^^
::

    git clone https://github.com/jerrymakesjelly/autoremove-torrents.git
    cd autoremove-torrents
    python3 setup.py install

或者

从 Docker 安装
^^^^^^^^^^^^^^
GHCR 上提供了构建好的镜像::

    docker pull ghcr.io/sysit/autoremove-torrents:1.6.1

挂载配置文件运行（加上 ``--view`` 参数可以先预览而不真正删除）::

    docker run --rm \
      -v $PWD/config.yml:/etc/autoremove/config.yml:ro \
      ghcr.io/sysit/autoremove-torrents:1.6.1 \
      --conf /etc/autoremove/config.yml


编写配置文件
++++++++++++++++++++++++++++++
为了让程序能按照你的想法去工作，你需要学习如何编写配置文件。

你可以把配置文件放在磁盘的任何地方。不过，在默认情况下，autoremove-torrents 只在 Shell 的当前工作目录去找 ``config.yml``::

    vim ./config.yml


语法也比较简单，下面是一个例子::

    my_task:
      client: qbittorrent
      host: http://127.0.0.1
      username: admin
      password: adminadmin
      strategies:
        my_strategy:
          categories: IPT
          remove: seeding_time > 1209600 or ratio > 1
      delete_data: true


在这个例子中，程序会自动删除那些标签是 IPT，做种时间超过 1209600 秒 **或者** 分享率大于 1 的种子。请查看 `文档`_ 以获得更多信息。

.. _文档: https://autoremove-torrents.readthedocs.io/zh_CN/latest/

运行
++++
::

    autoremove-torrents

如果你只是想看看哪些种子会被删除但并不想真的就删除它们，请使用 ``--view`` 命令行参数（``autoremove-torrents --view``）。


设置计划任务
-----------------------------
如果你想每 15 分钟检查一次哪些种子可以被删除，Linux 的 ``crontab`` 程序可以帮你。首先::

    crontab -e

然后，在文件的最后加一行（请先确认 ``autoremove-torrents`` 在你系统中的路径）::

*/15 * * * * /usr/bin/autoremove-torrents --conf=/home/jerrymakesjelly/autoremove-torrents/config.yml --log=/home/jerrymakesjelly/autoremove-torrents/logs

``--conf`` 参数指示了配置文件的路径。
``--log`` 参数指定了存储日志文件的路径（必须存在）。

任务失败时程序会以非零退出码结束，方便 cron 等调度器监测失败的运行。Kubernetes 的 CronJob 示例见`安装文档`_。

.. _安装文档: https://autoremove-torrents.readthedocs.io/zh_CN/latest/inst.html

截图
-----------
|Screenshot|

.. |Screenshot| image:: https://user-images.githubusercontent.com/6760674/174464634-15743d59-f1dc-41c9-bff6-6d90becaeb67.gif

更新日志
----------
**2026.11.8 星期六**：版本 1.6.1。

* ``remote_free_space`` 条件在客户端报告未知剩余空间时（如路径不存在）中止策略，而不是误删全部种子。
* ``remove:`` 表达式运算符优先级修正：``and`` 优先于 ``or``，与文档一致。
* 任务失败时以非零退出码结束；``--task`` 指定不存在的任务时会列出可用任务。
* 修复 uTorrent 总下载速度统计、无 category 字段的客户端崩溃、未知 Deluge 状态崩溃等问题。
* 仅支持 Python 3（移除 Python 2 兼容层）；提供 Docker 镜像 ``ghcr.io/sysit/autoremove-torrents``。
* 新增 ``content_paths`` 下载目录过滤器（1.6.0）。

`更多更新日志`_

.. _更多更新日志: https://autoremove-torrents.readthedocs.io/zh_CN/latest/changelog.html

计划列表
-----------
看你们的反馈。如果你有任何问题，欢迎提交 `issues`_。

.. _issues: https://github.com/jerrymakesjelly/autoremove-torrents/issues

`点击这里`_ 查看TODO列表。

.. _点击这里: https://github.com/jerrymakesjelly/autoremove-torrents/issues/63
