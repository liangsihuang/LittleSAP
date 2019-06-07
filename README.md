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
    
## 命名规则
* 类: AxxxBxxx
* 变量和函数: axxx_bxxx，一些常用缩写采用大写，如SOE,DOF,FE
* 原opensees函数: axxxBxxx，不要用这种camelcase，难看

## 原Opensees定义的计算类 Matrix和Vector
* 计算类并不用来存储，只是在计算的时候临时生成
* 所有二阶对称矩阵（刚度，应力，应变）都采用一阶列表存储，节省空间
   * 原opensees生成的矩阵Matrix后，作为类的属性进行保留，而不是每个对象的属性，猜测是为了节省内存
   * python直接使用numpy的一维或二维array存储和计算，矩阵直接作为对象的属性保留
* 求解线性方程组：
   * 原：A.Solve(b,x), A为Matrix
   * 新：x = np.linalg.solve(A,b)
* 矩阵加法：
   * 原：A.addMatrix(factor1, B, factor2)
   * 新: A = A x factor1 + B x factor2
* 矩阵乘法：
   * 原：A.addMatrixProduct(factor1, B, C, factor2)
   * 新: A = A x factor1 + B x C x factor2
   * 注意：numpy直接用'*'号是元素相乘，矩阵乘法用dot
   * 注意：1-d array 可以直接右乘 2-d array, 结果仍是1-d array
   * 但是，如果是2-d array则必须是列向量才行，否则报错。结果也是2-d array
   
   
## 函数迷思?
* 很多类都有getCopy()函数，可以用copy.deepcopy实现
    * 深拷贝是真的复制，浅拷贝只是复制个指针？
    * 材料非线性的实现：每一个积分点赋予一个材料对象，所以传入一个材料要复制好多分。

## 
   
