# LittleSAP

## 非线性有限元分析步骤
analyze()
* 根据约束对几何形体进行初始编号
    * handler
* 根据初始编号形成图，利用图论进行优化或不优化；同时确定了方程组的大小。
    * numberer
* 确定荷载增量的大小，施加荷载
    * integrator
* 刚度矩阵形成并组装成A，节点不平衡力形成并组装成B
    * integrator
* 解方程得X
    * soe
* 提交，并保存中间数据
    * node, ele, material