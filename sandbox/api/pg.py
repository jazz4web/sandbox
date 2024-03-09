import asyncio
import functools
import math

from datetime import datetime, timedelta
from validate_email import validate_email

from ..auth.attri import get_group, permissions
from ..common.aparsers import (
    iter_pages, parse_pic_filename, parse_title, parse_units)
from ..common.random import get_unique_s
from ..drafts.attri import status
from .parse import parse_art_query, parse_arts_query
from .slugs import check_max, make, parse_match


async def check_draft(request, conn, slug, cuid, target):
    query = await conn.fetchrow(
        '''SELECT articles.id, articles.title, articles.slug,
                  articles.suffix, articles.html, articles.summary,
                  articles.meta, articles.published, articles.edited,
                  articles.state, articles.commented, articles.viewed,
                  articles.author_id, users.username
             FROM articles, users
             WHERE articles.slug = $1
               AND articles.author_id = $2
               AND users.id = articles.author_id''',
        slug, cuid)
    if query:
        await parse_art_query(request, conn, query, target)


async def check_slug(conn, title):
    loop = asyncio.get_running_loop()
    slug = await loop.run_in_executor(
        None, functools.partial(make, title))
    match = await conn.fetch(
        'SELECT slug FROM articles WHERE slug LIKE $1', f'{slug}%')
    match = await loop.run_in_executor(
        None, functools.partial(parse_match, match))
    if not match or slug not in match:
        return slug
    maxi = await loop.run_in_executor(
        None, functools.partial(check_max, match, slug))
    return f'{slug}-{maxi+1}'


async def create_d(conn, title, uid):
    suffix = await get_unique_s(conn, 'articles', 8)
    slug = await check_slug(conn, title)
    now = datetime.utcnow()
    empty = await conn.fetchval(
        'SELECT id FROM articles WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE articles
                 SET title = $1, slug = $2, suffix = $3,
                     edited = $4, state = $5, author_id = $6
                 WHERE id = $7''',
            title, slug, suffix, now, status.draft, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO articles
               (title, slug, suffix, edited, state, author_id)
               VALUES ($1, $2, $3, $4, $5, $6)''',
            title, slug, suffix, now, status.draft, uid)
    return slug


async def select_drafts(request, conn, uid, target, page, per_page, last):
    query = await conn.fetch(
        '''SELECT a.id, a.title, a.slug, a.suffix, a.summary, a.published,
                  a.edited, a.state, a.commented, a.viewed, users.username
             FROM articles AS a, users
             WHERE a.author_id = users.id
               AND a.author_id = $1
               AND a.state IN ($2, $3)
             ORDER BY a.edited DESC LIMIT $4 OFFSET $5''',
        uid, status.draft, status.cens, per_page, per_page*(page-1))
    if query:
        await parse_arts_query(request, conn, query, target, page, last)


async def get_pic_stat(request, conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT pictures.uploaded, pictures.filename, pictures.width,
                  pictures.height, pictures.format, pictures.volume,
                  pictures.suffix, albums.author_id FROM pictures, albums
             WHERE pictures.album_id = albums.id
               AND albums.author_id = $1 AND pictures.suffix = $2''',
        uid, suffix)
    if query:
        return {'uploaded': f'{query.get("uploaded").isoformat()}Z',
                'filename': query.get('filename'),
                'width': query.get('width'),
                'height': query.get('height'),
                'format': query.get('format'),
                'volume': await parse_units(query.get('volume')),
                'suffix': query.get('suffix'),
                'url': request.url_for(
                    'picture', suffix=query.get('suffix'))._url,
                'path': request.app.url_path_for(
                    'picture', suffix=query.get('suffix')),
                'parsed15': await parse_pic_filename(
                    query.get('filename'), 15),
                'parsed25': await parse_pic_filename(
                    query.get('filename'), 20)}


async def select_pictures(conn, aid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT filename, suffix FROM pictures
             WHERE album_id = $1
             ORDER BY uploaded DESC LIMIT $2 OFFSET $3''',
        aid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'pictures': [{'filename': record.get('filename'),
                              'parsed40': await parse_pic_filename(
                                  record.get('filename'), 30),
                              'suffix': record.get('suffix')}
                             for record in query]}


