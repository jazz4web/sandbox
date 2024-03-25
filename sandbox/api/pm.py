from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from ..auth.attri import permissions
from ..auth.cu import checkcu
from ..common.aparsers import parse_page
from ..common.flashed import set_flashed
from ..common.pg import get_conn
from .pg import (
    check_last, check_outgoing, check_postponed, check_rel,
    edit_pm, receive_incomming, select_m, send_message)

USERNAME = 'SELECT username FROM users WHERE id = $1'
REM = '''UPDATE messages SET received = null, postponed = false,
                             removed_by_sender = false,
                             removed_by_recipient = false,
                             sender_id = null,
                             recipient_id = null WHERE id = $1'''


class Conversations(HTTPEndpoint):
    async def post(self, request):
        res = {'pm': 0}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if permissions.PM in cu['permissions']:
            conn = await get_conn(request.app.config)
            n = await conn.fetchval(
                '''SELECT count(*) FROM messages
                     WHERE recipient_id = $1
                       AND received IS NULL
                       AND postponed = false
                       AND removed_by_sender = false
                       AND removed_by_recipient = false''', cu.get('id'))
            await conn.close()
            res['pm'] = n
        return JSONResponse(res)


class Conversation(HTTPEndpoint):
    async def delete(self, request):
        res = {'done': None}
        d = await request.form()
        last, page = int(d.get('last', '0')), int(d.get('page', '0'))
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.PM not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, received, removed_by_sender, removed_by_recipient,
                      sender_id, recipient_id
                 FROM messages WHERE id = $1''', int(d.get('mid', '0')))
        if target is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if target.get('sender_id') != cu.get('id') and \
                target.get('recipient_id') != cu.get('id'):
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        url = None
        if target.get('sender_id') == cu.get('id'):
            recipient = await conn.fetchval(
                USERNAME, target.get('recipient_id'))
            if target.get('received') is None or \
                    target.get('removed_by_recipient'):
                await conn.execute(REM, target.get('id'))
            else:
                await conn.execute(
                    '''UPDATE messages SET removed_by_sender = true
                         WHERE id = $1''', target.get('id'))
            url = request.url_for('pm:conversation', username=recipient)._url
        if target.get('recipient_id') == cu.get('id'):
            sender = await conn.fetchval(USERNAME, target.get('sender_id'))
            if target.get('removed_by_sender'):
                await conn.execute(REM, target.get('id'))
            else:
                await conn.execute(
                    '''UPDATE messages SET removed_by_recipient = true
                         WHERE id = $1''', target.get('id'))
            url = request.url_for('pm:conversation', username=sender)._url
        res['done'] = True
        if page:
            if last == 1:
                page = page - 1 or 1
            res['redirect'] = f'{url}?page={page}'
        else:
            res['redirect'] = url
        await set_flashed(request, 'Удалено успешно.')
        await conn.close()
        return JSONResponse(res)

    async def get(self, request):
        res = {'cu': await checkcu(
                    request, request.headers.get('x-auth-token'))}
        cu = res['cu']
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.PM not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            'SELECT id, username, permissions FROM users WHERE username = $1',
            request.query_params.get('username', ''))
        if target is None:
            res['message'] = 'Получатель не определён.'
            await conn.close()
            return JSONResponse(res)
        if cu.get('id') == target.get('id'):
            res['message'] = 'Запрос отклонён.'
            await conn.close()
            return JSONResponse(res)
        if permissions.PM not in target.get('permissions'):
            u = target.get('username')
            res['nopm'] = f'{u} не может получать приватные сообщения.'
        rel = await check_rel(conn, cu.get('id'), target.get('id'))
        if rel['blocker'] or rel['blocked']:
            res['blocked'] = 'Приват заблокирован. Вы поссорились?'
        await check_postponed(conn, cu.get('id'), target.get('id'))
        page = await parse_page(request)
        last = await check_last(
            conn, page,
            request.app.config.get('PM_PER_PAGE', cast=int, default=3),
            '''SELECT count(*) FROM
                 (SELECT id FROM messages
                    WHERE sender_id = $1
                      AND recipient_id = $2
                      AND postponed = false
                      AND removed_by_sender = false
                  UNION
                  SELECT id FROM messages
                    WHERE sender_id = $2
                      AND recipient_id = $1
                      AND postponed = false
                      AND removed_by_recipient = false) AS m''',
            cu.get('id'), target.get('id'))
        if page > last:
            res['message'] = f'Всего страниц: {last}.'
            await conn.close()
            return JSONResponse(res)
        if request.query_params.get('nopage') == '0':
            page = last
        if page == last:
            res['incomming'] = await receive_incomming(
                conn, target.get('id'), cu.get('id'))
        res['outgoing'] = await check_outgoing(
            conn, cu.get('id'), target.get('id'))
        res['shform'] = permissions.PM in target.get('permissions') and \
                (not rel['blocker'] and not rel['blocked']) and \
                not res['outgoing']
        res['pagination'] = dict()
        await select_m(
            request, conn, cu.get('id'), target.get('id'), res['pagination'],
            page, request.app.config.get('PM_PER_PAGE', cast=int, default=3),
            last)
        if res['pagination']:
            if res['pagination']['next'] or res['pagination']['prev']:
                res['pv'] = request.app.jinja.get_template(
                    'pictures/pv.html').render(
                    request=request, pagination=res['pagination'])
        await conn.close()
        return JSONResponse(res)

    async def patch(self, request):
        res = {'done': None}
        d = await request.form()
        mid, text = int(d.get('mid', '0')), d.get('text', '')
        if not text:
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse(res)
        if len(text) > 25000:
            res['message'] = 'Превышен лимит в 25000 знаков.'
            return JSONResponse(res)
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.PM not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, body, received, sender_id
                 FROM messages WHERE id = $1 AND sender_id = $2''',
            mid, cu.get('id'))
        if target is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse(res)
        if target.get('body') != text and target.get('received') is None:
            await edit_pm(conn, target.get('id'), text)
            await set_flashed(request, 'Сообщение отредактировано.')
        res['done'] = True
        await conn.close()
        return JSONResponse(res)

    async def post(self, request):
        res = {'done': None}
        d = await request.form()
        recipient, text = d.get('recipient'), d.get('message')
        if not all((recipient, text)):
            res['message'] = 'Запрос содержит неверные параметры.'
            return JSONResponse()
        if len(text) > 25000:
            res['message'] = 'Превышен лимит в 25000 знаков.'
            return JSONResponse(res)
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.PM not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        if cu.get('username') == recipient:
            res['message'] = 'Запрос отклонён.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        recipient = await conn.fetchrow(
            'SELECT id, username, permissions FROM users WHERE username = $1',
            recipient)
        if recipient is None:
            res['message'] = 'Получатель не определён.'
            await conn.close()
            return JSONResponse(res)
        if permissions.PM not in recipient['permissions']:
            u = recipient.get('username')
            res['message'] = f'{u} не может получать приватые сообщения.'
            await conn.close()
            return JSONResponse(res)
        rel = await check_rel(conn, cu.get('id'), recipient.get('id'))
        if rel['blocker'] or rel['blocked']:
            res['message'] = 'Приват заблокирован, вы поссорились.'
            await conn.close()
            return JSONResponse(res)
        await send_message(conn, cu.get('id'), recipient.get('id'), text)
        await set_flashed(request, 'Сообщение отправлено.')
        res['done'] = True
        await conn.close()
        return JSONResponse(res)

    async def put(self, request):
        res = {'done': None}
        d = await request.form()
        cu = await checkcu(request, d.get('auth'))
        if cu is None:
            res['message'] = 'Доступ ограничен, требуется авторизация.'
            return JSONResponse(res)
        if permissions.PM not in cu['permissions']:
            res['message'] = 'Доступ ограничен, у вас недостаточно прав.'
            return JSONResponse(res)
        conn = await get_conn(request.app.config)
        target = await conn.fetchrow(
            '''SELECT id, body, received, sender_id FROM messages
                 WHERE id = $1 AND sender_id = $2''',
            int(d.get('mid', '0')), cu.get('id'))
        if target is None:
            res['message'] = 'Запрос содержит неверные параметры.'
            await conn.close()
            return JSONResponse()
        if target.get('received'):
            res['done'] = True
            res['update'] = True
            await conn.close()
            await set_flashed(request, 'Сообщение уже получено.')
            return JSONResponse(res)
        await conn.execute(
            'UPDATE messages SET postponed = true WHERE id = $1',
            target.get('id'))
        res['done'] = True
        res['text'] = target.get('body')
        res['id'] = target.get('id')
        await conn.close()
        return JSONResponse(res)
