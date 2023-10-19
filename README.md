# openstack-api-proxy
openstack接口代理转发服务

某些场景下无法直接访问openstack-api，可以在客户端和openstack服务直接部署一套接口代理转发服务。

* openstack url和代理转发服务提供的url的映射关系如下：

```
opensatck：https://vimip:port/xx/xx/
openstack-api-proxy：https://proxyip:port/vimid/xx/xx
```

* 其中vimip为每个VIM的API接口IP地址；port为VIM每个服务的端口号，VIM每个服务的端口号与proxy提供的端口号保持一致；proxyip为资源管理代理对VNFM提供可访问的IP地址；vimid为每个VIM统一规划的系统标识；xx/xx是每个服务url其他的信息，在映射过程中保持不变；

{{tablelayout?rowsHeaderSource=Auto&colwidth=",181px,315px"}}
^ 接口名称       ^ URL类型      | 端口号    |
| 认证管理接口     | adminurl   | 35357  |
| :::        | publicurl  | 5000   |
| 镜像管理接口     | adminurl   | 9292   |
| :::        | publicurl  | 9292   |
| 计算资源管理接口   | adminurl   | 8774   |
| :::        | publicurl  | 8774   |
| 网络资源管理接口   | adminurl   | 9696   |
| :::        | publicurl  | 9696   |
| 块存储资源管理接口  | adminurl   | 8776   |
| :::        | publicurl  | 8776   |
| 资源编排接口     | adminurl   | 8004   |
| :::        | publicurl  | 8004   |


## 部署方法

```
docker build -t vimproxy:1.0 . 
echo "启动vim-proxy容器"

docker run -d -ti \
      -m 256m \
      --name vimproxy \
      --net host \
      -e FLASK_APP=/home/vimproxy.py \
      -e PROXY_IP=$ip \
      --restart always vimproxy:1.0
```
