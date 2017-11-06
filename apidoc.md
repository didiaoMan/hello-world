用户信息
=======

---

简要描述：
--------

获取所有服务器中的用户信息，数据表中的所有字段信息都需要返回

请求URL：
--------

`/api/users`

请求方式：
--------

POST

返回数据示例
-----------

-成功

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
            "level": "直升机",
            "pos": "机械师"
        },
        {
            "userid": 1,
            "username": "java",
            "password": "hello",
            "sex": "男",
            "birthday": "1990-04-25",
            "birthplace": "北京",
            "level": "直升机",
            "pos": "机械师"
        }
    ]
}
```

-失败

```
{
    "result_code": 1
}
```

-空数据

```
{
    "result_code": 0,
    "data": []
}
```


用户头像
=======

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
