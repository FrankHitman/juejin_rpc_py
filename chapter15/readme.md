# Chapter 15 Notes

## 分布式 RPC 原理
- 带权重的多个服务器节点，权重越大，被客户端选中的概率就越大
- 容灾Failover： 节点挂掉 - 判断是否网络抖动导致 - 多次尝试确实挂掉 - 失效节点摘除 - 定期健康检查 - 恢复可用再放入有效节点列表
- 降低权重法： 调用出错 - 降低该节点权重 - 指数曲线降低，但不为0 - 调用成功 - 提升该节点权重 - 指数曲线升高权重
  - 客户端一次调用失败会尝试重试。如果降权太慢，会导致重试次数太多，因为第二次随机挑选节点时还是很有可能再次挑选到失效节点。
  - 降权太快也不好，网络抖动会导致节点流量分配的快速抖动，瞬间从正常降到近零，又可以瞬间从近零恢复到正常。
  - 1024=>512=>256=>128=>64=>32=>16=>8=>4=>2=>1 and (1=>2=>4=>8=>16=>32=>64=>128=>256=>512=>1024 or *4 or *8)
- 服务发现，动态变更服务器连接配置，无需重启的扩容与缩容： zookeeper/etcd
  - 服务注册 register service
  - 服务查找 get service
  - 服务变更通知 on service changed




##
