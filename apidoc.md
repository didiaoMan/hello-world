用户信息
=======


简要描述：
--------

获取所有服务器中的用户信息，数据表中的所有字段信息都需要返回

请求URL：
--------

`/api/users`

请求方式：
--------

GET

返回数据中字段名与数据表中字段对应关系
-----------------------------------

数据字段 | 数据表中字段
--------|------------
userid  | no
username | name
password | password
sex      | sex
birthday | year month date
birthplace| natives
level    | flly_machine

**注： 返回字段中`birthday`与数据表中的`year month date` 三个字段相关，需要将格式处理为`yyyy-MM-dd`比如`2014-03-01`**

返回数据示例
-----------

- 成功

```
{
    "result_code": 0,
    "data": [
        {
            "userid": 1,
            "username": "java",
            "password": "hello",
            "sex": "男",
            "birthday": "1990-04-25",
            "birthplace": "北京",
            "level": "直升机"
        },
        {
            "userid": 1,
            "username": "java",
            "password": "hello",
            "sex": "男",
            "birthday": "1990-04-25",
            "birthplace": "北京",
            "level": "直升机"
        }
    ]
}
```

- 失败

```
{
    "result_code": 1
}
```

- 空数据

```
{
    "result_code": 0,
    "data": []
}
```
**说明：返回每个数据不为空，若有字段没有值，字符串返回空字符串""，数字返回默认值，`result_code`的值统一定义**

用户头像
=======

参数：
-----

**参数列表**

参数名    | 参数类型      | 必选        | 说明    
---------|---------------|------------|----------
username |    string     |     是     |    用户名

指纹
===

血压、体温等数据回传
==================

航医提示
=======

登录
===

网络状态
=======

个人信息
=======