async def get_album(conn, uid, suffix):
    query = await conn.fetchrow(
        '''SELECT id, title, created, suffix, state, volume FROM albums
             WHERE suffix = $1 AND author_id = $2''',
        suffix, uid)
    if query:
        num = await conn.fetchval(
            'SELECT count(*) FROM pictures WHERE album_id = $1',
            query.get('id'))
        return {'id': query.get('id'),
                'title': query.get('title'),
                'created': f'{query.get("created").isoformat()}Z',
                'suffix': query.get('suffix'),
                'state': query.get('state'),
                'volume_': query.get('volume'),
                'volume': await parse_units(query.get('volume')),
                'files': num,
                'parse_t': len(query.get('title')) > 50,
                'parsed22': await parse_title(query.get('title'), 22),
                'parsed36': await parse_title(query.get('title'), 36),
                'parsed50': await parse_title(query.get('title'), 50)}
    return None


async def create_new_album(conn, uid, title, state):
    now = datetime.utcnow()
    suffix = await get_unique_s(conn, 'albums', 8)
    empty = await conn.fetchval(
        'SELECT id FROM albums WHERE author_id IS NULL')
    if empty:
        await conn.execute(
            '''UPDATE albums SET title = $1,
                                 created = $2,
                                 changed = $2,
                                 suffix = $3,
                                 state = $4,
                                 volume = 0,
                                 author_id = $5 WHERE id = $6''',
            title, now, suffix, state, uid, empty)
    else:
        await conn.execute(
            '''INSERT INTO
                 albums (title, created, changed, suffix, state, author_id)
                 VALUES ($1, $2, $2, $3, $4, $5)''',
            title, now, suffix, state, uid)
    return suffix


async def get_user_stat(conn, uid):
    return {'albums': await conn.fetchval(
        'SELECT count(*) FROM albums WHERE author_id = $1', uid),
            'files': await conn.fetchval(
        '''SELECT count(*) FROM albums, pictures
             WHERE author_id = $1
             AND pictures.album_id = albums.id''', uid),
            'volume': await parse_units(await conn.fetchval(
        'SELECT sum(volume) FROM albums WHERE author_id = $1', uid) or 0)}


async def select_albums(conn, uid, page, per_page, last):
    query = await conn.fetch(
        '''SELECT title, suffix FROM albums
             WHERE author_id = $1
             ORDER BY changed DESC LIMIT $2 OFFSET $3''',
        uid, per_page, per_page*(page-1))
    if query:
        return {'page': page,
                'next': page + 1 if page + 1 <= last else None,
                'prev': page - 1 or None,
                'pages': await iter_pages(page, last),
                'albums': [{'title': record.get('title'),
                            'parsed': await parse_title(
                                record.get('title'), 40),
                            'suffix': record.get('suffix')}
                           for record in query]}
    return None


async def check_last(conn, page, per_page, *args):
    num = await conn.fetchval(*args)
    return math.ceil(num / per_page) or 1


async def check_account(config, conn, account, address):
    length = timedelta(
        seconds=round(3600*config.get('TOKEN_LENGTH', cast=float)))
    interval = timedelta(
        seconds=round(3600*config.get('REQUEST_INTERVAL', cast=float)))
    if datetime.utcnow() - account.get('requested') < interval:
        return 'Сервис временно недоступен, попробуйте зайти позже.'
    if account.get('address') == address:
        return 'Задан Ваш текущий адрес, запрос не имеет смысла.'
    if await check_swap(conn, address, length):
        return 'Адрес в свопе, выберите другой или повторите попытку позже.'
    requested = await conn.fetchrow(
        'SELECT requested, user_id FROM accounts WHERE address = $1', address)
    if requested and requested.get('user_id'):
        return 'Этот адрес уже зарегистрирован, запрос отклонён.'
    if requested and datetime.utcnow() - requested.get('requested') < length:
        return 'Адрес регистрируется, выберите другой или попробуйте позже.'
    return None


