ng-mini
=======

一个利用rrdtool，yaml的集绘图，采集汇报的程序.单独驻守在服务器上，简单配置下yaml文件，就可以轻松的采集数据并汇报给你想要汇报
的地方

我们公司（CC）的NG很牛逼，信息采集画图很不错，不过是内部的东西，而且很大一部分是C写的，也看不到源码，所以大致根据效果，利用十一在家的时间写了这么一个程序ng-mini(因为最近想给媳妇买个ipad-mini,所以就想到了名字里面加个mini)。

###一、实现功能


 信息采集，例如你想采集带宽信息，内存，磁盘，CC，只要你能写出这样的程序或者命令，放到yaml文件的CmdLine后面，那么信息的采集就交给ng-mini 吧，而且你不用再使用crontab 了（当然也可以结合者来）
画图，自定义颜色，画图方式，是否要合并
信息汇报，类似saltstack的retuner,发送给服务端（数据库，NoSQL）,供你进行进一步的处理（告警，数据分析等）（PS:待完善）
自带web展示，基于微型web框架（你要弄个django怎么对得器mini这个字呢，哈哈）bottle.py,就一个文件。前端基于yahoo的pure 框架就一个CSS文件，一切都是要对得起mini这个字啊

###二、程序依赖


####1、python版本

 因为这里面的bottle.py 是依赖python2.5或者以上，所以我们原则上也是这样

####2、python额外的库文件

 PyYAML
####3、rrdtool （命令行下）

其它的暂时不依赖了

###三、程序安装

 centos 5.x 6.x

 wget -O – http://www.chenqing.org/soft/install-centos.sh |bash

 ubuntu 13.4 (我这测试了这个版本)

 sudo wget -O – http://www.chenqing.org/soft/install-ubuntu.sh |bash

 下一步打算提交到epel源以及ubuntu的仓库中

###四、程序启动

 service ng-client start

###五、查看web界面

 http://yourip:65533

 github:https://github.com/chenqing/ng-mini

###六、demo地址：

 http://www.chenqing.org:65533/mini



