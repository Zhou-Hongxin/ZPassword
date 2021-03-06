from database_tool import userTable
from database_tool import detailTable
import sendMail
import random

'''
消息处理函数，用来处理服务器接收到的消息
消息格式是[信号, 消息内容]
信号    信号含义    消息内容    返回值
 1    客户端请求登录    ['用户名', '密码sha256值']    用户不存在或密码错误或登陆成功及数据库内容
 2    客户端请求增加用户    ['用户名', '密码sha256值']    用户已存在或添加成功或添加失败
 3    客户端请求删除用户    ['用户识别码']    删除成功或删除失败
 4    客户端请求修改密码    ['用户识别码', '修改前密码sha256', '修改后的密码sha256']    原密码错误或修改成功或修改失败
 5    客户端请求增加项目    ['用户识别码', 'url', '网站用户名', '网站密码']    添加成功或添加失败
 6    客户端请求删除项目    ['用户识别码', 'url', '网站用户名']    删除成功或删除失败
 7    客户端请求修改项目    [['用户识别码', 'url', '网站用户名', '网站密码'], ['修改后url', '修改后用户名', '修改后密码']]    修改成功或修改失败或无修改
 8    客户端请求查询信息    ['用户识别码']    用户所有信息列表
 9    查询用户是否存在      ['用户名']    用户存在或不存在
 10   查询用户ID           ['用户名']    用户ID
'''


def message_handle(signal: int, content: list, id_dict: dict):
    # 客户端请求登录
    if signal == 1:
        try:
            db = userTable.select(None, content[0])
        except:
            return return_json('UserNotExists')
        if db is None:
            return return_json('UserNotExists')
        elif len(db) == 0:
            return return_json('UserNotExists')
        else:
            if db[2] == content[1]:
                # 创建用户识别码
                seed = "1234567890abcdefghijkmnpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                sa = []
                for i in range(32):
                    sa.append(random.choice(seed))
                salt = ''.join(sa)
                user_db = [salt, detailTable.select(str(db[0]))]
                # result = ['LoginSuccess', user_db]
                # 此处将登陆成功信息及数据库内容放入list中再返回
                return return_json('LoginSuccess', user_db)
            elif not db[2] == content[1]:
                return return_json('PasswordIncorrect')
        return return_json('UnknowError')

    # 客户端请求增加用户
    elif signal == 2:
        result = userTable.insert(content[0], content[1])
        if result == 'UserExists':
            return return_json(result)
        else:
            if result:
                return return_json('InsertSuccess')
            elif not result:
                return return_json('InsertFail')

    # 客户端请求删除用户
    elif signal == 3:
        if content[0] is "":
            result = userTable.delete(userid=id_dict[content[1]]) and detailTable.delete(str(id_dict[content[1]]))
        else:
            result = userTable.delete(content[0]) and detailTable.delete(str(id_dict[content[1]]))
        if result:
            return return_json('DeleteSuccess')
        elif not result:
            return return_json('DeleteFail')

    # 客户端请求修改密码
    elif signal == 4:
        original_password = userTable.select(str(id_dict[content[0]]), None)
        if original_password[2] == content[1]:
            result = userTable.update(str(id_dict[content[0]]), None, content[2])
            if result == 'NothingToChange':
                return return_json(result)
            else:
                if result:
                    return return_json('UpdateSuccess')
                elif not result:
                    return return_json('UpdateFail')
        else:
            return return_json('OriginalPasswordIncorrect')

    # 客户端请求增加项目
    elif signal == 5:
        result = detailTable.insert(str(id_dict[content[0]]), content[1], content[2], content[3])
        if result:
            return return_json('InsertRecordSuccess')
        elif not result:
            return return_json('InsertRecordFail')

    # 客户端请求删除项目
    elif signal == 6:
        result = detailTable.delete(str(id_dict[content[0]]), content[1], content[2])
        if result == 'NothingToDelete':
            return return_json(result)
        else:
            if result:
                return return_json('DeleteRecordSuccess')
            elif not result:
                return return_json('DeleteRecordFail')

    # 客户端请求修改项目
    elif signal == 7:
        result = detailTable.update(str(id_dict[content[0][0]]), content[0][1], content[0][2], content[0][3], content[1][0],
                                    content[1][1], content[1][2])
        if result == 'RecordNothingToChange':
            return return_json(result)
        else:
            if result:
                return return_json('UpdateRecordSuccess')
            elif not result:
                return return_json('UpdateRecordFail')

    # 客户端请求查询当前用户所有存储信息
    elif signal == 8:
        result = detailTable.select(str(id_dict[content[0]]))
        if result == 'UserHaveNoData':
            return return_json(result)
        else:
            return return_json('QuerySuccess', [content[0], result])

    # 客户端请求查询用户是否存在
    elif signal == 9:
        result = userTable.select(user=content[0])
        if result is None:
            result = sendMail.send_mail(content[0])
            return return_json('SendMailSuccess', [result])
        else:
            return return_json('UserExists')

    elif signal == 10:
        result = userTable.select(user=content[0])
        if result is None:
            return 'UserNotExists'
        else:
            return result[0]


# 用这个函数返回json格式的数据，上方函数返回数据必须调用该函数
# 只有1号分支需要content内容，但是依旧保留该参数，以备需求改变时修改轻松
def return_json(message: str = None, content: list = None):
    if content is None:
        result = {
            'message': message,
            'content': []
        }
    else:
        result = {
            'message': message,
            'content': content
        }
    return result