async def check_rel(conn, uid1, uid2):
    friend = bool(await conn.fetchrow(
        '''SELECT author_id, friend_id FROM friends
             WHERE author_id = $1 AND friend_id = $2''', uid1, uid2))
    follower = bool(await conn.fetchrow(
        '''SELECT author_id, follower_id FROM followers
             WHERE author_id = $1 AND follower_id = $2''', uid1, uid2))
    blocker = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid2, uid1))
    blocked = bool(await conn.fetchrow(
        '''SELECT target_id, blocker_id FROM blockers
             WHERE target_id = $1 AND blocker_id = $2''', uid1, uid2))
    return {'friend': friend, 'follower': follower,
            'blocker': blocker, 'blocked': blocked}


async def filter_target_user(request, conn, username):
    query = await conn.fetchrow(
        '''SELECT id, username, registered, last_visit, permissions,
                  description, last_published FROM users
             WHERE username = $1''', username)
    if query:
        return {'uid': query.get('id'),
                'username': query.get('username'),
                'group': await get_group(query.get('permissions')),
                'registered': f'{query.get("registered").isoformat()}Z',
                'last_visit': f'{query.get("last_visit").isoformat()}Z',
                'permissions': query.get('permissions'),
                'description': query.get('description'),
                'last_published': f'{query.get("last_published").isoformat()}Z'
                if query.get('last_published') else None,
                'ava': request.url_for(
                    'ava', username=query.get('username'), size=160)._url}


async def get_acc(conn, account, address):
    now = datetime.utcnow()
    if account:
        address = account.get('address')
        await conn.execute(
            '''UPDATE accounts SET swap = null, requested = $1
                 WHERE address = $2''', now, address)
    else:
        await conn.execute(
            '''INSERT INTO accounts (address, requested)
                 VALUES ($1, $2)''', address, now)
    return await conn.fetchrow(
        'SELECT id, address, user_id FROM accounts WHERE address = $1',
        address)


async def define_acc(conn, account):
    if account and account.get('user_id'):
        username = await conn.fetchval(
            'SELECT username FROM users WHERE id = $1', account.get('user_id'))
        return username, 'Сброс забытого пароля', 'emails/resetpwd.html'
    return 'Гость', 'Регистрация', 'emails/invitation.html'


async def check_swap(conn, address, length):
    swapped = await conn.fetchrow(
        'SELECT id, swap, requested FROM accounts WHERE swap = $1', address)
    if swapped:
        if datetime.utcnow() - swapped.get('requested') > length:
            await conn.execute(
                'UPDATE accounts SET swap = null WHERE id = $1',
                swapped.get('id'))
            return None
        else:
            return True


async def check_address(request, conn, address):
    message = None
    interval = timedelta(
        seconds=round(
            3600*request.app.config.get('REQUEST_INTERVAL', cast=float)))
    length = timedelta(
        seconds=round(
            3600*request.app.config.get('TOKEN_LENGTH', cast=float)))
    acc = await conn.fetchrow(
        'SELECT address, requested, user_id FROM accounts WHERE address = $1',
        address)
    if acc and datetime.utcnow() - acc.get('requested') < interval:
        message = 'Сервис временно недоступен, попробуйте зайти позже.'
    if await check_swap(conn, address, length):
        message = 'Адрес в свопе, выберите другой или повторите попытку позже.'
    return message, acc


async def filter_user(conn, login):
    squery = '''SELECT users.id, users.username,
                       users.password_hash, users.permissions,
                       users.last_published, users.registered
                  FROM users, accounts
                    WHERE users.id = accounts.user_id '''
    if validate_email(login):
        squery += ' AND accounts.address = $1'
    else:
        squery += ' AND users.username = $1'
    query = await conn.fetchrow(squery, login)
    if query and permissions.NOLOGIN not in query.get('permissions'):
        return {'id': query.get('id'),
                'username': query.get('username'),
                'password_hash': query.get('password_hash'),
                'registered': query.get('registered'),
                'last_published': query.get('last_published'),
                'permissions': query.get('permissions')}
