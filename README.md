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
* 变量和函数: axxx_bxxx
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

## 废弃的函数
* 很多类都有getCopy()函数，不知道意义在哪。是怕被改变？
    * 新：直接使用=号，试试看
   
